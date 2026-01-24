"""
TUBench Analysis Tool - 分析工具主入口
用于分析Java项目中的测试演化数据，筛选和分类符合条件的commits
"""

import sys
import os
import argparse
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config, AnalysisConfig
from utils.logger import setup_logger, get_logger
from analysis.project_analyzer import ProjectAnalyzer
from analysis.report_generator import ReportGenerator


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='TUBench Analysis Tool - 测试演化数据集分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 分析单个项目
  python analysis.py --project /path/to/commons-csv
  
  # 分析目录下所有项目
  python analysis.py --projects-dir /path/to/defects4j-projects
  
  # 指定输出目录和并发数
  python analysis.py --project /path/to/project --output ./output --workers 8
  
  # 快速扫描模式（只做文件级筛选）
  python analysis.py --project /path/to/project --phase quick
  
  # 断点续传
  python analysis.py --project /path/to/project --resume
  
  # 分析指定commit
  python analysis.py --project /path/to/project --commit abc123
        '''
    )
    
    # 项目路径（二选一）
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--project', '-p', type=str,
                       help='单个项目的路径')
    group.add_argument('--projects-dir', '-d', type=str,
                       help='包含多个项目的目录路径')
    
    # 输出配置
    parser.add_argument('--output', '-o', type=str,
                        default=None,
                        help='输出目录 (默认: ./output/analysis/<project>_<YYYY-MM-DD>)')
    
    # 执行配置
    parser.add_argument('--workers', '-w', type=int,
                        default=4,
                        help='并发worker数量 (默认: 4)')
    parser.add_argument('--phase', type=str,
                        choices=['quick', 'method', 'full'],
                        default='full',
                        help='执行阶段: quick(快速扫描), method(方法分析), full(完整分析)')
    
    # 过滤配置
    parser.add_argument('--since', type=str,
                        default='2016-01-01',
                        help='只分析此日期之后的commits (默认: 2016-01-01)')
    parser.add_argument('--sample', type=int,
                        help='采样数量，用于快速测试')
    parser.add_argument('--commit', type=str,
                        help='只分析指定的commit')
    
    # 其他选项
    parser.add_argument('--resume', action='store_true',
                        help='断点续传，跳过已分析的commits')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='详细日志输出')
    parser.add_argument('--no-cache', action='store_true',
                        help='禁用缓存')
    
    return parser.parse_args()


def validate_project_path(path: str) -> bool:
    """验证项目路径"""
    if not os.path.exists(path):
        return False
    
    # 检查是否为Git仓库
    git_dir = os.path.join(path, '.git')
    if not os.path.exists(git_dir):
        return False
    
    # 检查是否有pom.xml（Maven项目）
    pom_file = os.path.join(path, 'pom.xml')
    if not os.path.exists(pom_file):
        return False
    
    return True


def get_project_list(args) -> list:
    """获取要分析的项目列表"""
    projects = []
    
    if args.project:
        # 单个项目
        if validate_project_path(args.project):
            projects.append(args.project)
        else:
            raise ValueError(f"无效的项目路径: {args.project}")
    
    elif args.projects_dir:
        # 多个项目
        if not os.path.exists(args.projects_dir):
            raise ValueError(f"目录不存在: {args.projects_dir}")
        
        for name in sorted(os.listdir(args.projects_dir)):
            path = os.path.join(args.projects_dir, name)
            if os.path.isdir(path) and validate_project_path(path):
                projects.append(path)
        
        if not projects:
            raise ValueError(f"在 {args.projects_dir} 中未找到有效的Maven项目")
    
    return projects


def _get_output_dir(args, project_name: str) -> str:
    """生成项目输出目录（默认: ./output/analysis/<project>_<YYYY-MM-DD_HH-MM-SS>）"""
    if args.output:
        return os.path.join(args.output, project_name)
    date_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    return os.path.join('./output/analysis', f"{project_name}_{date_str}")


def analyze_single_project(project_path: str, args, logger) -> dict:
    """分析单个项目"""
    project_name = os.path.basename(project_path)
    logger.info(f"\n{'='*60}")
    logger.info(f"开始分析项目: {project_name}")
    logger.info(f"路径: {project_path}")
    logger.info(f"{'='*60}")
    
    # 创建项目分析器
    output_dir = _get_output_dir(args, project_name)
    analyzer = ProjectAnalyzer(
        project_path=project_path,
        output_dir=output_dir,
        workers=args.workers,
        resume=args.resume,
        enable_cache=not args.no_cache,
        verbose=args.verbose
    )
    
    # 执行分析
    try:
        result = analyzer.analyze(
            since_date=args.since,
            sample=args.sample,
            phase=args.phase,
            single_commit=args.commit
        )
        
        logger.info(f"\n项目 {project_name} 分析完成!")
        logger.info(f"  合格commits: {len(result.qualified_commits)}")
        logger.info(f"  Type1 (执行出错): {result.type_statistics.get('type1_execution_error', {}).get('count', 0)}")
        logger.info(f"  Type2 (覆盖率降低): {result.type_statistics.get('type2_coverage_decrease', {}).get('count', 0)}")
        logger.info(f"  Type3 (适应性调整): {result.type_statistics.get('type3_adaptive_change', {}).get('count', 0)}")
        
        return {
            'project': project_name,
            'success': True,
            'result': result
        }
        
    except Exception as e:
        logger.error(f"项目 {project_name} 分析失败: {e}", exc_info=args.verbose)
        return {
            'project': project_name,
            'success': False,
            'error': str(e)
        }


def main():
    """主函数"""
    # 解析参数
    args = parse_args()
    
    # 设置日志
    log_level = 'DEBUG' if args.verbose else 'INFO'
    setup_logger(level=log_level)
    logger = get_logger()
    
    logger.info("="*60)
    logger.info("TUBench Analysis Tool")
    logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)
    
    try:
        # 获取项目列表
        projects = get_project_list(args)
        logger.info(f"找到 {len(projects)} 个项目待分析")
        
        # 创建输出目录
        base_output = args.output if args.output else './output/analysis'
        os.makedirs(base_output, exist_ok=True)
        
        # 分析每个项目
        all_results = []
        for i, project_path in enumerate(projects):
            logger.info(f"\n[{i+1}/{len(projects)}] 处理项目...")
            result = analyze_single_project(project_path, args, logger)
            all_results.append(result)
        
        # 生成全局汇总报告（如果有多个项目）
        if len(projects) > 1:
            logger.info("\n生成全局汇总报告...")
            report_generator = ReportGenerator(args.output)
            successful_results = [r['result'] for r in all_results if r['success']]
            if successful_results:
                report_generator.generate_global_summary(
                    successful_results,
                    os.path.join(args.output, 'global_summary')
                )
        
        # 输出总结
        logger.info("\n" + "="*60)
        logger.info("分析完成!")
        logger.info("="*60)
        
        successful = sum(1 for r in all_results if r['success'])
        failed = sum(1 for r in all_results if not r['success'])
        
        logger.info(f"成功: {successful} 个项目")
        if failed > 0:
            logger.info(f"失败: {failed} 个项目")
            for r in all_results:
                if not r['success']:
                    logger.info(f"  - {r['project']}: {r['error']}")
        
        logger.info(f"\n输出目录: {args.output}")
        
    except Exception as e:
        logger.error(f"执行失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
