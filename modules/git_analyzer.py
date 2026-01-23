"""
Git分析模块 - 负责提取commits、diff分析等Git操作
"""

import os
from datetime import datetime
from git import Repo, GitCommandError
from config import Config
from utils.logger import get_logger
from utils.exceptions import RepositoryError, GitOperationError

logger = get_logger()


class GitAnalyzer:
    """Git仓库分析器"""
    
    def __init__(self, repo_path):
        """
        初始化Git分析器
        
        Args:
            repo_path: Git仓库路径
        """
        self.repo_path = repo_path
        try:
            self.repo = Repo(repo_path)
            logger.info(f"成功加载Git仓库: {repo_path}")
        except Exception as e:
            logger.error(f"加载Git仓库失败: {e}")
            raise RepositoryError(f"无法加载Git仓库: {repo_path}", {"original_error": str(e)})
    
    def get_all_commits(self, since_date=None, branch='HEAD'):
        """
        获取所有commits
        
        Args:
            since_date: 起始日期（datetime对象）
            branch: 分支名称
            
        Returns:
            list: commit对象列表
        """
        try:
            commits = list(self.repo.iter_commits(branch))
            logger.info(f"共找到 {len(commits)} 个commits")
            
            # 日期过滤
            if since_date:
                commits = [c for c in commits if datetime.fromtimestamp(c.committed_date) >= since_date]
                logger.info(f"日期过滤后剩余 {len(commits)} 个commits")
            
            return commits
        except Exception as e:
            logger.error(f"获取commits失败: {e}")
            return []
    
    def get_commit_info(self, commit):
        """
        获取commit基本信息
        
        Args:
            commit: commit对象
            
        Returns:
            dict: commit信息字典
        """
        try:
            parent_hash = commit.parents[0].hexsha if commit.parents else None
            
            return {
                'commit_hash': commit.hexsha,
                'parent_hash': parent_hash,
                'author': str(commit.author),
                'date': datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M:%S'),
                'message': commit.message.strip()
            }
        except Exception as e:
            logger.error(f"获取commit信息失败 [{commit.hexsha}]: {e}")
            return None
    
    def get_changed_files(self, commit):
        """
        获取commit中变更的文件列表
        
        Args:
            commit: commit对象
            
        Returns:
            dict: {'test_files': [], 'source_files': [], 'other_files': []}
        """
        try:
            if not commit.parents:
                logger.debug(f"Commit {commit.hexsha} 没有父commit，跳过")
                return {'test_files': [], 'source_files': [], 'other_files': []}
            
            parent = commit.parents[0]
            diffs = parent.diff(commit)
            
            test_files = []
            source_files = []
            other_files = []
            
            for diff in diffs:
                # 获取文件路径（新文件或修改的文件）
                file_path = diff.b_path if diff.b_path else diff.a_path
                
                if not file_path or not file_path.endswith('.java'):
                    continue
                
                # 分类文件
                if self._is_test_file(file_path):
                    test_files.append(file_path)
                elif self._is_source_file(file_path):
                    source_files.append(file_path)
                else:
                    other_files.append(file_path)
            
            return {
                'test_files': test_files,
                'source_files': source_files,
                'other_files': other_files
            }
        
        except Exception as e:
            logger.error(f"获取变更文件失败 [{commit.hexsha}]: {e}")
            return {'test_files': [], 'source_files': [], 'other_files': []}
    
    def get_file_diff(self, commit, file_path):
        """
        获取指定文件的diff内容
        
        Args:
            commit: commit对象
            file_path: 文件路径
            
        Returns:
            str: diff文本内容（unified diff格式）
        """
        try:
            if not commit.parents:
                return ""
            
            parent = commit.parents[0]
            
            # 使用git命令生成完整的unified diff格式（包含文件头）
            # 这样unidiff库才能正确解析
            diff_text = self.repo.git.diff(
                parent.hexsha,
                commit.hexsha,
                '--',
                file_path,
                unified=3  # 上下文行数
            )
            
            return diff_text
        
        except Exception as e:
            logger.error(f"获取文件diff失败 [{file_path}]: {e}")
            return ""
    
    def get_file_content(self, commit_hash, file_path):
        """
        获取指定commit中某个文件的内容
        
        Args:
            commit_hash: commit哈希值
            file_path: 文件路径
            
        Returns:
            str: 文件内容
        """
        try:
            commit = self.repo.commit(commit_hash)
            blob = commit.tree / file_path
            return blob.data_stream.read().decode('utf-8', errors='ignore')
        except Exception as e:
            logger.debug(f"获取文件内容失败 [{commit_hash}:{file_path}]: {e}")
            return None
    
    def create_worktree(self, commit_hash, worktree_path):
        """
        创建临时worktree
        
        Args:
            commit_hash: commit哈希值
            worktree_path: worktree路径
            
        Returns:
            bool: 是否成功
        """
        try:
            # 删除已存在的worktree路径
            if os.path.exists(worktree_path):
                self.remove_worktree(worktree_path)
            
            # 创建worktree
            self.repo.git.worktree('add', worktree_path, commit_hash)
            logger.debug(f"创建worktree: {worktree_path} @ {commit_hash[:8]}")
            return True
        
        except Exception as e:
            logger.error(f"创建worktree失败 [{commit_hash}]: {e}")
            return False
    
    def remove_worktree(self, worktree_path):
        """
        删除worktree
        
        Args:
            worktree_path: worktree路径
            
        Returns:
            bool: 是否成功
        """
        try:
            if os.path.exists(worktree_path):
                self.repo.git.worktree('remove', worktree_path, '--force')
                logger.debug(f"删除worktree: {worktree_path}")
            return True
        
        except Exception as e:
            logger.error(f"删除worktree失败 [{worktree_path}]: {e}")
            return False
    
    def _is_test_file(self, file_path):
        """判断是否为测试文件"""
        return any(pattern in file_path for pattern in Config.TEST_PATH_PATTERNS)
    
    def _is_source_file(self, file_path):
        """判断是否为源代码文件"""
        return any(pattern in file_path for pattern in Config.SOURCE_PATH_PATTERNS)
