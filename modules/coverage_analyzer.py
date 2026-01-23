"""
覆盖率分析模块 - 负责解析JaCoCo报告并分析覆盖情况
"""

import os
import xml.etree.ElementTree as ET
from utils.logger import get_logger
from utils.exceptions import CoverageError

logger = get_logger()


class CoverageAnalyzer:
    """覆盖率分析器"""
    
    def __init__(self):
        """初始化覆盖率分析器"""
        pass
    
    def parse_jacoco_report(self, report_path):
        """
        解析JaCoCo XML报告
        
        Args:
            report_path: JaCoCo报告文件路径
            
        Returns:
            dict: 覆盖率数据 {'classes': {'pkg.ClassName': {covered_lines: set()}}}
        """
        try:
            if not os.path.exists(report_path):
                logger.error(f"JaCoCo报告不存在: {report_path}")
                return None
            
            tree = ET.parse(report_path)
            root = tree.getroot()
            
            coverage_data = {'classes': {}}
            
            # 遍历所有package
            for package in root.findall('.//package'):
                package_name = package.get('name', '').replace('/', '.')
                
                # 遍历package中的sourcefile
                for sourcefile in package.findall('sourcefile'):
                    source_name = sourcefile.get('name', '')
                    # 尝试推断类名 (简化处理：假设类名与文件名一致)
                    class_simple_name = source_name.replace('.java', '')
                    full_class_name = f"{package_name}.{class_simple_name}"
                    
                    covered_lines = set()
                    for line in sourcefile.findall('line'):
                        if int(line.get('ci', 0)) > 0:  # ci = covered instructions
                            covered_lines.add(int(line.get('nr', 0)))
                    
                    if covered_lines:
                        coverage_data['classes'][full_class_name] = {
                            'source_file': source_name,
                            'covered_lines': covered_lines
                        }
                        
                        # 同时也尝试匹配可能的内部类或其他类名
                        # 在JaCoCo中，class元素和sourcefile元素是兄弟，但我们这里主要关心行覆盖
                        # 为了兼容性，我们也可以遍历class元素来获取更精确的类名映射，但行信息只在sourcefile里
            
            logger.debug(f"成功解析JaCoCo报告: {report_path}")
            return coverage_data
        
        except Exception as e:
            logger.error(f"解析JaCoCo报告失败 [{report_path}]: {e}")
            return None

    def analyze_test_coverage_for_changes(self, coverage_data, changed_test_methods, 
                                          changed_source_methods):
        """
        分析变更的被测方法的覆盖情况
        
        Args:
            coverage_data: 覆盖率数据
            changed_test_methods: 变更的测试方法列表 (仅用于统计，不用于关联)
            changed_source_methods: 变更的被测方法列表
            
        Returns:
            dict: 覆盖率统计
        """
        if not coverage_data or not changed_source_methods:
            return {
                'total_methods': 0,
                'covered_methods': 0,
                'coverage_ratio': 0.0,
                'details': []
            }
        
        total_methods = len(changed_source_methods)
        covered_count = 0
        details = []
        
        classes_coverage = coverage_data.get('classes', {})
        
        for method in changed_source_methods:
            full_class_name = f"{method.get('package', '')}.{method.get('class', '')}"
            start_line = method.get('start_line', 0)
            end_line = method.get('end_line', 0)
            
            is_covered = False
            
            # 查找该类的覆盖信息
            class_cov = classes_coverage.get(full_class_name)
            
            # 如果精确匹配失败，尝试模糊匹配（处理内部类情况）
            if not class_cov:
                class_cov = self._fuzzy_match_class(classes_coverage, method.get('class', ''), full_class_name)
            
            # 检查方法范围内是否有被覆盖的行
            if class_cov:
                covered_lines = class_cov['covered_lines']
                # 只要有一行被覆盖，我们就算该方法被覆盖了
                for line_num in range(start_line, end_line + 1):
                    if line_num in covered_lines:
                        is_covered = True
                        break

            if is_covered:
                covered_count += 1
                
            details.append({
                'method': f"{full_class_name}.{method.get('method', '')}",
                'covered': is_covered
            })
        
        # 计算覆盖率：被覆盖的变更方法 / 总变更方法
        coverage_ratio = covered_count / total_methods if total_methods > 0 else 0.0
        
        return {
            'total_methods': total_methods,
            'covered_methods': covered_count,
            'coverage_ratio': coverage_ratio,
            'details': details
        }
    
    def _fuzzy_match_class(self, classes_coverage, class_name, full_class_name):
        """
        模糊匹配类名，处理内部类情况
        
        策略：
        1. 查找以 .ClassName 结尾的 key
        2. 查找包含 ClassName$ 的 key（内部类模式）
        3. 查找源文件名匹配的 key
        
        Args:
            classes_coverage: 覆盖率数据字典
            class_name: 简单类名
            full_class_name: 完整类名
            
        Returns:
            dict or None: 匹配的覆盖信息，未找到返回None
        """
        if not class_name:
            return None
        
        # 策略1: 查找以 .ClassName 结尾的 key
        suffix = f".{class_name}"
        for key, value in classes_coverage.items():
            if key.endswith(suffix):
                logger.debug(f"模糊匹配成功: {full_class_name} -> {key}")
                return value
        
        # 策略2: 查找包含 ClassName$ 的 key（内部类）
        inner_class_pattern = f"{class_name}$"
        for key, value in classes_coverage.items():
            if inner_class_pattern in key:
                logger.debug(f"内部类匹配: {full_class_name} -> {key}")
                return value
        
        # 策略3: 通过源文件名匹配
        source_file = f"{class_name}.java"
        for key, value in classes_coverage.items():
            if value.get('source_file') == source_file:
                logger.debug(f"源文件匹配: {full_class_name} -> {key}")
                return value
        
        return None
