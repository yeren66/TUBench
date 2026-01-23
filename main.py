"""
测试演化数据集构建工具 - 主程序
"""

import sys
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from config import Config
from utils.logger import setup_logger, get_logger
from modules import (
    GitAnalyzer,
    CodeAnalyzer,
    ChangeDetector,
    MavenExecutor,
    CoverageAnalyzer,
    CommitFilter,
    DatasetGenerator
)

# 设置日志
setup_logger()
logger = get_logger()


class DatasetBuilder:
    """数据集构建器主类"""
    
    def __init__(self, repo_path):
        """
        初始化数据集构建器
        
        Args:
            repo_path: Git仓库路径
        """
        self.repo_path = repo_path
        self.git_analyzer = GitAnalyzer(repo_path)
        self.code_analyzer = CodeAnalyzer()
        self.change_detector = ChangeDetector()
        self.commit_filter = CommitFilter()
        self.dataset_generator = DatasetGenerator(
            Config.get_output_path(Config.OUTPUT_FILE)
        )
    
    def run(self):
        """运行数据集构建流程"""
        logger.info("=" * 80)
        logger.info("测试演化数据集构建工具")
        logger.info("=" * 80)
        
        try:
            # 阶段1: 获取所有commits
            logger.info("\n[阶段1] 获取commits...")
            commits = self.git_analyzer.get_all_commits(
                since_date=Config.get_date_filter()
            )
            
            if not commits:
                logger.error("未找到符合条件的commits")
                return
            
            logger.info(f"共找到 {len(commits)} 个commits待处理")
            
            # 加载已处理的commits（支持断点续传）
            if Config.SAVE_INTERMEDIATE:
                processed_hashes = self.dataset_generator.load_intermediate_results(
                    Config.get_output_path(Config.INTERMEDIATE_FILE)
                )
                commits = [c for c in commits if c.hexsha not in processed_hashes]
                logger.info(f"跳过已处理的commits，剩余 {len(commits)} 个待处理")
            
            # 阶段2: 快速预筛选
            logger.info("\n[阶段2] 快速预筛选...")
            filtered_commits = self.pre_filter_commits(commits)
            logger.info(f"预筛选后剩余 {len(filtered_commits)} 个commits")
            
            if not filtered_commits:
                logger.warning("没有commits通过预筛选")
                return
            
            # 阶段3: 详细分析（并行处理）
            logger.info("\n[阶段3] 详细分析（并行处理）...")
            self.process_commits_parallel(filtered_commits)
            
            # 保存最终数据集
            logger.info("\n[阶段4] 保存数据集...")
            self.dataset_generator.save_dataset()
            
            # 输出统计信息
            stats = self.dataset_generator.get_statistics()
            logger.info("\n" + "=" * 80)
            logger.info("构建完成！统计信息:")
            logger.info(f"  总计处理: {stats['total_commits']} commits")
            logger.info(f"  符合标准: {stats['qualified_commits']} commits")
            logger.info(f"  合格率: {stats['qualification_rate']:.2%}")
            logger.info("=" * 80)
        
        except Exception as e:
            logger.error(f"构建失败: {e}", exc_info=True)
    
    def pre_filter_commits(self, commits):
        """
        快速预筛选commits（不切换版本）
        
        Args:
            commits: commit对象列表
            
        Returns:
            list: 通过预筛选的commits
        """
        filtered = []
        
        for i, commit in enumerate(commits):
            logger.info(f"预筛选 [{i+1}/{len(commits)}]: {commit.hexsha[:8]}")
            
            # 获取变更文件
            changed_files = self.git_analyzer.get_changed_files(commit)
            
            # 必须同时修改测试文件和源代码文件
            if self.commit_filter.filter_by_file_changes(changed_files):
                filtered.append(commit)
                logger.debug(f"  ✓ 通过预筛选")
            else:
                logger.debug(f"  ✗ 未通过预筛选")
        
        return filtered
    
    def process_commits_parallel(self, commits):
        """
        并行处理commits
        
        Args:
            commits: commit对象列表
        """
        # 将commit对象转换为可序列化的数据
        commit_hashes = [c.hexsha for c in commits]
        
        with ProcessPoolExecutor(max_workers=Config.PARALLEL_WORKERS) as executor:
            futures = {
                executor.submit(
                    process_single_commit_worker,
                    self.repo_path,
                    commit_hash
                ): commit_hash
                for commit_hash in commit_hashes
            }
            
            completed = 0
            for future in as_completed(futures):
                commit_hash = futures[future]
                completed += 1
                
                try:
                    result = future.result()
                    
                    if result:
                        formatted_data = self.dataset_generator.format_commit_data(result)
                        self.dataset_generator.add_commit(formatted_data)
                        
                        status = "✓ 合格" if result.get('qualified') else "✗ 不合格"
                        logger.info(f"[{completed}/{len(commits)}] {commit_hash[:8]} - {status}")
                    
                    # 定期保存中间结果
                    if Config.SAVE_INTERMEDIATE and completed % Config.SAVE_INTERVAL == 0:
                        self.dataset_generator.save_intermediate_results(
                            Config.get_output_path(Config.INTERMEDIATE_FILE)
                        )
                
                except Exception as e:
                    logger.error(f"处理commit失败 [{commit_hash[:8]}]: {e}")
        
        # 最终保存中间结果
        if Config.SAVE_INTERMEDIATE:
            self.dataset_generator.save_intermediate_results(
                Config.get_output_path(Config.INTERMEDIATE_FILE)
            )


