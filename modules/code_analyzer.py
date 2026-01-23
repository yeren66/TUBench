"""
代码分析模块 - 负责Java代码解析和方法提取
"""

import javalang
import re
from utils.logger import get_logger
from utils.exceptions import ParseError

logger = get_logger()


class CodeAnalyzer:
    """Java代码分析器"""
    
    def __init__(self):
        """初始化代码分析器"""
        pass
    
    def parse_java_file(self, file_content):
        """
        解析Java文件，提取类和方法信息
        
        Args:
            file_content: Java文件内容
            
        Returns:
            dict: {'classes': [{'name': str, 'methods': [{'name': str, 'start_line': int, 'end_line': int}]}]}
        """
        try:
            tree = javalang.parse.parse(file_content)
            classes = []
            
            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                class_info = {
                    'name': node.name,
                    'methods': []
                }
                
                # 提取类中的方法
                for idx, method in enumerate(node.methods):
                    start_line = method.position.line if method.position else 0
                    method_info = {
                        'name': method.name,
                        'start_line': start_line,
                        'parameters': [p.type.name for p in method.parameters] if method.parameters else []
                    }
                    
                    # 估算方法结束行
                    end_line = self._estimate_method_end_line(file_content, start_line)
                    
                    # 如果无法确定结束行，使用下一个方法的开始行作为参考
                    if end_line is None:
                        if idx + 1 < len(node.methods) and node.methods[idx + 1].position:
                            # 使用下一个方法的开始行减1
                            end_line = node.methods[idx + 1].position.line - 1
                        else:
                            # 最后的方法，使用文件总行数
                            end_line = len(file_content.split('\n'))
                    
                    method_info['end_line'] = end_line
                    class_info['methods'].append(method_info)
                
                classes.append(class_info)
            
            return {'classes': classes}
        
        except Exception as e:
            logger.debug(f"解析Java文件失败: {e}")
            return {'classes': []}
    
    def _estimate_method_end_line(self, file_content, start_line):
        """
        估算方法的结束行号，使用状态机跳过字符串和注释中的括号
        
        Args:
            file_content: 文件内容
            start_line: 方法开始行号
            
        Returns:
            int or None: 估算的结束行号，无法确定时返回None
        """
        lines = file_content.split('\n')
        if start_line >= len(lines) or start_line < 1:
            return None
        
        brace_stack = []  # 使用栈追踪括号
        found_first_brace = False
        
        # 状态追踪
        in_string = False       # 在字符串中 "..."
        in_char = False         # 在字符中 '...'
        in_single_comment = False  # 在单行注释中 //
        in_multi_comment = False   # 在多行注释中 /* */
        escape_next = False     # 下一个字符是转义字符
        
        for line_idx in range(start_line - 1, len(lines)):
            line = lines[line_idx]
            in_single_comment = False  # 每行重置单行注释状态
            
            i = 0
            while i < len(line):
                char = line[i]
                next_char = line[i + 1] if i + 1 < len(line) else ''
                
                # 处理转义字符
                if escape_next:
                    escape_next = False
                    i += 1
                    continue
                
                if char == '\\' and (in_string or in_char):
                    escape_next = True
                    i += 1
                    continue
                
                # 处理多行注释结束
                if in_multi_comment:
                    if char == '*' and next_char == '/':
                        in_multi_comment = False
                        i += 2
                        continue
                    i += 1
                    continue
                
                # 处理单行注释
                if in_single_comment:
                    i += 1
                    continue
                
                # 处理字符串
                if in_string:
                    if char == '"':
                        in_string = False
                    i += 1
                    continue
                
                # 处理字符常量
                if in_char:
                    if char == "'":
                        in_char = False
                    i += 1
                    continue
                
                # 检测注释开始
                if char == '/' and next_char == '/':
                    in_single_comment = True
                    i += 2
                    continue
                
                if char == '/' and next_char == '*':
                    in_multi_comment = True
                    i += 2
                    continue
                
                # 检测字符串/字符开始
                if char == '"':
                    in_string = True
                    i += 1
                    continue
                
                if char == "'":
                    in_char = True
                    i += 1
                    continue
                
                # 处理括号（只有在代码区域才计数）
                if char == '{':
                    brace_stack.append('{')
                    found_first_brace = True
                elif char == '}':
                    if brace_stack:
                        brace_stack.pop()
                    # 当找到第一个括号后，栈空表示方法结束
                    if found_first_brace and len(brace_stack) == 0:
                        return line_idx + 1  # 返回1-indexed行号
                
                i += 1
        
        # 无法确定结束行，返回None让上层处理
        return None
    
    def get_methods_in_range(self, classes_info, start_line, end_line):
        """
        获取指定行范围内的方法
        
        Args:
            classes_info: 类信息字典
            start_line: 起始行
            end_line: 结束行
            
        Returns:
            list: 方法信息列表
        """
        methods = []
        
        for class_info in classes_info.get('classes', []):
            for method in class_info['methods']:
                method_start = method['start_line']
                method_end = method['end_line']
                
                # 检查方法是否与指定范围有重叠
                if self._ranges_overlap(method_start, method_end, start_line, end_line):
                    methods.append({
                        'class': class_info['name'],
                        'method': method['name'],
                        'parameters': method.get('parameters', []),
                        'start_line': method_start,
                        'end_line': method_end
                    })
        
        return methods
    
    def _ranges_overlap(self, start1, end1, start2, end2):
        """检查两个范围是否有重叠"""
        return not (end1 < start2 or end2 < start1)
    
    def extract_test_methods(self, file_content):
        """
        提取测试方法（带@Test注解的方法）
        
        Args:
            file_content: Java文件内容
            
        Returns:
            list: 测试方法列表
        """
        try:
            tree = javalang.parse.parse(file_content)
            test_methods = []
            
            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                class_name = node.name
                
                for method in node.methods:
                    # 检查是否有@Test注解
                    if method.annotations:
                        for annotation in method.annotations:
                            if annotation.name == 'Test':
                                test_methods.append({
                                    'class': class_name,
                                    'method': method.name,
                                    'start_line': method.position.line if method.position else 0
                                })
                                break
            
            return test_methods
        
        except Exception as e:
            logger.debug(f"提取测试方法失败: {e}")
            return []
    
    def get_package_name(self, file_content):
        """
        获取Java文件的包名
        
        Args:
            file_content: Java文件内容
            
        Returns:
            str: 包名
        """
        try:
            tree = javalang.parse.parse(file_content)
            return tree.package.name if tree.package else ""
        except:
            return ""
    
    def get_class_full_name(self, file_path, file_content):
        """
        获取类的全限定名
        
        Args:
            file_path: 文件路径
            file_content: 文件内容
            
        Returns:
            str: 类的全限定名 (如: com.example.MyClass)
        """
        package = self.get_package_name(file_content)
        class_name = file_path.split('/')[-1].replace('.java', '')
        
        if package:
            return f"{package}.{class_name}"
        return class_name
