"""
Commit分析器 - 负责分析单个commit的完整信息
"""

import os
import json
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor

from config import Config, AnalysisConfig
from utils.logger import get_logger
from modules import GitAnalyzer, CodeAnalyzer, ChangeDetector
from modules.diff_filter import DiffFilter
from modules.isolated_executor import IsolatedExecutor
from modules.commit_classifier import CommitClassifier

logger = get_logger()


@dataclass
class CommitAnalysisResult:
    """单个Commit的完整分析结果"""
    
    basic_info: Dict[str, Any] = field(default_factory=dict)
    file_changes: Dict[str, Any] = field(default_factory=dict)
    method_changes: Dict[str, Any] = field(default_factory=dict)
    diff_info: Dict[str, Any] = field(default_factory=dict)
    v1_execution: Dict[str, Any] = field(default_factory=dict)
    v05_execution: Dict[str, Any] = field(default_factory=dict)
    t05_execution: Dict[str, Any] = field(default_factory=dict)
    v0_execution: Dict[str, Any] = field(default_factory=dict)
    classification: Dict[str, Any] = field(default_factory=dict)
    test_source_mapping: Dict[str, Any] = field(default_factory=dict)
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return asdict(self)


class CommitAnalyzer:
    """单个Commit分析器"""
    
    def __init__(self, repo_path: str, output_dir: str):
        """
        初始化
        
        Args:
            repo_path: 仓库路径
            output_dir: 输出目录
        """
        self.repo_path = repo_path
        self.output_dir = output_dir
        self.project_name = os.path.basename(repo_path)
        
        # 初始化组件
        self.git_analyzer = GitAnalyzer(repo_path)
        self.code_analyzer = CodeAnalyzer()
        self.change_detector = ChangeDetector()
        self.diff_filter = DiffFilter()
    
    def analyze_full(self, commit_hash: str) -> CommitAnalysisResult:
        """
        完整分析单个commit
        
        Args:
            commit_hash: commit hash
            
        Returns:
            完整的分析结果
        """
        start_time = datetime.now()
        result = CommitAnalysisResult()
        
        try:
            # 1. 收集基础信息
            result.basic_info = self._collect_basic_info(commit_hash)
            
            # 2. 分析文件变更
            result.file_changes = self._analyze_file_changes(commit_hash)
            
            # 3. 分析方法变更
            result.method_changes = self._analyze_method_changes(commit_hash, result.file_changes)
            
            # 4. 处理diff
            result.diff_info = self._process_diff(commit_hash)

            # 4.1 统计方法级变更行数
            result.method_changes['method_change_stats'] = self._compute_method_change_stats(
                commit_hash,
                result.basic_info.get('parent_hash'),
                result.file_changes
            )
            
            # 5. 执行4个版本
            execution_results = self._execute_all_versions(
                commit_hash,
                result.basic_info.get('parent_hash'),
                result.diff_info,
                result.method_changes.get('source_methods', []),
                result.method_changes.get('test_methods', [])
            )
            result.v1_execution = execution_results.get('v1', {})
            result.v05_execution = execution_results.get('v05', {})
            result.t05_execution = execution_results.get('t05', {})
            result.v0_execution = execution_results.get('v0', {})
            
            # 6. 分类判定
            result.classification = self._classify(
                result.v1_execution,
                result.v05_execution,
                result.t05_execution,
                result.v0_execution
            )
            
            # 7. 分析元数据
            end_time = datetime.now()
            result.analysis_metadata = {
                'analysis_timestamp': end_time.isoformat(),
                'analysis_duration_seconds': (end_time - start_time).total_seconds(),
                'project': self.project_name,
                'commit_hash': commit_hash,
                'phases_completed': ['basic', 'file', 'method', 'diff', 'execution', 'classification']
            }
            
        except Exception as e:
            logger.error(f"分析commit失败 {commit_hash[:8]}: {e}")
            result.analysis_metadata['error'] = str(e)
        
        return result
    
    def analyze_methods(self, commit_hash: str) -> Optional[dict]:
        """
        只进行方法级分析（Phase 2使用）
        
        Args:
            commit_hash: commit hash
            
        Returns:
            方法分析结果，如果没有方法变更则返回None
        """
        try:
            # 基础信息
            basic_info = self._collect_basic_info(commit_hash)
            if not basic_info.get('parent_hash'):
                return None
            
            # 文件变更
            file_changes = self._analyze_file_changes(commit_hash)
            
            # 方法变更
            method_changes = self._analyze_method_changes(commit_hash, file_changes)
            
            # 检查是否有方法级变更
            source_methods = method_changes.get('source_methods', [])
            test_methods = method_changes.get('test_methods', [])
            
            if not source_methods or not test_methods:
                return None
            
            # Diff信息
            diff_info = self._process_diff(commit_hash)
            method_change_stats = self._compute_method_change_stats(
                commit_hash,
                basic_info.get('parent_hash'),
                file_changes
            )
            
            return {
                'commit_hash': commit_hash,
                'parent_hash': basic_info.get('parent_hash'),
                'basic_info': basic_info,
                'file_changes': file_changes,
                'method_changes': method_changes,
                'diff_info': diff_info,
                'method_change_stats': method_change_stats,
                'has_method_changes': True
            }
            
        except Exception as e:
            logger.debug(f"方法分析失败 {commit_hash[:8]}: {e}")
            return None
    
    def analyze_execution(self, method_info: dict) -> Optional[dict]:
        """
        执行分析（Phase 3使用）
        
        Args:
            method_info: Phase 2的方法分析结果
            
        Returns:
            包含执行结果的完整信息
        """
        commit_hash = method_info['commit_hash']
        parent_hash = method_info['parent_hash']
        diff_info = method_info['diff_info']
        
        try:
            # 执行4个版本
            execution_results = self._execute_all_versions(
                commit_hash,
                parent_hash,
                diff_info,
                method_info.get('method_changes', {}).get('source_methods', []),
                method_info.get('method_changes', {}).get('test_methods', [])
            )
            
            # 检查V-1和V0是否都成功
            def _test_pass(execution: dict) -> bool:
                test_info = execution.get('test', {})
                status = test_info.get('status')
                if status:
                    return status == 'pass'
                return test_info.get('success', False)

            v1_ok = execution_results.get('v1', {}).get('build', {}).get('success', False) and \
                    _test_pass(execution_results.get('v1', {}))
            v0_ok = execution_results.get('v0', {}).get('build', {}).get('success', False) and \
                    _test_pass(execution_results.get('v0', {}))
            
            qualified = v1_ok and v0_ok
            
            # 分类
            classification = {}
            if qualified:
                classification = self._classify(
                    execution_results.get('v1', {}),
                    execution_results.get('v05', {}),
                    execution_results.get('t05', {}),
                    execution_results.get('v0', {})
                )
            
            # 合并结果
            result = {
                **method_info,
                'v1_execution': execution_results.get('v1', {}),
                'v05_execution': execution_results.get('v05', {}),
                't05_execution': execution_results.get('t05', {}),
                'v0_execution': execution_results.get('v0', {}),
                'classification': classification,
                'qualified': qualified,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"执行分析失败 {commit_hash[:8]}: {e}")
            return None
    
    def _collect_basic_info(self, commit_hash: str) -> dict:
        """收集基础信息"""
        commit = self.git_analyzer.repo.commit(commit_hash)
        info = self.git_analyzer.get_commit_info(commit)
        
        return {
            'project': self.project_name,
            'commit_hash': commit_hash,
            'short_hash': commit_hash[:8],
            'parent_hash': info.get('parent_hash'),
            'parent_short_hash': info.get('parent_hash', '')[:8] if info.get('parent_hash') else None,
            'author': info.get('author'),
            'date': info.get('date'),
            'message': info.get('message'),
            'message_subject': info.get('message', '').split('\n')[0] if info.get('message') else ''
        }
    
    def _analyze_file_changes(self, commit_hash: str) -> dict:
        """分析文件变更"""
        commit = self.git_analyzer.repo.commit(commit_hash)
        changed_files = self.git_analyzer.get_changed_files(commit)
        
        source_files = []
        test_files = []
        other_files = []
        
        # 获取详细的文件变更信息
        if commit.parents:
            parent = commit.parents[0]
            diffs = parent.diff(commit)
            
            for diff in diffs:
                file_path = diff.b_path or diff.a_path
                
                # 判断变更类型
                if diff.new_file:
                    change_type = 'added'
                elif diff.deleted_file:
                    change_type = 'deleted'
                elif diff.renamed:
                    change_type = 'renamed'
                else:
                    change_type = 'modified'
                
                file_info = {
                    'path': file_path,
                    'change_type': change_type,
                    'old_path': diff.a_path if diff.renamed else None,
                    'is_java': file_path.endswith('.java')
                }
                
                # 分类
                if file_path in changed_files.get('source_files', []):
                    source_files.append(file_info)
                elif file_path in changed_files.get('test_files', []):
                    test_files.append(file_info)
                else:
                    other_files.append(file_info)
        
        return {
            'source_files': source_files,
            'test_files': test_files,
            'other_files': other_files,
            'summary': {
                'total_files': len(source_files) + len(test_files) + len(other_files),
                'source_count': len(source_files),
                'test_count': len(test_files),
                'other_count': len(other_files)
            }
        }
    
    def _analyze_method_changes(self, commit_hash: str, file_changes: dict) -> dict:
        """分析方法变更
        
        正确处理新增行和删除行的方法归属：
        - 新增行 (+) 对应当前版本的行号，在当前版本的方法结构中查找
        - 删除行 (-) 对应父版本的行号，在父版本的方法结构中查找
        """
        commit = self.git_analyzer.repo.commit(commit_hash)
        parent_hash = commit.parents[0].hexsha if commit.parents else None
        
        source_methods = []
        test_methods = []
        
        # 分析源文件中的方法变更
        for file_info in file_changes.get('source_files', []):
            methods = self._analyze_single_file_methods(
                commit_hash, parent_hash, commit, file_info, is_test=False
            )
            source_methods.extend(methods)
        
        # 分析测试文件中的方法变更
        for file_info in file_changes.get('test_files', []):
            methods = self._analyze_single_file_methods(
                commit_hash, parent_hash, commit, file_info, is_test=True
            )
            test_methods.extend(methods)
        
        return {
            'source_methods': source_methods,
            'test_methods': test_methods,
            'summary': {
                'source_methods_count': len(source_methods),
                'test_methods_count': len(test_methods)
            }
        }
    
    def _analyze_single_file_methods(self, commit_hash: str, parent_hash: str, 
                                      commit, file_info: dict, is_test: bool) -> list:
        """分析单个文件的方法变更
        
        Args:
            commit_hash: 当前commit hash
            parent_hash: 父commit hash
            commit: commit对象
            file_info: 文件信息
            is_test: 是否为测试文件
            
        Returns:
            list: 变更的方法列表
        """
        file_path = file_info.get('path')
        change_type = file_info.get('change_type')
        
        if not file_path or not file_path.endswith('.java'):
            return []
        
        try:
            diff_text = self.git_analyzer.get_file_diff(commit, file_path)
            if not diff_text:
                return []
            
            # 获取当前版本和父版本的文件内容
            current_content = self.git_analyzer.get_file_content(commit_hash, file_path)
            parent_content = self.git_analyzer.get_file_content(parent_hash, file_path) if parent_hash else None
            
            # 文件被删除的情况：只有父版本有内容
            if change_type == 'deleted':
                current_content = None
            # 文件被新增的情况：只有当前版本有内容
            elif change_type == 'added':
                parent_content = None
            
            # 提取两个版本的方法结构
            current_methods = self._extract_methods_from_content(current_content, file_path)
            parent_methods = self._extract_methods_from_content(parent_content, file_path)
            
            # 解析diff获取变更行号
            parsed_diff = self.change_detector.parse_diff(diff_text)
            
            # 收集变更的方法（使用set去重）
            changed_method_keys = set()
            changed_methods_map = {}
            
            for entry in parsed_diff:
                for change in entry.get('changes', []):
                    # 新增行 -> 在当前版本的方法中查找
                    for line_no in change.get('added_lines', []):
                        method = self._find_method_at_line(current_methods, line_no)
                        if method:
                            key = self._get_method_key(method)
                            if key not in changed_method_keys:
                                changed_method_keys.add(key)
                                changed_methods_map[key] = method.copy()
                    
                    # 删除行 -> 在父版本的方法中查找
                    for line_no in change.get('removed_lines', []):
                        method = self._find_method_at_line(parent_methods, line_no)
                        if method:
                            key = self._get_method_key(method)
                            if key not in changed_method_keys:
                                changed_method_keys.add(key)
                                # 对于删除的行，优先使用当前版本的方法信息（如果存在）
                                current_method = self._find_method_by_key(current_methods, key)
                                changed_methods_map[key] = (current_method or method).copy()
            
            # 转换为结果列表
            result_methods = []
            for method in changed_methods_map.values():
                if is_test:
                    method['is_test_method'] = self._is_test_method(method)
                result_methods.append(method)
            
            return result_methods
            
        except Exception as e:
            logger.debug(f"分析文件方法失败 {file_path}: {e}")
            return []
    
    def _extract_methods_from_content(self, content: str, file_path: str) -> list:
        """从文件内容中提取所有方法信息
        
        Args:
            content: 文件内容
            file_path: 文件路径
            
        Returns:
            list: 方法信息列表
        """
        if not content:
            return []
        
        methods = []
        classes_info = self.code_analyzer.parse_java_file(content)
        package = self.code_analyzer.get_package_name(content)
        
        for cls in classes_info.get('classes', []):
            for m in cls.get('methods', []):
                methods.append({
                    'class': cls.get('name'),
                    'method': m.get('name'),
                    'parameters': m.get('parameters', []),
                    'start_line': m.get('start_line', 0),
                    'end_line': m.get('end_line', 0),
                    'package': package,
                    'file': file_path,
                    'return_type': m.get('return_type'),
                    'modifiers': m.get('modifiers', [])
                })
        return methods
    
    def _find_method_at_line(self, methods: list, line_no: int) -> Optional[dict]:
        """根据行号找到对应的方法
        
        Args:
            methods: 方法列表
            line_no: 行号
            
        Returns:
            dict or None: 找到的方法信息
        """
        for m in methods:
            if m.get('start_line', 0) <= line_no <= m.get('end_line', 0):
                return m
        return None
    
    def _get_method_key(self, method: dict) -> tuple:
        """生成方法的唯一标识key
        
        Args:
            method: 方法信息
            
        Returns:
            tuple: 方法的唯一标识
        """
        return (
            method.get('package', ''),
            method.get('class', ''),
            method.get('method', ''),
            tuple(method.get('parameters', []))
        )
    
    def _find_method_by_key(self, methods: list, key: tuple) -> Optional[dict]:
        """根据方法key在列表中查找方法
        
        Args:
            methods: 方法列表
            key: 方法的唯一标识
            
        Returns:
            dict or None: 找到的方法信息
        """
        for m in methods:
            if self._get_method_key(m) == key:
                return m
        return None
    
    def _is_test_method(self, method: dict) -> bool:
        """判断是否为测试方法"""
        method_name = method.get('method', '') or method.get('method_name', '')
        
        # 检查是否以test开头
        if method_name.lower().startswith('test'):
            return True
        
        # 检查注解（如果有）
        annotations = method.get('annotations', [])
        test_annotations = ['@Test', '@Before', '@After', '@BeforeEach', '@AfterEach']
        for ann in test_annotations:
            if ann in annotations:
                return True
        
        return False
    
    def _process_diff(self, commit_hash: str) -> dict:
        """处理diff，分离源代码和测试代码的diff"""
        commit = self.git_analyzer.repo.commit(commit_hash)
        
        # 获取完整diff
        full_diff = self.git_analyzer.get_full_diff(commit)
        
        # 分离diff
        source_diff, test_diff, stats = self.diff_filter.filter_test_changes(full_diff)
        full_stats = self.diff_filter.extract_changes_info(full_diff, label="完整")
        source_stats = self.diff_filter.extract_changes_info(source_diff, label="源代码")
        test_stats = self.diff_filter.extract_test_changes_info(test_diff)
        
        return {
            'full_diff': full_diff,
            'source_only_diff': source_diff,
            'test_only_diff': test_diff,
            'stats': stats,
            'change_stats': {
                'full': full_stats,
                'source': source_stats,
                'test': test_stats
            }
        }
    
    def _execute_all_versions(self,
                              commit_hash: str,
                              parent_hash: str,
                              diff_info: dict,
                              changed_source_methods: Optional[list] = None,
                              changed_test_methods: Optional[list] = None) -> dict:
        """执行4个版本的构建和测试"""
        if not parent_hash:
            logger.warning(f"Commit {commit_hash[:8]} 没有父commit")
            return {}
        
        executor = IsolatedExecutor(
            repo_path=self.repo_path,
            work_dir=AnalysisConfig.ANALYSIS_WORKTREE_DIR
        )
        
        results = {}
        
        try:
            # 根据配置决定是否并行执行
            if AnalysisConfig.PARALLEL_VERSION_EXECUTION:
                results = self._execute_versions_parallel(
                    executor,
                    commit_hash,
                    parent_hash,
                    diff_info,
                    changed_source_methods,
                    changed_test_methods
                )
            else:
                results = self._execute_versions_sequential(
                    executor,
                    commit_hash,
                    parent_hash,
                    diff_info,
                    changed_source_methods,
                    changed_test_methods
                )
        finally:
            # 确保清理
            executor.cleanup_all()
        
        return results
    
    def _execute_versions_sequential(self, executor: 'IsolatedExecutor',
                                     commit_hash: str, parent_hash: str,
                                     diff_info: dict,
                                     changed_source_methods: Optional[list] = None,
                                     changed_test_methods: Optional[list] = None) -> dict:
        """顺序执行4个版本"""
        results = {}
        
        # V-1: 父commit
        logger.debug(f"  执行 V-1...")
        results['v1'] = executor.execute_version(
            commit_hash=parent_hash,
            version_type='v1',
            changed_source_methods=changed_source_methods,
            changed_test_methods=changed_test_methods
        )
        
        # V-0.5: 父commit + 源代码patch
        logger.debug(f"  执行 V-0.5...")
        results['v05'] = executor.execute_version(
            commit_hash=parent_hash,
            version_type='v05',
            patch_content=diff_info.get('source_only_diff'),
            changed_source_methods=changed_source_methods,
            changed_test_methods=changed_test_methods
        )
        
        # T-0.5: 父commit + 测试代码patch
        logger.debug(f"  执行 T-0.5...")
        results['t05'] = executor.execute_version(
            commit_hash=parent_hash,
            version_type='t05',
            patch_content=diff_info.get('test_only_diff'),
            changed_source_methods=changed_source_methods,
            changed_test_methods=changed_test_methods
        )
        
        # V0: 当前commit
        logger.debug(f"  执行 V0...")
        results['v0'] = executor.execute_version(
            commit_hash=commit_hash,
            version_type='v0',
            changed_source_methods=changed_source_methods,
            changed_test_methods=changed_test_methods
        )
        
        return results
    
    def _execute_versions_parallel(self, executor: 'IsolatedExecutor',
                                   commit_hash: str, parent_hash: str,
                                   diff_info: dict,
                                   changed_source_methods: Optional[list] = None,
                                   changed_test_methods: Optional[list] = None) -> dict:
        """并行执行4个版本"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {
                pool.submit(
                    executor.execute_version,
                    parent_hash, 'v1', None, changed_source_methods, changed_test_methods
                ): 'v1',
                pool.submit(
                    executor.execute_version,
                    parent_hash, 'v05', diff_info.get('source_only_diff'),
                    changed_source_methods, changed_test_methods
                ): 'v05',
                pool.submit(
                    executor.execute_version,
                    parent_hash, 't05', diff_info.get('test_only_diff'),
                    changed_source_methods, changed_test_methods
                ): 't05',
                pool.submit(
                    executor.execute_version,
                    commit_hash, 'v0', None, changed_source_methods, changed_test_methods
                ): 'v0'
            }
            
            for future in futures:
                version = futures[future]
                try:
                    results[version] = future.result(timeout=AnalysisConfig.COMMIT_TIMEOUT)
                except Exception as e:
                    logger.error(f"执行 {version} 失败: {e}")
                    results[version] = {'error': str(e)}
        
        return results
    
    def _classify(self, v1_result: dict, v05_result: dict,
                  t05_result: dict, v0_result: dict) -> dict:
        """对commit进行分类"""
        classifier = CommitClassifier(
            coverage_threshold=AnalysisConfig.COVERAGE_DECREASE_THRESHOLD
        )
        
        return classifier.classify(v1_result, v05_result, t05_result, v0_result)

    def _compute_method_change_stats(self, commit_hash: str, parent_hash: str, file_changes: dict) -> dict:
        """统计方法级别的增删行数（源/测试）"""
        stats = {'source': [], 'test': []}

        if not parent_hash:
            return stats

        commit = self.git_analyzer.repo.commit(commit_hash)

        def _collect_file_stats(file_info, category):
            file_path = file_info.get('path')
            if not file_path or not file_path.endswith('.java'):
                return

            diff_text = self.git_analyzer.get_file_diff(commit, file_path)
            if not diff_text:
                return

            parsed = self.change_detector.parse_diff(diff_text)
            file_changes_list = []
            for entry in parsed:
                if entry.get('file') == file_path:
                    file_changes_list.extend(entry.get('changes', []))

            if not file_changes_list:
                return

            child_content = self.git_analyzer.get_file_content(commit_hash, file_path) or ""
            parent_content = self.git_analyzer.get_file_content(parent_hash, file_path) or ""

            child_classes = self.code_analyzer.parse_java_file(child_content)
            parent_classes = self.code_analyzer.parse_java_file(parent_content)

            child_pkg = self.code_analyzer.get_package_name(child_content)
            parent_pkg = self.code_analyzer.get_package_name(parent_content)

            child_methods = []
            for cls in child_classes.get('classes', []):
                for m in cls.get('methods', []):
                    child_methods.append({
                        'class': cls.get('name'),
                        'method': m.get('name'),
                        'parameters': m.get('parameters', []),
                        'start_line': m.get('start_line', 0),
                        'end_line': m.get('end_line', 0),
                        'package': child_pkg,
                        'file': file_path
                    })

            parent_methods = []
            for cls in parent_classes.get('classes', []):
                for m in cls.get('methods', []):
                    parent_methods.append({
                        'class': cls.get('name'),
                        'method': m.get('name'),
                        'parameters': m.get('parameters', []),
                        'start_line': m.get('start_line', 0),
                        'end_line': m.get('end_line', 0),
                        'package': parent_pkg,
                        'file': file_path
                    })

            def _find_method(methods, line_no):
                for m in methods:
                    if m.get('start_line', 0) <= line_no <= m.get('end_line', 0):
                        return m
                return None

            method_stats = {}

            for change in file_changes_list:
                for line_no in change.get('added_lines', []):
                    m = _find_method(child_methods, line_no)
                    if not m:
                        continue
                    key = (m['package'], m['class'], m['method'], tuple(m.get('parameters', [])), file_path)
                    entry = method_stats.setdefault(key, {
                        'package': m['package'],
                        'class': m['class'],
                        'method': m['method'],
                        'parameters': m.get('parameters', []),
                        'file': file_path,
                        'added_lines': 0,
                        'removed_lines': 0
                    })
                    entry['added_lines'] += 1

                for line_no in change.get('removed_lines', []):
                    m = _find_method(parent_methods, line_no)
                    if not m:
                        continue
                    key = (m['package'], m['class'], m['method'], tuple(m.get('parameters', [])), file_path)
                    entry = method_stats.setdefault(key, {
                        'package': m['package'],
                        'class': m['class'],
                        'method': m['method'],
                        'parameters': m.get('parameters', []),
                        'file': file_path,
                        'added_lines': 0,
                        'removed_lines': 0
                    })
                    entry['removed_lines'] += 1

            for entry in method_stats.values():
                entry['total_changed_lines'] = entry.get('added_lines', 0) + entry.get('removed_lines', 0)
                stats[category].append(entry)

        for file_info in file_changes.get('source_files', []):
            _collect_file_stats(file_info, 'source')
        for file_info in file_changes.get('test_files', []):
            _collect_file_stats(file_info, 'test')

        return stats
