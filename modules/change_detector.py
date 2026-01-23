"""
变更检测模块 - 负责分析diff并识别具体变更的方法
使用正则表达式解析diff，与diff_filter.py保持一致
"""

import re
from utils.logger import get_logger

logger = get_logger()


class ChangeDetector:
    """代码变更检测器"""
    
    def __init__(self):
        """初始化变更检测器"""
        pass
    
    def parse_diff(self, diff_text):
        """
        解析diff文本
        
        Args:
            diff_text: diff文本内容
            
        Returns:
            list: 变更信息列表 [{'file': str, 'changes': [{'type': str, 'start': int, 'end': int}]}]
        """
        try:
            if not diff_text:
                return []
            
            file_diffs = self._split_diff_by_file(diff_text)
            changes = []
            
            for file_diff, file_path in file_diffs:
                file_changes = {
                    'file': file_path,
                    'changes': []
                }
                
                # 解析hunks
                hunks = self._parse_hunks(file_diff)
                for hunk in hunks:
                    change_info = {
                        'type': 'modified',
                        'added_lines': hunk['added_lines'],
                        'removed_lines': hunk['removed_lines'],
                        'start_line': hunk['target_start'],
                        'end_line': hunk['target_start'] + hunk['target_length']
                    }
                    file_changes['changes'].append(change_info)
                
                changes.append(file_changes)
            
            return changes
        
        except Exception as e:
            logger.error(f"解析diff失败: {e}")
            return []
    
    def _split_diff_by_file(self, diff_text):
        """
        按文件分割diff文本
        
        Args:
            diff_text: 完整的diff文本
            
        Returns:
            list: [(file_diff, file_path), ...]
        """
        file_diffs = []
        
        # 分割diff文本
        parts = re.split(r'(diff --git [^\n]+\n)', diff_text)
        
        current_diff = []
        current_path = None
        
        for part in parts:
            if not part:
                continue
                
            if part.startswith('diff --git'):
                # 保存前一个文件的diff
                if current_diff and current_path:
                    file_diffs.append(("\n".join(current_diff), current_path))
                
                # 开始新的文件diff
                current_diff = [part.strip()]
                
                # 提取文件路径
                match = re.search(r'diff --git a/(.*?) b/', part)
                if match:
                    current_path = match.group(1)
                else:
                    current_path = None
            else:
                # 添加到当前文件的diff
                if part.strip():
                    current_diff.append(part)
        
        # 保存最后一个文件的diff
        if current_diff and current_path:
            file_diffs.append(("\n".join(current_diff), current_path))
        
        return file_diffs
    
    def _parse_hunks(self, file_diff):
        """
        解析文件diff中的所有hunks
        
        Args:
            file_diff: 单个文件的diff文本
            
        Returns:
            list: [{'target_start': int, 'target_length': int, 'added_lines': [], 'removed_lines': []}, ...]
        """
        hunks = []
        
        # 匹配hunk header: @@ -start,len +start,len @@
        hunk_pattern = re.compile(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@')
        
        # 分割成行
        lines = file_diff.split('\n')
        
        current_hunk = None
        target_line_no = 0
        source_line_no = 0
        
        for line in lines:
            hunk_match = hunk_pattern.match(line)
            if hunk_match:
                # 保存之前的hunk
                if current_hunk:
                    hunks.append(current_hunk)
                
                # 解析hunk header
                source_start = int(hunk_match.group(1))
                source_len = int(hunk_match.group(2)) if hunk_match.group(2) else 1
                target_start = int(hunk_match.group(3))
                target_len = int(hunk_match.group(4)) if hunk_match.group(4) else 1
                
                current_hunk = {
                    'source_start': source_start,
                    'source_length': source_len,
                    'target_start': target_start,
                    'target_length': target_len,
                    'added_lines': [],
                    'removed_lines': []
                }
                target_line_no = target_start
                source_line_no = source_start
                
            elif current_hunk is not None:
                if line.startswith('+') and not line.startswith('+++'):
                    current_hunk['added_lines'].append(target_line_no)
                    target_line_no += 1
                elif line.startswith('-') and not line.startswith('---'):
                    current_hunk['removed_lines'].append(source_line_no)
                    source_line_no += 1
                elif line.startswith(' ') or line == '':
                    # 上下文行
                    target_line_no += 1
                    source_line_no += 1
        
        # 保存最后一个hunk
        if current_hunk:
            hunks.append(current_hunk)
        
        return hunks
    
    def get_changed_line_ranges(self, diff_text):
        """
        获取diff中变更的行号范围（针对目标文件）
        
        Args:
            diff_text: diff文本
            
        Returns:
            list: [(start_line, end_line), ...]
        """
        try:
            if not diff_text:
                return []
            
            ranges = []
            file_diffs = self._split_diff_by_file(diff_text)
            
            for file_diff, _ in file_diffs:
                hunks = self._parse_hunks(file_diff)
                for hunk in hunks:
                    start = hunk['target_start']
                    end = hunk['target_start'] + hunk['target_length']
                    ranges.append((start, end))
            
            return ranges
        
        except Exception as e:
            logger.error(f"获取变更行范围失败: {e}")
            return []
    
    def detect_changed_methods(self, file_content, diff_text, code_analyzer):
        """
        检测变更的方法
        
        Args:
            file_content: 文件内容（变更后）
            diff_text: diff文本
            code_analyzer: CodeAnalyzer实例
            
        Returns:
            list: 变更的方法列表
        """
        try:
            # 解析文件，获取所有方法
            classes_info = code_analyzer.parse_java_file(file_content)
            
            # 获取变更的行范围
            changed_ranges = self.get_changed_line_ranges(diff_text)
            
            # 找出哪些方法被变更
            changed_methods = []
            
            for start, end in changed_ranges:
                methods = code_analyzer.get_methods_in_range(classes_info, start, end)
                for method in methods:
                    # 避免重复添加
                    if not any(m['method'] == method['method'] and m['class'] == method['class'] 
                              for m in changed_methods):
                        changed_methods.append(method)
            
            return changed_methods
        
        except Exception as e:
            logger.error(f"检测变更方法失败: {e}")
            return []
    
    def has_significant_changes(self, diff_text):
        """
        判断是否有实质性变更（排除空白、注释等）
        
        Args:
            diff_text: diff文本
            
        Returns:
            bool: 是否有实质性变更
        """
        try:
            if not diff_text:
                return False
            
            file_diffs = self._split_diff_by_file(diff_text)
            
            for file_diff, _ in file_diffs:
                lines = file_diff.split('\n')
                for line in lines:
                    # 跳过diff元数据行
                    if line.startswith('diff --git') or line.startswith('index ') or \
                       line.startswith('---') or line.startswith('+++') or \
                       line.startswith('@@'):
                        continue
                    
                    # 检查实际变更行
                    if line.startswith('+') or line.startswith('-'):
                        content = line[1:].strip()
                        # 检查是否为空白行或纯注释
                        if content and not content.startswith('//') and not content.startswith('/*'):
                            return True
            
            return False
        
        except Exception as e:
            logger.debug(f"检查实质性变更失败: {e}")
            return False
