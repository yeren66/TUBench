"""
过滤版本生成器 - 负责生成隐藏测试变更的V-0.5版本
"""

import os
import tempfile
from git import GitCommandError
from config import Config
from utils.logger import get_logger
from .diff_filter import DiffFilter

logger = get_logger()


class FilteredVersionGenerator:
    """过滤版本生成器 - 生成仅源代码/仅测试代码变更的版本"""
    
    MODE_SOURCE_ONLY = "source_only"
    MODE_TEST_ONLY = "test_only"
    
    def __init__(self, git_analyzer):
        """
        初始化过滤版本生成器
        
        Args:
            git_analyzer: GitAnalyzer实例
        """
        self.git_analyzer = git_analyzer
        self.diff_filter = DiffFilter()
        self.repo = git_analyzer.repo
    
    def generate_filtered_version(self, commit_info):
        """
        生成过滤后的版本 (V-0.5，仅源代码变更)
        """
        result = self._generate_version(commit_info, mode=self.MODE_SOURCE_ONLY)
        return {
            'success': result['success'],
            'filtered_commit_hash': result.get('commit_hash'),
            'branch_name': result.get('branch_name'),
            'test_changes_hidden': result.get('hidden_changes', {}),
            'stats': result.get('stats', {}),
            'error': result.get('error')
        }
    
    def generate_test_only_version(self, commit_info):
        """
        生成测试变更版本 (T-0.5，仅测试代码变更)
        """
        result = self._generate_version(commit_info, mode=self.MODE_TEST_ONLY)
        return {
            'success': result['success'],
            'test_only_commit_hash': result.get('commit_hash'),
            'branch_name': result.get('branch_name'),
            'source_changes_hidden': result.get('hidden_changes', {}),
            'stats': result.get('stats', {}),
            'error': result.get('error')
        }
    
    def _generate_version(self, commit_info, mode):
        """
        生成指定模式的版本
        
        Args:
            commit_info: commit信息字典
            mode: 生成模式 (source_only/test_only)
            
        Returns:
            dict: {
                'success': bool,
                'commit_hash': str,
                'branch_name': str,
                'hidden_changes': dict,
                'stats': dict,
                'error': str
            }
        """
        result = {
            'success': False,
            'commit_hash': None,
            'branch_name': None,
            'hidden_changes': {},
            'stats': {},
            'error': None
        }
        
        try:
            commit_hash = commit_info['commit_hash']
            parent_hash = commit_info['parent_hash']
            
            if not parent_hash:
                result['error'] = "没有父commit，无法生成版本"
                return result
            
            if mode not in (self.MODE_SOURCE_ONLY, self.MODE_TEST_ONLY):
                result['error'] = f"未知生成模式: {mode}"
                return result
            
            # 1. 获取完整的diff (使用git命令获取标准格式)
            try:
                diff_text = self.repo.git.diff(parent_hash, commit_hash)
            except Exception as e:
                logger.error(f"获取diff失败: {e}")
                result['error'] = f"获取diff失败: {e}"
                return result
            
            # 2. 过滤diff，分离源代码和测试代码变更
            filtered_diff, test_diff, filter_stats = self.diff_filter.filter_test_changes(diff_text)
            selected_diff, hidden_diff = self._select_diff(filtered_diff, test_diff, mode)
            
            if not selected_diff:
                result['error'] = "选定的diff为空，无法生成版本"
                return result
            
            # 3. 获取原始commit的完整message
            original_commit = self.repo.commit(commit_hash)
            original_message = original_commit.message.strip()
            
            # 4. 创建新分支并应用diff
            branch_name = self._build_branch_name(commit_hash, mode)
            commit_message = self._build_commit_message(original_message, mode)
            new_hash = self._apply_diff_to_branch(
                parent_hash,
                selected_diff,
                branch_name,
                commit_message
            )
            
            if not new_hash:
                result['error'] = "应用diff失败"
                return result
            
            # 5. 验证可编译性
            if not self._verify_compilable(new_hash):
                result['error'] = "生成的版本无法编译"
                # 清理分支
                self._cleanup_branch(branch_name)
                return result
            
            # 6. 提取被隐藏的变更信息
            hidden_changes_info = self.diff_filter.extract_changes_info(hidden_diff)
            
            # 7. 返回成功结果
            result['success'] = True
            result['commit_hash'] = new_hash
            result['branch_name'] = branch_name
            result['hidden_changes'] = hidden_changes_info
            result['stats'] = filter_stats
            
            logger.info(f"成功生成版本: {new_hash[:8]} (分支: {branch_name}, 模式: {mode})")
            
        except Exception as e:
            logger.error(f"生成版本失败 [{commit_info.get('commit_hash', 'unknown')[:8]}]: {e}")
            result['error'] = str(e)
        
        return result
    
    def _apply_diff_to_branch(self, parent_hash, diff_text, branch_name, commit_message):
        """
        应用diff到新分支
        
        Args:
            parent_hash: 父commit的hash
            diff_text: diff文本
            branch_name: 新分支名称
            commit_message: commit message
            
        Returns:
            str: 新commit的hash，失败返回None
        """
        try:
            # 1. 彻底清理工作区，确保完全干净的状态
            logger.debug(f"清理工作区...")
            self.repo.git.reset('--hard', 'HEAD')
            self.repo.git.clean('-fd')  # 删除未跟踪的文件和目录
            
            # 2. 删除已存在的同名分支
            try:
                self.repo.git.branch('-D', branch_name)
                logger.debug(f"已删除旧分支: {branch_name}")
            except GitCommandError:
                pass  # 分支不存在，忽略
            
            # 3. 从父commit创建新分支
            self.repo.git.checkout('-b', branch_name, parent_hash)
            
            # 4. 再次确保分支状态干净（移除可能的target/等编译产物）
            self.repo.git.reset('--hard', parent_hash)
            self.repo.git.clean('-fd')
            logger.debug(f"已创建并清理分支: {branch_name}")
            
            # 将diff保存到临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False) as f:
                f.write(diff_text)
                patch_file = f.name
            
            try:
                # 应用patch
                self.repo.git.apply(patch_file, '--whitespace=nowarn')
                
                # 添加变更到暂存区
                self.repo.git.add('-A')
                
                # 检查是否有变更需要提交
                if self.repo.is_dirty():
                    self.repo.git.commit('-m', commit_message)
                    
                    # 获取新commit的hash
                    new_commit_hash = self.repo.head.commit.hexsha
                    
                    logger.debug(f"成功应用filtered diff，新commit: {new_commit_hash[:8]}")
                    return new_commit_hash
                else:
                    logger.warning("应用patch后没有变更")
                    return None
                
            finally:
                # 清理临时文件
                if os.path.exists(patch_file):
                    os.remove(patch_file)
        
        except GitCommandError as e:
            logger.error(f"应用diff失败: {e}")
            return None
        
        except Exception as e:
            logger.error(f"应用diff异常: {e}")
            return None

    def _select_diff(self, filtered_diff, test_diff, mode):
        """
        根据模式选择需要应用的diff以及隐藏的diff
        """
        if mode == self.MODE_SOURCE_ONLY:
            return filtered_diff, test_diff
        if mode == self.MODE_TEST_ONLY:
            return test_diff, filtered_diff
        return "", ""
    
    def _build_branch_name(self, commit_hash, mode):
        """
        构建分支名称
        """
        prefix = "filtered" if mode == self.MODE_SOURCE_ONLY else "test-only"
        return f"{prefix}/{commit_hash[:8]}"
    
    def _build_commit_message(self, original_message, mode):
        """
        构建提交信息
        """
        if mode == self.MODE_SOURCE_ONLY:
            suffix = "[Filtered Version - Source Code Changes Only]"
        else:
            suffix = "[Test-Only Version - Test Code Changes Only]"
        return f"{original_message}\n\n{suffix}"
    
    def _verify_compilable(self, commit_hash):
        """
        验证指定commit是否可编译
        
        Args:
            commit_hash: commit的hash
            
        Returns:
            bool: 是否可编译
        """
        try:
            # 切换到该commit并确保工作区干净
            self.repo.git.checkout(commit_hash)
            self.repo.git.reset('--hard')
            self.repo.git.clean('-fd')  # 清理编译前的状态
            
            # 确保工作区干净
            self.repo.git.reset('--hard', commit_hash)
            self.repo.git.clean('-fd')
            
            # 检查是否有pom.xml
            pom_path = os.path.join(self.repo.working_dir, 'pom.xml')
            if not os.path.exists(pom_path):
                logger.warning(f"未找到pom.xml，跳过编译验证")
                return True  # 假设可以编译
            
            # 尝试编译
            from .maven_executor import MavenExecutor
            maven = MavenExecutor(self.repo.working_dir)
            success, _ = maven._run_maven_command('clean compile -DskipTests')
            
            # 编译验证后，清理编译产物，确保分支干净
            if success:
                logger.debug("编译成功，清理编译产物...")
                target_dir = os.path.join(self.repo.working_dir, 'target')
                if os.path.exists(target_dir):
                    import shutil
                    shutil.rmtree(target_dir)
                    logger.debug(f"已删除target目录")
            
            return success
        
        except Exception as e:
            logger.error(f"验证编译失败: {e}")
            return False
    
    def _cleanup_branch(self, branch_name):
        """
        清理创建的分支
        
        Args:
            branch_name: 分支名称
        """
        try:
            # 切换回主分支
            self.repo.git.checkout('HEAD', '--detach')
            # 删除分支
            self.repo.git.branch('-D', branch_name)
            logger.debug(f"已清理分支: {branch_name}")
        except Exception as e:
            logger.warning(f"清理分支失败 [{branch_name}]: {e}")
    
    def restore_original_branch(self):
        """恢复到原始分支/状态"""
        try:
            # 切换回HEAD
            self.repo.git.checkout('HEAD', '--detach')
            logger.debug("已恢复到原始状态")
        except Exception as e:
            logger.warning(f"恢复原始状态失败: {e}")