def process_single_commit_worker(repo_path, commit_hash):
    """
    Worker函数：处理单个commit（在独立进程中运行）
    
    Args:
        repo_path: Git仓库路径
        commit_hash: commit哈希值
        
    Returns:
        dict: commit处理结果
    """
    # 在worker进程中重新初始化
    git_analyzer = GitAnalyzer(repo_path)
    code_analyzer = CodeAnalyzer()
    change_detector = ChangeDetector()
    maven_executor = None
    coverage_analyzer = CoverageAnalyzer()
    commit_filter = CommitFilter()
    
    commit = git_analyzer.repo.commit(commit_hash)
    
    # 获取基本信息
    commit_info = git_analyzer.get_commit_info(commit)
    commit_info['changed_files'] = git_analyzer.get_changed_files(commit)
    commit_info['changed_methods'] = {'test_methods': [], 'source_methods': []}
    commit_info['coverage_analysis'] = {}
    commit_info['build_status'] = {'parent_success': False, 'child_success': False}
    
    try:
        # 分析变更的方法
        for test_file in commit_info['changed_files']['test_files']:
            diff_text = git_analyzer.get_file_diff(commit, test_file)
            file_content = git_analyzer.get_file_content(commit.hexsha, test_file)
            
            if file_content:
                changed_methods = change_detector.detect_changed_methods(
                    file_content, diff_text, code_analyzer
                )
                # 添加包信息
                package = code_analyzer.get_package_name(file_content)
                for method in changed_methods:
                    method['package'] = package
                    method['file'] = test_file
                commit_info['changed_methods']['test_methods'].extend(changed_methods)
        
        for source_file in commit_info['changed_files']['source_files']:
            diff_text = git_analyzer.get_file_diff(commit, source_file)
            file_content = git_analyzer.get_file_content(commit.hexsha, source_file)
            
            if file_content:
                changed_methods = change_detector.detect_changed_methods(
                    file_content, diff_text, code_analyzer
                )
                # 添加包信息
                package = code_analyzer.get_package_name(file_content)
                for method in changed_methods:
                    method['package'] = package
                    method['file'] = source_file
                commit_info['changed_methods']['source_methods'].extend(changed_methods)
        
        # 检查是否有方法级别的变更
        if not commit_filter.filter_by_method_changes(commit_info['changed_methods']):
            commit_info['qualified'] = False
            commit_info['filter_reasons'] = ['方法变更不符合要求']
            return commit_info
        
        # 创建worktree进行构建和测试
        worktree_path = Config.WORKTREE_PREFIX + commit_hash
        
        # 处理父commit
        if commit.parents:
            parent_hash = commit.parents[0].hexsha
            if git_analyzer.create_worktree(parent_hash, worktree_path):
                maven_executor = MavenExecutor(worktree_path)
                
                if maven_executor.has_pom():
                    # 执行测试并收集覆盖率
                    test_result = maven_executor.test_with_jacoco()
                    commit_info['build_status']['parent_success'] = test_result['success']
                    
                    if test_result['success'] and test_result['jacoco_report']:
                        coverage_data = coverage_analyzer.parse_jacoco_report(
                            test_result['jacoco_report']
                        )
                        
                        if coverage_data:
                            commit_info['coverage_analysis']['parent_commit'] = \
                                coverage_analyzer.analyze_test_coverage_for_changes(
                                    coverage_data,
                                    commit_info['changed_methods']['test_methods'],
                                    commit_info['changed_methods']['source_methods']
                                )
                
                git_analyzer.remove_worktree(worktree_path)
        
        # 处理子commit
        if git_analyzer.create_worktree(commit_hash, worktree_path):
            maven_executor = MavenExecutor(worktree_path)
            
            if maven_executor.has_pom():
                test_result = maven_executor.test_with_jacoco()
                commit_info['build_status']['child_success'] = test_result['success']
                
                if test_result['success'] and test_result['jacoco_report']:
                    coverage_data = coverage_analyzer.parse_jacoco_report(
                        test_result['jacoco_report']
                    )
                    
                    if coverage_data:
                        commit_info['coverage_analysis']['child_commit'] = \
                            coverage_analyzer.analyze_test_coverage_for_changes(
                                coverage_data,
                                commit_info['changed_methods']['test_methods'],
                                commit_info['changed_methods']['source_methods']
                            )
            
            git_analyzer.remove_worktree(worktree_path)
        
        # 应用所有过滤条件
        qualified, reasons = commit_filter.apply_all_filters(
            commit_info,
            threshold=Config.COVERAGE_THRESHOLD
        )
        
        commit_info['qualified'] = qualified
        commit_info['filter_reasons'] = reasons
        
    except Exception as e:
        logger.error(f"处理commit异常 [{commit_hash[:8]}]: {e}")
        commit_info['qualified'] = False
        commit_info['filter_reasons'] = [f'处理异常: {str(e)}']
    
    return commit_info


def main():
    """主函数"""
    # 检查配置
    if len(sys.argv) > 1:
        Config.REPO_PATH = sys.argv[1]
    
    try:
        Config.validate()
    except ValueError as e:
        logger.error(str(e))
        logger.info("\n使用方法: python main.py <git_repo_path>")
        logger.info("或在config.py中设置REPO_PATH")
        sys.exit(1)
    
    # 构建数据集
    builder = DatasetBuilder(Config.REPO_PATH)
    builder.run()


if __name__ == "__main__":
    main()
