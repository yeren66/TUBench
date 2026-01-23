"""
Commit过滤器 - 负责应用各种过滤条件
"""

from utils.logger import get_logger

logger = get_logger()


class CommitFilter:
    """Commit过滤器"""
    
    def __init__(self):
        """初始化过滤器"""
        pass
    
    def filter_by_file_changes(self, changed_files):
        """
        基于文件变更过滤：必须同时修改测试文件和源代码文件
        
        Args:
            changed_files: 变更文件字典 {'test_files': [], 'source_files': []}
            
        Returns:
            bool: 是否通过过滤
        """
        has_test_changes = len(changed_files.get('test_files', [])) > 0
        has_source_changes = len(changed_files.get('source_files', [])) > 0
        
        passed = has_test_changes and has_source_changes
        
        if not passed:
            reason = []
            if not has_test_changes:
                reason.append("无测试文件变更")
            if not has_source_changes:
                reason.append("无源代码文件变更")
            logger.debug(f"过滤: {', '.join(reason)}")
        
        return passed
    
    def filter_by_build_status(self, build_status):
        """
        基于构建状态过滤：父commit和子commit都必须能够成功构建
        
        Args:
            build_status: 构建状态字典 {'parent_success': bool, 'child_success': bool}
            
        Returns:
            bool: 是否通过过滤
        """
        parent_ok = build_status.get('parent_success', False)
        child_ok = build_status.get('child_success', False)
        
        passed = parent_ok and child_ok
        
        if not passed:
            reasons = []
            if not parent_ok:
                reasons.append("父commit构建失败")
            if not child_ok:
                reasons.append("子commit构建失败")
            logger.debug(f"过滤: {', '.join(reasons)}")
        
        return passed
    
    def filter_by_coverage_threshold(self, coverage_analysis, threshold=0.5):
        """
        基于覆盖率阈值过滤：至少threshold比例的测试需要覆盖变更的被测方法
        
        Args:
            coverage_analysis: 覆盖率分析结果
            threshold: 覆盖率阈值 (默认0.5，即50%)
            
        Returns:
            bool: 是否通过过滤
        """
        # 检查父commit和子commit的覆盖情况
        parent_coverage = coverage_analysis.get('parent_commit', {})
        child_coverage = coverage_analysis.get('child_commit', {})
        
        parent_ratio = parent_coverage.get('coverage_ratio', 0.0)
        child_ratio = child_coverage.get('coverage_ratio', 0.0)
        
        # 任一版本达到阈值即可
        passed = parent_ratio >= threshold or child_ratio >= threshold
        
        if not passed:
            logger.debug(f"过滤: 覆盖率不足 (parent: {parent_ratio:.2%}, child: {child_ratio:.2%}, threshold: {threshold:.2%})")
        
        return passed
    
    def filter_by_method_changes(self, changed_methods):
        """
        基于方法变更过滤：必须有明确的测试方法和被测方法变更
        
        Args:
            changed_methods: 变更方法字典 {'test_methods': [], 'source_methods': []}
            
        Returns:
            bool: 是否通过过滤
        """
        has_test_method_changes = len(changed_methods.get('test_methods', [])) > 0
        has_source_method_changes = len(changed_methods.get('source_methods', [])) > 0
        
        passed = has_test_method_changes and has_source_method_changes
        
        if not passed:
            reasons = []
            if not has_test_method_changes:
                reasons.append("无测试方法变更")
            if not has_source_method_changes:
                reasons.append("无被测方法变更")
            logger.debug(f"过滤: {', '.join(reasons)}")
        
        return passed
    
    def apply_all_filters(self, commit_info, threshold=0.5):
        """
        应用所有过滤条件
        
        Args:
            commit_info: commit信息字典
            threshold: 覆盖率阈值
            
        Returns:
            tuple: (passed: bool, reasons: list)
        """
        reasons = []
        
        # 1. 文件变更过滤
        if not self.filter_by_file_changes(commit_info.get('changed_files', {})):
            reasons.append("文件变更不符合要求")
        
        # 2. 方法变更过滤
        if not self.filter_by_method_changes(commit_info.get('changed_methods', {})):
            reasons.append("方法变更不符合要求")
        
        # 3. 构建状态过滤
        if not self.filter_by_build_status(commit_info.get('build_status', {})):
            reasons.append("构建失败")
        
        # 4. 覆盖率过滤
        if not self.filter_by_coverage_threshold(commit_info.get('coverage_analysis', {}), threshold):
            reasons.append("覆盖率不足")
        
        passed = len(reasons) == 0
        
        return passed, reasons
