"""
数据集生成器 - 负责生成最终的JSON格式数据集
"""

import json
import os
from datetime import datetime
from utils.logger import get_logger

logger = get_logger()


class DatasetGenerator:
    """数据集生成器"""
    
    def __init__(self, output_path):
        """
        初始化数据集生成器
        
        Args:
            output_path: 输出文件路径
        """
        self.output_path = output_path
        self.dataset = []
    
    def add_commit(self, commit_data):
        """
        添加一个commit到数据集
        
        Args:
            commit_data: commit数据字典
        """
        self.dataset.append(commit_data)
    
    def save_dataset(self):
        """
        保存数据集到文件
        
        Returns:
            bool: 是否成功保存
        """
        try:
            # 创建输出目录
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            
            # 添加元数据
            output_data = {
                'metadata': {
                    'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_commits': len(self.dataset),
                    'qualified_commits': len([c for c in self.dataset if c.get('qualified', False)])
                },
                'commits': self.dataset
            }
            
            # 保存JSON文件
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"数据集已保存: {self.output_path}")
            logger.info(f"总计: {len(self.dataset)} commits, 合格: {output_data['metadata']['qualified_commits']} commits")
            
            return True
        
        except Exception as e:
            logger.error(f"保存数据集失败: {e}")
            return False
    
    def load_intermediate_results(self, intermediate_path):
        """
        加载中间结果（支持断点续传）
        
        Args:
            intermediate_path: 中间结果文件路径
            
        Returns:
            list: 已处理的commit哈希列表
        """
        try:
            if os.path.exists(intermediate_path):
                with open(intermediate_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.dataset = data.get('commits', [])
                    processed_hashes = [c['commit_hash'] for c in self.dataset]
                    logger.info(f"加载中间结果: {len(processed_hashes)} commits")
                    return processed_hashes
        except Exception as e:
            logger.warning(f"加载中间结果失败: {e}")
        
        return []
    
    def save_intermediate_results(self, intermediate_path):
        """
        保存中间结果
        
        Args:
            intermediate_path: 中间结果文件路径
        """
        try:
            os.makedirs(os.path.dirname(intermediate_path), exist_ok=True)
            
            output_data = {
                'saved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'commits': self.dataset
            }
            
            with open(intermediate_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"中间结果已保存: {len(self.dataset)} commits")
        
        except Exception as e:
            logger.warning(f"保存中间结果失败: {e}")
    
    def format_commit_data(self, commit_info):
        """
        格式化commit数据，确保输出格式统一
        
        Args:
            commit_info: commit信息字典
            
        Returns:
            dict: 格式化后的commit数据
        """
        return {
            'commit_hash': commit_info.get('commit_hash', ''),
            'parent_hash': commit_info.get('parent_hash', ''),
            'author': commit_info.get('author', ''),
            'date': commit_info.get('date', ''),
            'message': commit_info.get('message', ''),
            'changed_files': commit_info.get('changed_files', {}),
            'changed_methods': {
                'test_methods': [
                    {
                        'class': m.get('class', ''),
                        'method': m.get('method', ''),
                        'line_range': [m.get('start_line', 0), m.get('end_line', 0)]
                    }
                    for m in commit_info.get('changed_methods', {}).get('test_methods', [])
                ],
                'source_methods': [
                    {
                        'class': m.get('class', ''),
                        'method': m.get('method', ''),
                        'line_range': [m.get('start_line', 0), m.get('end_line', 0)]
                    }
                    for m in commit_info.get('changed_methods', {}).get('source_methods', [])
                ]
            },
            'coverage_analysis': commit_info.get('coverage_analysis', {}),
            'build_status': commit_info.get('build_status', {}),
            'qualified': commit_info.get('qualified', False),
            'filter_reasons': commit_info.get('filter_reasons', [])
        }
    
    def get_statistics(self):
        """
        获取数据集统计信息
        
        Returns:
            dict: 统计信息
        """
        total = len(self.dataset)
        qualified = len([c for c in self.dataset if c.get('qualified', False)])
        
        return {
            'total_commits': total,
            'qualified_commits': qualified,
            'qualification_rate': qualified / total if total > 0 else 0.0
        }
