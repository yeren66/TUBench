"""
项目分析器 - 负责分析单个项目的所有commits
"""

import os
import json
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

from config import Config, AnalysisConfig
from utils.logger import get_logger
from modules import GitAnalyzer, CommitFilter
from .commit_analyzer import CommitAnalyzer
from .cache_manager import CacheManager
from .report_generator import ReportGenerator

logger = get_logger()


@dataclass
class ProjectAnalysisResult:
    """项目分析结果"""
    
    project_info: Dict[str, Any] = field(default_factory=dict)
    filter_funnel: Dict[str, Any] = field(default_factory=dict)
    type_statistics: Dict[str, Any] = field(default_factory=dict)
    execution_statistics: Dict[str, Any] = field(default_factory=dict)
    qualified_commits: List[str] = field(default_factory=list)
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)


class ProjectAnalyzer:
    """项目分析器"""
    
    def __init__(self,
                 project_path: str,
                 output_dir: str,
                 workers: int = 4,
                 resume: bool = False,
                 enable_cache: bool = True,
                 verbose: bool = False):
        """
        初始化项目分析器
        
        Args:
            project_path: 项目路径
            output_dir: 输出目录
            workers: 并发worker数
            resume: 是否断点续传
            enable_cache: 是否启用缓存
            verbose: 详细日志
        """
        self.project_path = project_path
        self.project_name = os.path.basename(project_path)
        self.output_dir = output_dir
        self.workers = workers
        self.resume = resume
        self.verbose = verbose
        
        # 初始化组件
        self.git_analyzer = GitAnalyzer(project_path)
        self.commit_filter = CommitFilter()
        self.cache_manager = CacheManager(
            cache_dir=os.path.join(AnalysisConfig.CACHE_DIR, self.project_name),
            enabled=enable_cache
        )
        self.report_generator = ReportGenerator(output_dir)
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'commits'), exist_ok=True)
        
        # 统计数据
        self._stats = {
            'total_commits': 0,
            'after_date_filter': 0,
            'has_test_and_source': 0,
            'has_method_changes': 0,
            'v1_build_success': 0,
            'v0_build_success': 0,
            'qualified': 0,
            'from_cache': 0,
            'errors': []
        }
    
    def analyze(self,
                since_date: str = None,
                sample: int = None,
                phase: str = 'full',
                single_commit: str = None) -> ProjectAnalysisResult:
        """
        执行项目分析
        
        Args:
            since_date: 起始日期 (YYYY-MM-DD)
            sample: 采样数量
            phase: 执行阶段 ('quick', 'method', 'full')
            single_commit: 只分析指定的commit
            
        Returns:
            项目分析结果
        """
        start_time = datetime.now()
        logger.info(f"开始分析项目: {self.project_name}")
        logger.info(f"分析阶段: {phase}")
        
        result = ProjectAnalysisResult()
        
        try:
            # 收集项目信息
            result.project_info = self._collect_project_info(since_date)
            if result.project_info.get('total_commits') is not None:
                self._stats['total_commits'] = result.project_info.get('total_commits', 0)
            
            # Phase 1: 快速扫描
            logger.info("\n[Phase 1] 快速扫描...")
            if single_commit:
                candidates = [single_commit]
                self._stats['total_commits'] = 1
                self._stats['after_date_filter'] = 1
            else:
                candidates = self._phase1_quick_scan(since_date)
            
            logger.info(f"  候选commits: {len(candidates)}")
            
            if phase == 'quick':
                # 只做快速扫描，保存中间结果
                self._save_phase_result('phase1', candidates)
                result.filter_funnel = self._build_filter_funnel()
                return result
            
            # Phase 2: 方法分析
            logger.info("\n[Phase 2] 方法级分析...")
            method_analyzed = self._phase2_method_analysis(candidates, sample)
            logger.info(f"  有方法变更的commits: {len(method_analyzed)}")
            
            if phase == 'method':
                # 保存中间结果
                self._save_phase_result('phase2', method_analyzed)
                result.filter_funnel = self._build_filter_funnel()
                return result
            
            # Phase 3: 执行分析
            logger.info("\n[Phase 3] 执行分析...")
            execution_results = self._phase3_execution_analysis(method_analyzed)
            
            # Phase 4: 分类判定
            logger.info("\n[Phase 4] 分类判定...")
            classified_results = self._phase4_classification(execution_results)
            
            # Phase 5: 报告生成
            logger.info("\n[Phase 5] 生成报告...")
            result = self._phase5_report_generation(classified_results, start_time, since_date)
            
            return result
            
        except Exception as e:
            logger.error(f"项目分析失败: {e}", exc_info=self.verbose)
            result.analysis_metadata['error'] = str(e)
            return result
    
    def _collect_project_info(self, since_date: str) -> dict:
        """收集项目基本信息"""
        repo = self.git_analyzer.repo
        
        # 获取所有commits来统计
        all_commits = list(repo.iter_commits('HEAD'))
        
        # 日期范围
        dates = [datetime.fromtimestamp(c.committed_date) for c in all_commits]
        
        return {
            'name': self.project_name,
            'path': self.project_path,
            'default_branch': repo.active_branch.name if not repo.head.is_detached else 'HEAD',
            'total_commits': len(all_commits),
            'date_range': {
                'earliest': min(dates).strftime('%Y-%m-%d') if dates else None,
                'latest': max(dates).strftime('%Y-%m-%d') if dates else None,
                'filter_since': since_date
            }
        }
    
    def _phase1_quick_scan(self, since_date: str) -> List[str]:
        """
        Phase 1: 快速扫描
        只检查文件变更，筛选同时修改测试和源代码的commits
        """
        # 解析日期
        date_filter = None
        if since_date:
            try:
                date_filter = datetime.strptime(since_date, "%Y-%m-%d")
            except:
                logger.warning(f"无效的日期格式: {since_date}")
        
        # 获取所有commits
        commits = self.git_analyzer.get_all_commits(since_date=date_filter)
        self._stats['total_commits'] = len(commits) if not date_filter else self._stats['total_commits']
        self._stats['after_date_filter'] = len(commits)
        
        candidates = []
        for i, commit in enumerate(commits):
            if i % 100 == 0:
                logger.debug(f"  扫描进度: {i}/{len(commits)}")
            
            # 获取变更文件
            changed_files = self.git_analyzer.get_changed_files(commit)
            
            # 检查是否同时修改了测试和源代码
            if self.commit_filter.filter_by_file_changes(changed_files):
                candidates.append(commit.hexsha)
        
        self._stats['has_test_and_source'] = len(candidates)
        return candidates
    
    def _phase2_method_analysis(self, candidates: List[str], sample: int = None) -> List[dict]:
        """
        Phase 2: 方法级分析
        分析每个commit的方法变更
        """
        if sample and len(candidates) > sample:
            logger.info(f"  采样 {sample} 个commits")
            import random
            candidates = random.sample(candidates, sample)
        
        analyzed = []
        
        for i, commit_hash in enumerate(candidates):
            if i % 20 == 0:
                logger.debug(f"  方法分析进度: {i}/{len(candidates)}")
            
            # 检查缓存
            if self.resume and self.cache_manager.has_cache(
                self.project_name, commit_hash, 'method'
            ):
                cached = self.cache_manager.get_cache(
                    self.project_name, commit_hash, 'method'
                )
                if cached and cached.get('data'):
                    analyzed.append(cached['data'])
                    self._stats['from_cache'] += 1
                    continue
            
            try:
                # 创建commit分析器并进行方法分析
                commit_analyzer = CommitAnalyzer(
                    repo_path=self.project_path,
                    output_dir=self.output_dir
                )
                
                method_info = commit_analyzer.analyze_methods(commit_hash)
                
                if method_info and method_info.get('has_method_changes'):
                    analyzed.append(method_info)
                    
                    # 缓存结果
                    self.cache_manager.set_cache(
                        self.project_name, commit_hash, 'method', method_info
                    )
                    
            except Exception as e:
                logger.debug(f"  方法分析失败 {commit_hash[:8]}: {e}")
                self._stats['errors'].append({
                    'commit': commit_hash,
                    'phase': 'method_analysis',
                    'error': str(e)
                })
        
        self._stats['has_method_changes'] = len(analyzed)
        return analyzed
    
    def _phase3_execution_analysis(self, method_analyzed: List[dict]) -> List[dict]:
        """
        Phase 3: 执行分析
        并发执行4个版本的构建和测试
        """
        results = []
        
        # 过滤已缓存的
        to_process = []
        for info in method_analyzed:
            commit_hash = info['commit_hash']
            
            if self.resume and self.cache_manager.has_cache(
                self.project_name, commit_hash, 'execution'
            ):
                cached = self.cache_manager.get_cache(
                    self.project_name, commit_hash, 'execution'
                )
                if cached and cached.get('data'):
                    cached_data = cached['data']
                    results.append(cached_data)
                    self._stats['from_cache'] += 1
                    if cached_data.get('v1_execution', {}).get('build', {}).get('success'):
                        self._stats['v1_build_success'] += 1
                    if cached_data.get('v0_execution', {}).get('build', {}).get('success'):
                        self._stats['v0_build_success'] += 1
                    # 确保输出目录存在对应的commit结果
                    self._save_commit_result(commit_hash, cached_data)
                    continue
            
            to_process.append(info)
        
        logger.info(f"  需要执行分析的commits: {len(to_process)} (缓存: {len(results)})")
        
        if not to_process:
            return results
        
        # 并发处理
        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            futures = {}
            
            for info in to_process:
                future = executor.submit(
                    _process_single_commit_execution,
                    self.project_path,
                    self.output_dir,
                    info
                )
                futures[future] = info['commit_hash']
            
            completed = 0
            for future in as_completed(futures):
                commit_hash = futures[future]
                completed += 1
                
                try:
                    result = future.result(timeout=AnalysisConfig.COMMIT_TIMEOUT)
                    
                    if result:
                        results.append(result)
                        
                        # 更新统计
                        if result.get('v1_execution', {}).get('build', {}).get('success'):
                            self._stats['v1_build_success'] += 1
                        if result.get('v0_execution', {}).get('build', {}).get('success'):
                            self._stats['v0_build_success'] += 1
                        
                        # 缓存结果
                        self.cache_manager.set_cache(
                            self.project_name, commit_hash, 'execution', result
                        )
                        
                        # 保存commit详情
                        self._save_commit_result(commit_hash, result)
                    
                    status = "✓" if result and result.get('qualified') else "✗"
                    logger.info(f"  [{completed}/{len(to_process)}] {commit_hash[:8]} {status}")
                    
                except Exception as e:
                    logger.error(f"  [{completed}/{len(to_process)}] {commit_hash[:8]} 失败: {e}")
                    self._stats['errors'].append({
                        'commit': commit_hash,
                        'phase': 'execution',
                        'error': str(e)
                    })
        
        return results
    
    def _phase4_classification(self, execution_results: List[dict]) -> List[dict]:
        """
        Phase 4: 分类判定
        """
        classified = []
        
        for result in execution_results:
            # 检查是否合格
            def _test_pass(execution: dict) -> bool:
                test_info = execution.get('test', {})
                status = test_info.get('status')
                if status:
                    return status == 'pass'
                return test_info.get('success', False)

            v1_ok = result.get('v1_execution', {}).get('build', {}).get('success', False) and \
                    _test_pass(result.get('v1_execution', {}))
            v0_ok = result.get('v0_execution', {}).get('build', {}).get('success', False) and \
                    _test_pass(result.get('v0_execution', {}))
            
            if not (v1_ok and v0_ok):
                result['qualified'] = False
                continue
            
            result['qualified'] = True
            self._stats['qualified'] += 1
            
            # 进行分类
            classification = self._classify_commit(result)
            result['classification'] = classification
            
            classified.append(result)
        
        return classified
    
    def _classify_commit(self, result: dict) -> dict:
        """对单个commit进行分类"""
        from modules.commit_classifier import CommitClassifier
        
        classifier = CommitClassifier(
            coverage_threshold=AnalysisConfig.COVERAGE_DECREASE_THRESHOLD
        )
        
        return classifier.classify(
            v1_result=result.get('v1_execution', {}),
            v05_result=result.get('v05_execution', {}),
            t05_result=result.get('t05_execution', {}),
            v0_result=result.get('v0_execution', {})
        )
    
    def _phase5_report_generation(self, classified_results: List[dict], 
                                  start_time: datetime,
                                  since_date: Optional[str] = None) -> ProjectAnalysisResult:
        """
        Phase 5: 生成报告
        """
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        result = ProjectAnalysisResult()
        
        # 项目信息
        result.project_info = self._collect_project_info(since_date)
        
        # 过滤漏斗
        result.filter_funnel = self._build_filter_funnel()
        
        # 类型统计
        result.type_statistics = self._build_type_statistics(classified_results)
        
        # 执行统计
        result.execution_statistics = self._build_execution_statistics(classified_results)
        
        # 合格commits列表（包含分类信息）
        result.qualified_commits = []
        for r in classified_results:
            if r.get('qualified'):
                primary_type = r.get('classification', {}).get('primary_type', '')
                result.qualified_commits.append({
                    'commit_hash': r['commit_hash'],
                    'primary_type': primary_type
                })
        
        # 元数据
        result.analysis_metadata = {
            'analysis_start_time': start_time.isoformat(),
            'analysis_end_time': end_time.isoformat(),
            'total_duration_seconds': duration,
            'workers_used': self.workers,
            'commits_analyzed': len(classified_results),
            'commits_from_cache': self._stats['from_cache'],
            'errors_count': len(self._stats['errors'])
        }
        
        # 生成报告文件
        self.report_generator.generate_project_summary_json(
            result,
            os.path.join(self.output_dir, 'analysis_result.json')
        )
        
        self.report_generator.generate_project_summary_markdown(
            result,
            os.path.join(self.output_dir, 'summary.md')
        )
        
        return result
    
    def _build_filter_funnel(self) -> dict:
        """构建过滤漏斗统计"""
        stats = self._stats
        
        def rate(num, denom):
            if denom == 0:
                return "0.0%"
            return f"{(num/denom*100):.1f}%"
        
        return {
            'stage0_total': stats['total_commits'],
            'stage1_after_date_filter': stats['after_date_filter'],
            'stage2_has_test_and_source': stats['has_test_and_source'],
            'stage3_has_method_changes': stats['has_method_changes'],
            'stage4_v1_build_success': stats['v1_build_success'],
            'stage5_v0_build_success': stats['v0_build_success'],
            'stage6_qualified': stats['qualified'],
            'filter_rates': {
                'date_filter': rate(stats['after_date_filter'], stats['total_commits']),
                'file_change_filter': rate(stats['has_test_and_source'], stats['after_date_filter']),
                'method_change_filter': rate(stats['has_method_changes'], stats['has_test_and_source']),
                'v1_build_filter': rate(stats['v1_build_success'], stats['has_method_changes']),
                'v0_build_filter': rate(stats['v0_build_success'], stats['v1_build_success']),
                'overall': rate(stats['qualified'], stats['total_commits'])
            }
        }
    
    def _build_type_statistics(self, results: List[dict]) -> dict:
        """构建类型统计"""
        type1_count = 0
        type1_compile = 0
        type1_runtime = 0
        type2_count = 0
        type3_count = 0
        
        coverage_decreases = []
        scenarios = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        
        type1_examples = []
        type2_examples = []
        type3_examples = []
        
        for r in results:
            if not r.get('qualified'):
                continue
            
            c = r.get('classification', {})
            
            # 场景统计
            scenario = c.get('scenario', 'D')
            scenarios[scenario] = scenarios.get(scenario, 0) + 1
            
            # Type1
            if c.get('type1_execution_error', {}).get('detected'):
                type1_count += 1
                subtype = c['type1_execution_error'].get('subtype')
                if subtype == 'compile_failure':
                    type1_compile += 1
                else:
                    type1_runtime += 1
                if len(type1_examples) < 3:
                    type1_examples.append(r['commit_hash'])
            
            # Type2
            if c.get('type2_coverage_decrease', {}).get('detected'):
                type2_count += 1
                evidence = c['type2_coverage_decrease'].get('evidence', {})
                if 'coverage_diff' in evidence:
                    coverage_decreases.append(evidence['coverage_diff'])
                if len(type2_examples) < 3:
                    type2_examples.append(r['commit_hash'])
            
            # Type3
            if c.get('type3_adaptive_change', {}).get('detected'):
                type3_count += 1
                if len(type3_examples) < 3:
                    type3_examples.append(r['commit_hash'])
        
        total = len([r for r in results if r.get('qualified')])
        
        def pct(n):
            return f"{(n/total*100):.1f}%" if total > 0 else "0.0%"
        
        return {
            'type1_execution_error': {
                'count': type1_count,
                'percentage': pct(type1_count),
                'subtypes': {
                    'compile_failure': type1_compile,
                    'runtime_failure': type1_runtime
                },
                'examples': type1_examples
            },
            'type2_coverage_decrease': {
                'count': type2_count,
                'percentage': pct(type2_count),
                'avg_coverage_decrease': sum(coverage_decreases) / len(coverage_decreases) if coverage_decreases else 0,
                'examples': type2_examples
            },
            'type3_adaptive_change': {
                'count': type3_count,
                'percentage': pct(type3_count),
                'examples': type3_examples
            },
            'scenario_distribution': scenarios
        }
    
    def _build_execution_statistics(self, results: List[dict]) -> dict:
        """构建执行统计"""
        v05_compile_success = 0
        v05_test_success = 0
        t05_compile_success = 0
        t05_test_success = 0
        
        for r in results:
            v05 = r.get('v05_execution', {})
            t05 = r.get('t05_execution', {})
            
            if v05.get('build', {}).get('success'):
                v05_compile_success += 1
            if v05.get('test', {}).get('status') == 'pass' or v05.get('test', {}).get('success'):
                v05_test_success += 1
            if t05.get('build', {}).get('success'):
                t05_compile_success += 1
            if t05.get('test', {}).get('status') == 'pass' or t05.get('test', {}).get('success'):
                t05_test_success += 1
        
        return {
            'v05_results': {
                'compile_success': v05_compile_success,
                'compile_failed': len(results) - v05_compile_success,
                'test_success': v05_test_success,
                'test_failed': v05_compile_success - v05_test_success
            },
            't05_results': {
                'compile_success': t05_compile_success,
                'compile_failed': len(results) - t05_compile_success,
                'test_success': t05_test_success,
                'test_failed': t05_compile_success - t05_test_success
            }
        }
    
    def _save_phase_result(self, phase: str, data: List):
        """保存阶段结果"""
        output_path = os.path.join(self.output_dir, f'{phase}_result.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'phase': phase,
                'timestamp': datetime.now().isoformat(),
                'count': len(data),
                'data': data
            }, f, indent=2, ensure_ascii=False)
        logger.info(f"  阶段结果已保存: {output_path}")
    
    def _save_commit_result(self, commit_hash: str, result: dict):
        """保存单个commit的分析结果"""
        # 获取分类类型（用于目录名前缀）
        classification = result.get('classification', {})
        primary_type = classification.get('primary_type', '')
        
        # 提取类型编号 (type1_execution_error -> type1, type2_coverage_decrease -> type2, etc.)
        type_prefix = ''
        if primary_type:
            if primary_type.startswith('type1'):
                type_prefix = 'type1_'
            elif primary_type.startswith('type2'):
                type_prefix = 'type2_'
            elif primary_type.startswith('type3'):
                type_prefix = 'type3_'
        
        # 使用前8位作为目录名（足够唯一标识），加上类型前缀
        short_hash = commit_hash[:8]
        dir_name = f"{type_prefix}{short_hash}" if type_prefix else short_hash
        commit_dir = os.path.join(self.output_dir, 'commits', dir_name)
        os.makedirs(commit_dir, exist_ok=True)
        
        # JSON 文件放在 commit 目录下，命名为 detail.json
        output_path = os.path.join(commit_dir, 'detail.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        # 保存 diff 文件
        diff_info = result.get('diff_info', {})
        self._write_diff_file(commit_dir, 'full.diff', diff_info.get('full_diff'))
        self._write_diff_file(commit_dir, 'source_only.diff', diff_info.get('source_only_diff'))
        self._write_diff_file(commit_dir, 'test_only.diff', diff_info.get('test_only_diff'))

        # 生成可视化友好的摘要
        self.report_generator.generate_commit_summary_markdown(
            result,
            os.path.join(commit_dir, 'summary.md')
        )

    def _write_diff_file(self, commit_dir: str, filename: str, content: str):
        """写入diff文件，便于在编辑器中高亮查看"""
        if content is None:
            return
        path = os.path.join(commit_dir, filename)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logger.debug(f"写入diff失败 {path}: {e}")


def _process_single_commit_execution(repo_path: str, output_dir: str, method_info: dict) -> dict:
    """
    处理单个commit的执行分析（在独立进程中运行）
    """
    from .commit_analyzer import CommitAnalyzer
    
    commit_analyzer = CommitAnalyzer(
        repo_path=repo_path,
        output_dir=output_dir
    )
    
    try:
        return commit_analyzer.analyze_execution(method_info)
    except Exception as e:
        logger.error(f"执行分析失败 {method_info['commit_hash'][:8]}: {e}")
        return None
