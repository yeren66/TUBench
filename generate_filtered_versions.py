"""
测试演化数据集后处理工具 - 生成过滤版本
用于从初步筛选的数据集中生成隐藏测试变更的版本
"""

import sys
import json
import os
from config import Config
from utils.logger import setup_logger, get_logger
from modules import GitAnalyzer, FilteredVersionGenerator

setup_logger()
logger = get_logger()


def load_qualified_commits(dataset_file):
    """
    加载合格的commits
    
    Args:
        dataset_file: 数据集文件路径
        
    Returns:
        list: 合格的commit信息列表
    """
    try:
        with open(dataset_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            commits = data.get('commits', [])
            # 只选择qualified=True的commits
            qualified = [c for c in commits if c.get('qualified', False)]
            logger.info(f"加载了 {len(qualified)} 个合格的commits（总计 {len(commits)} 个）")
            return qualified
    except Exception as e:
        logger.error(f"加载数据集失败: {e}")
        return []


def generate_filtered_versions(repo_path, dataset_file, output_file):
    """
    为所有合格的commits生成过滤版本
    
    Args:
        repo_path: Git仓库路径
        dataset_file: 输入数据集文件
        output_file: 输出数据集文件
    """
    logger.info("=" * 80)
    logger.info("测试演化数据集 - 生成过滤版本")
    logger.info("=" * 80)
    
    # 加载合格的commits
    qualified_commits = load_qualified_commits(dataset_file)
    if not qualified_commits:
        logger.error("没有找到合格的commits")
        return
    
    # 初始化工具
    git_analyzer = GitAnalyzer(repo_path)
    version_generator = FilteredVersionGenerator(git_analyzer)
    
    # 统计信息
    stats = {
        'total': len(qualified_commits),
        'source_only': {
            'success': 0,
            'failed_apply': 0,
            'failed_compile': 0,
            'failed_other': 0
        },
        'test_only': {
            'success': 0,
            'failed_apply': 0,
            'failed_compile': 0,
            'failed_other': 0
        }
    }
    
    # 处理结果
    results = []
    
    try:
        for i, commit_info in enumerate(qualified_commits):
            commit_hash = commit_info['commit_hash']
            logger.info(f"\n处理 [{i+1}/{len(qualified_commits)}]: {commit_hash[:8]}")
            
            # 生成过滤版本（仅源代码变更）
            source_result = version_generator.generate_filtered_version(commit_info)
            # 生成测试版本（仅测试代码变更）
            test_result = version_generator.generate_test_only_version(commit_info)
            
            # 构建输出数据
            output_data = {
                'original_commit': commit_hash,
                'parent_commit': commit_info['parent_hash'],
                'author': commit_info['author'],
                'date': commit_info['date'],
                'message': commit_info['message'],
                'changed_files': commit_info['changed_files'],
                'changed_methods': commit_info['changed_methods'],
                'coverage_analysis': commit_info.get('coverage_analysis', {}),
                'filtered_version': {
                    'success': source_result['success'],
                    'filtered_commit_hash': source_result.get('filtered_commit_hash'),
                    'branch_name': source_result.get('branch_name'),
                    'test_changes_hidden': source_result.get('test_changes_hidden', {}),
                    'filter_stats': source_result.get('stats', {}),
                    'error': source_result.get('error')
                },
                'test_only_version': {
                    'success': test_result['success'],
                    'test_only_commit_hash': test_result.get('test_only_commit_hash'),
                    'branch_name': test_result.get('branch_name'),
                    'source_changes_hidden': test_result.get('source_changes_hidden', {}),
                    'filter_stats': test_result.get('stats', {}),
                    'error': test_result.get('error')
                }
            }
            
            # 更新统计 - 源代码版本
            if source_result['success']:
                stats['source_only']['success'] += 1
                logger.info(
                    f"  ✓ 源代码版本成功: {source_result['filtered_commit_hash'][:8]} "
                    f"(分支: {source_result['branch_name']})"
                )
            else:
                error_msg = source_result.get('error', 'Unknown error')
                if 'apply' in error_msg.lower() or 'patch' in error_msg.lower():
                    stats['source_only']['failed_apply'] += 1
                elif 'compile' in error_msg.lower() or '编译' in error_msg:
                    stats['source_only']['failed_compile'] += 1
                else:
                    stats['source_only']['failed_other'] += 1
                logger.warning(f"  ✗ 源代码版本失败: {error_msg}")
            
            # 更新统计 - 测试版本
            if test_result['success']:
                stats['test_only']['success'] += 1
                logger.info(
                    f"  ✓ 测试版本成功: {test_result['test_only_commit_hash'][:8]} "
                    f"(分支: {test_result['branch_name']})"
                )
            else:
                error_msg = test_result.get('error', 'Unknown error')
                if 'apply' in error_msg.lower() or 'patch' in error_msg.lower():
                    stats['test_only']['failed_apply'] += 1
                elif 'compile' in error_msg.lower() or '编译' in error_msg:
                    stats['test_only']['failed_compile'] += 1
                else:
                    stats['test_only']['failed_other'] += 1
                logger.warning(f"  ✗ 测试版本失败: {error_msg}")
            
            results.append(output_data)
        
        # 保存结果
        def _success_rate(success, total):
            return f"{(success / total * 100):.2f}%" if total else "0.00%"
        
        output_data = {
            'metadata': {
                'source_dataset': dataset_file,
                'total_processed': stats['total'],
                'source_only': {
                    'successful': stats['source_only']['success'],
                    'failed': {
                        'apply_patch': stats['source_only']['failed_apply'],
                        'compilation': stats['source_only']['failed_compile'],
                        'other': stats['source_only']['failed_other']
                    },
                    'success_rate': _success_rate(stats['source_only']['success'], stats['total'])
                },
                'test_only': {
                    'successful': stats['test_only']['success'],
                    'failed': {
                        'apply_patch': stats['test_only']['failed_apply'],
                        'compilation': stats['test_only']['failed_compile'],
                        'other': stats['test_only']['failed_other']
                    },
                    'success_rate': _success_rate(stats['test_only']['success'], stats['total'])
                }
            },
            'commits': results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info("\n" + "=" * 80)
        logger.info("处理完成！")
        logger.info(f"总计: {stats['total']}")
        logger.info(
            f"源代码版本成功: {stats['source_only']['success']} "
            f"({_success_rate(stats['source_only']['success'], stats['total'])})"
        )
        logger.info(
            f"测试版本成功: {stats['test_only']['success']} "
            f"({_success_rate(stats['test_only']['success'], stats['total'])})"
        )
        logger.info("源代码版本失败:")
        logger.info(f"  - Patch应用失败: {stats['source_only']['failed_apply']}")
        logger.info(f"  - 编译失败: {stats['source_only']['failed_compile']}")
        logger.info(f"  - 其他错误: {stats['source_only']['failed_other']}")
        logger.info("测试版本失败:")
        logger.info(f"  - Patch应用失败: {stats['test_only']['failed_apply']}")
        logger.info(f"  - 编译失败: {stats['test_only']['failed_compile']}")
        logger.info(f"  - 其他错误: {stats['test_only']['failed_other']}")
        logger.info(f"\n结果已保存到: {output_file}")
        logger.info("=" * 80)
        
    finally:
        # 恢复原始状态
        version_generator.restore_original_branch()


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python generate_filtered_versions.py <dataset.json> [output.json]")
        print("\n参数:")
        print("  dataset.json - 初步筛选后的数据集文件路径")
        print("  output.json  - 输出文件路径（可选，默认为filtered_dataset.json）")
        print("\n示例:")
        print("  python generate_filtered_versions.py output/dataset.json output/filtered_dataset.json")
        sys.exit(1)
    
    dataset_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output/filtered_dataset.json"
    
    # 验证输入文件
    if not os.path.exists(dataset_file):
        logger.error(f"数据集文件不存在: {dataset_file}")
        sys.exit(1)
    
    # 使用配置中的仓库路径
    if not Config.REPO_PATH:
        logger.error("请在config.py中设置REPO_PATH")
        sys.exit(1)
    
    try:
        Config.validate()
        generate_filtered_versions(Config.REPO_PATH, dataset_file, output_file)
    except Exception as e:
        logger.error(f"处理失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
