"""
隔离执行器 - 在临时worktree中执行构建和测试，不污染原始仓库
使用方案B：临时worktree + patch应用，分析完即删除
"""

import os
import shutil
import subprocess
import tempfile
import threading
from datetime import datetime
from typing import Optional, Dict, Any

from git import Repo, GitCommandError
from config import Config, AnalysisConfig
from utils.logger import get_logger
from modules.maven_executor import MavenExecutor
from modules.coverage_analyzer import CoverageAnalyzer
from modules.code_analyzer import CodeAnalyzer

logger = get_logger()


class IsolatedExecutor:
    """隔离执行器 - 确保不污染原始仓库"""
    
    def __init__(self, repo_path: str, work_dir: str = None):
        """
        初始化隔离执行器
        
        Args:
            repo_path: 原始仓库路径
            work_dir: 工作目录，默认为临时目录
        """
        self.repo_path = repo_path
        self.project_name = os.path.basename(repo_path)
        
        # 线程本地存储，为每个线程创建独立的 Repo 实例
        self._thread_local = threading.local()
        
        # Work directory (isolate by PID to avoid cross-process cleanup collisions)
        base_dir = work_dir or AnalysisConfig.ANALYSIS_WORKTREE_DIR
        self.work_dir = os.path.join(base_dir, f"{self.project_name}_{os.getpid()}")
        os.makedirs(self.work_dir, exist_ok=True)
        
        # 记录创建的worktree，用于清理（需要线程安全）
        self._created_worktrees = []
        self._worktrees_lock = threading.Lock()
        
        # 覆盖率分析器
        self.coverage_analyzer = CoverageAnalyzer()
    
    @property
    def repo(self) -> Repo:
        """获取当前线程的 Repo 实例（线程安全）"""
        if not hasattr(self._thread_local, 'repo'):
            self._thread_local.repo = Repo(self.repo_path)
        return self._thread_local.repo
    
    def execute_version(self,
                       commit_hash: str,
                       version_type: str,
                       patch_content: str = None,
                       changed_source_methods: Optional[list] = None,
                       changed_test_methods: Optional[list] = None) -> Dict[str, Any]:
        """
        在隔离环境中执行指定版本
        
        Args:
            commit_hash: 基础commit hash（对于v05/t05是parent_hash）
            version_type: 版本类型 ('v1', 'v05', 't05', 'v0')
            patch_content: 需要应用的patch（v05和t05需要）
            
        Returns:
            执行结果字典
        """
        result = {
            'version': version_type,
            'commit_used': commit_hash,
            'build': {'success': False},
            'test': {'success': False},
            'coverage': {'available': False}
        }
        
        # 生成worktree路径
        worktree_path = self._get_worktree_path(commit_hash, version_type)
        
        try:
            # 1. 创建worktree
            if not self._create_worktree(commit_hash, worktree_path):
                result['build']['error_message'] = "Failed to create worktree"
                return result
            
            result['worktree_path'] = worktree_path
            
            # 2. 应用patch（如果需要）
            if patch_content and version_type in ('v05', 't05'):
                patch_result = self._apply_patch(patch_content, worktree_path)
                result['patch_applied'] = patch_result['success']
                
                if not patch_result['success']:
                    result['build']['error_message'] = f"Failed to apply patch: {patch_result.get('error')}"
                    return result
            
            # 3. 执行编译
            build_result = self._run_maven_compile(worktree_path)
            result['build'] = build_result
            
            if not build_result['success']:
                return result
            
            # 4. 执行测试
            test_result = self._run_maven_test(worktree_path, changed_test_methods)
            result['test'] = test_result
            
            # 5. 收集覆盖率（无论测试是否成功都尝试收集）
            if build_result['success']:
                coverage_result = self._collect_coverage(
                    worktree_path,
                    changed_source_methods=changed_source_methods,
                    changed_test_methods=changed_test_methods
                )
                result['coverage'] = coverage_result
            
        except Exception as e:
            logger.error(f"执行版本 {version_type} 失败: {e}")
            result['error'] = str(e)
        
        finally:
            # 清理worktree
            self._cleanup_worktree(worktree_path)
        
        return result
    
    def _get_worktree_path(self, commit_hash: str, version_type: str) -> str:
        """生成worktree路径"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        return os.path.join(
            self.work_dir,
            f"{self.project_name}_{commit_hash[:8]}_{version_type}_{timestamp}"
        )
    
    def _create_worktree(self, commit_hash: str, worktree_path: str) -> bool:
        """创建git worktree"""
        try:
            # 确保路径不存在
            if os.path.exists(worktree_path):
                shutil.rmtree(worktree_path)
            
            # 创建worktree
            self.repo.git.worktree('add', '--detach', worktree_path, commit_hash)
            
            with self._worktrees_lock:
                self._created_worktrees.append(worktree_path)
            logger.debug(f"创建worktree: {worktree_path}")
            return True
            
        except GitCommandError as e:
            logger.error(f"创建worktree失败: {e}")
            return False
    
    def _apply_patch(self, patch_content: str, worktree_path: str) -> Dict[str, Any]:
        """应用patch到worktree"""
        result = {'success': False}
        
        if not patch_content or not patch_content.strip():
            result['success'] = True
            result['message'] = "Empty patch, nothing to apply"
            return result
        
        try:
            # 将patch写入临时文件
            patch_file = os.path.join(worktree_path, '.tubench_patch.diff')
            with open(patch_file, 'w', encoding='utf-8') as f:
                f.write(patch_content)
            
            # 应用patch
            process = subprocess.run(
                ['git', 'apply', '--verbose', patch_file],
                cwd=worktree_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # 清理patch文件
            os.remove(patch_file)
            
            if process.returncode == 0:
                result['success'] = True
                result['output'] = process.stdout
            else:
                # 尝试使用 --3way 选项
                process2 = subprocess.run(
                    ['git', 'apply', '--3way', patch_file] if os.path.exists(patch_file) else
                    ['echo', patch_content, '|', 'git', 'apply', '--3way'],
                    cwd=worktree_path,
                    capture_output=True,
                    text=True,
                    shell=True,
                    timeout=60
                )
                
                if process2.returncode == 0:
                    result['success'] = True
                else:
                    result['error'] = process.stderr or process2.stderr
                    logger.debug(f"Patch应用失败: {result['error']}")
            
        except subprocess.TimeoutExpired:
            result['error'] = "Patch application timed out"
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _run_maven_compile(self, worktree_path: str) -> Dict[str, Any]:
        """执行Maven编译"""
        result = {
            'success': False,
            'duration_seconds': 0,
            'command': 'mvn compile -DskipTests'
        }
        
        start_time = datetime.now()
        
        try:
            # 检查pom.xml是否存在
            pom_path = os.path.join(worktree_path, 'pom.xml')
            if not os.path.exists(pom_path):
                result['error_message'] = "pom.xml not found"
                return result
            
            # 执行编译
            process = subprocess.run(
                ['mvn', 'compile', '-DskipTests', '-B', '-q'],
                cwd=worktree_path,
                capture_output=True,
                text=True,
                timeout=AnalysisConfig.COMPILE_TIMEOUT
            )
            
            result['return_code'] = process.returncode
            result['stdout'] = process.stdout[-5000:] if len(process.stdout) > 5000 else process.stdout
            result['stderr'] = process.stderr[-5000:] if len(process.stderr) > 5000 else process.stderr
            
            if process.returncode == 0:
                result['success'] = True
            else:
                result['error_message'] = self._extract_compile_error(process.stderr or process.stdout)
                result['compile_errors'] = self._parse_compile_errors(process.stderr or process.stdout)
                
        except subprocess.TimeoutExpired:
            result['error_message'] = f"Compilation timed out after {AnalysisConfig.COMPILE_TIMEOUT}s"
        except Exception as e:
            result['error_message'] = str(e)
        
        result['duration_seconds'] = (datetime.now() - start_time).total_seconds()
        return result
    
    def _run_maven_test(self, worktree_path: str, changed_test_methods: Optional[list] = None) -> Dict[str, Any]:
        """执行Maven测试并收集覆盖率"""
        result = {
            'success': False,
            'duration_seconds': 0,
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0,
            'failed_tests': [],
            'error_tests': []
        }
        result['selection_skipped'] = False
        
        start_time = datetime.now()
        
        try:
            # 使用JaCoCo运行测试
            maven_executor = MavenExecutor(worktree_path)
            selected_tests = self._build_test_selectors(worktree_path, changed_test_methods)
            if changed_test_methods is not None and not selected_tests:
                result['success'] = True
                result['selection_skipped'] = True
                result['error_message'] = "No changed tests identified"
                result['selected_tests'] = []
                return result

            test_result = maven_executor.test_with_jacoco(selected_tests=selected_tests)
            
            result['success'] = test_result.get('success', False)
            result['return_code'] = test_result.get('return_code', -1)
            result['stdout'] = test_result.get('stdout', '')[-5000:]
            result['stderr'] = test_result.get('stderr', '')[-5000:]
            result['selected_tests'] = selected_tests
            
            # 解析测试结果
            if test_result.get('success') or 'Tests run:' in str(test_result.get('stdout', '')):
                test_summary = self._parse_test_summary(test_result.get('stdout', ''))
                result.update(test_summary)
            
            # 如果测试失败，解析失败的测试
            if not result['success']:
                failed_tests = self._parse_failed_tests(worktree_path)
                result['failed_tests'] = failed_tests
                
        except subprocess.TimeoutExpired:
            result['error_message'] = f"Test timed out after {AnalysisConfig.TEST_TIMEOUT}s"
        except Exception as e:
            result['error_message'] = str(e)
        
        result['duration_seconds'] = (datetime.now() - start_time).total_seconds()
        return result

    def _build_test_selectors(self, worktree_path: str, changed_test_methods: Optional[list]) -> list:
        """构建Maven Surefire测试选择器列表"""
        if not changed_test_methods:
            return []

        class_methods = {}
        class_only = set()
        resolved = self._resolve_changed_methods(worktree_path, changed_test_methods)
        resolved_keys = {
            (m.get('file'), m.get('class'), m.get('method'))
            for m in resolved
        }
        use_resolved = len(resolved_keys) > 0

        for method in changed_test_methods:
            class_name = method.get('class')
            package = method.get('package')
            method_name = method.get('method')
            is_test = method.get('is_test_method', False)
            file_path = method.get('file')

            if not class_name:
                continue

            if file_path:
                abs_path = os.path.join(worktree_path, file_path)
                if not os.path.exists(abs_path):
                    continue

            if use_resolved and (file_path, class_name, method_name) not in resolved_keys:
                continue

            fqcn = f"{package}.{class_name}" if package else class_name

            if is_test and method_name:
                class_methods.setdefault(fqcn, set()).add(method_name)
            else:
                class_only.add(fqcn)

        selectors = []
        for fqcn, methods in class_methods.items():
            if methods:
                selector = f"{fqcn}#" + "+".join(sorted(methods))
                selectors.append(selector)

        for fqcn in sorted(class_only):
            if fqcn not in class_methods:
                selectors.append(fqcn)

        return selectors
    
    def _collect_coverage(self,
                          worktree_path: str,
                          changed_source_methods: Optional[list] = None,
                          changed_test_methods: Optional[list] = None) -> Dict[str, Any]:
        """收集覆盖率信息"""
        result = {'available': False}
        
        try:
            jacoco_report = os.path.join(worktree_path, Config.JACOCO_REPORT_PATH)
            
            if os.path.exists(jacoco_report):
                coverage_data = self.coverage_analyzer.parse_jacoco_report(jacoco_report)
                
                if coverage_data:
                    result['available'] = True
                    result['jacoco_report_path'] = jacoco_report
                    # 变更方法覆盖率（更敏感的指标）
                    if changed_source_methods:
                        resolved_methods = self._resolve_changed_methods(
                            worktree_path,
                            changed_source_methods
                        )
                        method_coverage = self.coverage_analyzer.analyze_test_coverage_for_changes(
                            coverage_data,
                            changed_test_methods or [],
                            resolved_methods
                        )
                        result['method_coverage'] = method_coverage

                        method_line_coverage = self.coverage_analyzer.analyze_changed_methods_line_coverage(
                            coverage_data,
                            resolved_methods
                        )
                        result['method_line_coverage'] = method_line_coverage

                        method_branch_coverage = self.coverage_analyzer.analyze_changed_methods_branch_coverage(
                            coverage_data,
                            resolved_methods
                        )
                        result['method_branch_coverage'] = method_branch_coverage

        except Exception as e:
            logger.debug(f"收集覆盖率失败: {e}")
            result['error'] = str(e)
        
        return result

    def _resolve_changed_methods(self, worktree_path: str, changed_methods: list) -> list:
        """在指定版本的工作区内重新定位变更方法的起止行"""
        if not changed_methods:
            return []

        code_analyzer = CodeAnalyzer()
        resolved = []
        parsed_cache = {}

        for method in changed_methods:
            file_rel_path = method.get('file')
            if not file_rel_path:
                continue

            file_path = os.path.join(worktree_path, file_rel_path)
            if not os.path.exists(file_path):
                continue

            if file_path not in parsed_cache:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    parsed_cache[file_path] = code_analyzer.parse_java_file(content)
                except Exception:
                    parsed_cache[file_path] = {'classes': []}

            classes_info = parsed_cache[file_path]
            class_name = method.get('class')
            method_name = method.get('method')
            parameters = method.get('parameters', [])

            class_methods = []
            for class_info in classes_info.get('classes', []):
                if class_info.get('name') == class_name:
                    class_methods = class_info.get('methods', [])
                    break

            if not class_methods:
                continue

            candidates = [m for m in class_methods if m.get('name') == method_name]
            if not candidates:
                continue

            chosen = None
            if parameters:
                exact = [m for m in candidates if m.get('parameters', []) == parameters]
                if exact:
                    chosen = exact[0]
                else:
                    param_count = len(parameters)
                    by_count = [m for m in candidates if len(m.get('parameters', [])) == param_count]
                    chosen = by_count[0] if by_count else candidates[0]
            else:
                chosen = candidates[0]

            if not chosen:
                continue

            resolved.append({
                'class': class_name,
                'method': method_name,
                'parameters': chosen.get('parameters', parameters),
                'start_line': chosen.get('start_line', 0),
                'end_line': chosen.get('end_line', 0),
                'file': file_rel_path,
                'package': method.get('package', '')
            })

        return resolved
    
    def _extract_compile_error(self, output: str) -> str:
        """提取编译错误信息"""
        lines = output.split('\n')
        error_lines = []
        
        for line in lines:
            if '[ERROR]' in line or 'error:' in line.lower():
                error_lines.append(line.strip())
        
        if error_lines:
            return '\n'.join(error_lines[:10])
        return "Compilation failed"
    
    def _parse_compile_errors(self, output: str) -> list:
        """解析编译错误详情"""
        errors = []
        lines = output.split('\n')
        
        for i, line in enumerate(lines):
            if '.java:' in line and ('error:' in line.lower() or '[ERROR]' in line):
                try:
                    # 尝试提取文件名和行号
                    parts = line.split('.java:')
                    if len(parts) >= 2:
                        file_part = parts[0].split('/')[-1] + '.java'
                        rest = parts[1]
                        
                        # 尝试提取行号
                        line_num = None
                        if ':' in rest:
                            try:
                                line_num = int(rest.split(':')[0].strip().strip('[').strip(']'))
                            except:
                                pass
                        
                        errors.append({
                            'file': file_part,
                            'line': line_num,
                            'message': line.strip()
                        })
                except:
                    pass
        
        return errors[:10]  # 最多返回10个错误
    
    def _parse_test_summary(self, output: str) -> dict:
        """解析测试摘要"""
        result = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0
        }
        
        import re
        
        # 查找 "Tests run: X, Failures: Y, Errors: Z, Skipped: W"
        pattern = r'Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+),\s*Skipped:\s*(\d+)'
        matches = re.findall(pattern, output)
        
        if matches:
            # 汇总所有匹配（可能有多个测试类）
            for match in matches:
                result['total_tests'] += int(match[0])
                result['failed'] += int(match[1])
                result['errors'] += int(match[2])
                result['skipped'] += int(match[3])
            
            result['passed'] = result['total_tests'] - result['failed'] - result['errors'] - result['skipped']
        
        return result
    
    def _parse_failed_tests(self, worktree_path: str) -> list:
        """解析失败的测试"""
        failed_tests = []
        
        # 尝试从surefire报告解析
        surefire_dir = os.path.join(worktree_path, 'target', 'surefire-reports')
        
        if os.path.exists(surefire_dir):
            import xml.etree.ElementTree as ET
            
            for filename in os.listdir(surefire_dir):
                if filename.startswith('TEST-') and filename.endswith('.xml'):
                    try:
                        filepath = os.path.join(surefire_dir, filename)
                        tree = ET.parse(filepath)
                        root = tree.getroot()
                        
                        for testcase in root.findall('.//testcase'):
                            failure = testcase.find('failure')
                            error = testcase.find('error')
                            
                            if failure is not None or error is not None:
                                elem = failure if failure is not None else error
                                failed_tests.append({
                                    'class': testcase.get('classname'),
                                    'method': testcase.get('name'),
                                    'full_name': f"{testcase.get('classname')}.{testcase.get('name')}",
                                    'failure_type': elem.get('type'),
                                    'message': elem.get('message', '')[:500],
                                    'stack_trace': (elem.text or '')[:1000]
                                })
                    except Exception as e:
                        logger.debug(f"解析测试报告失败 {filename}: {e}")
        
        return failed_tests[:50]  # 最多返回50个
    
    def _cleanup_worktree(self, worktree_path: str):
        """清理worktree"""
        try:
            if os.path.exists(worktree_path):
                # 先尝试用git命令删除
                try:
                    self.repo.git.worktree('remove', '--force', worktree_path)
                except:
                    pass
                
                # 如果还存在，强制删除目录
                if os.path.exists(worktree_path):
                    shutil.rmtree(worktree_path, ignore_errors=True)
                
                logger.debug(f"清理worktree: {worktree_path}")
                
                with self._worktrees_lock:
                    if worktree_path in self._created_worktrees:
                        self._created_worktrees.remove(worktree_path)
                    
        except Exception as e:
            logger.warning(f"清理worktree失败 {worktree_path}: {e}")
    
    def cleanup_all(self):
        """清理所有创建的worktree"""
        # 清理记录的worktree（获取副本以避免并发修改）
        with self._worktrees_lock:
            worktrees_copy = list(self._created_worktrees)
        for worktree_path in worktrees_copy:
            self._cleanup_worktree(worktree_path)
        
        # 清理可能遗留的worktree
        try:
            # 获取所有worktree
            output = self.repo.git.worktree('list', '--porcelain')
            
            for line in output.split('\n'):
                if line.startswith('worktree '):
                    path = line.replace('worktree ', '').strip()
                    # 只清理我们创建的临时worktree
                    if self.work_dir in path and self.project_name in path:
                        self._cleanup_worktree(path)
        except Exception as e:
            logger.debug(f"清理遗留worktree失败: {e}")
        
        # 执行git worktree prune
        try:
            self.repo.git.worktree('prune')
        except:
            pass
