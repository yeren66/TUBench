"""
Commit分类器 - 基于执行结果进行三种类型分类

类型定义:
- Type1 (执行出错): V-0.5编译失败或测试失败
- Type2 (覆盖率差距): V0相比V-0.5覆盖率提升，说明旧测试覆盖不足
- Type3 (适应性调整): 不属于Type1和Type2的合格commit
"""

from typing import Dict, Any

from config import AnalysisConfig
from utils.logger import get_logger

logger = get_logger()


class CommitClassifier:
    """Commit分类器 - 检测三种过时测试用例类型"""
    
    def __init__(self, coverage_threshold: float = None):
        """
        初始化分类器
        
        Args:
            coverage_threshold: 覆盖率下降阈值，默认使用配置
        """
        if coverage_threshold is None:
            coverage_threshold = AnalysisConfig.COVERAGE_DECREASE_THRESHOLD
        self.coverage_threshold = coverage_threshold
    
    def classify(self,
                 v1_result: Dict[str, Any],
                 v05_result: Dict[str, Any],
                 t05_result: Dict[str, Any],
                 v0_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        对commit进行分类
        
        分类逻辑:
        1. 先检测Type1（执行出错）
        2. 再检测Type2（覆盖率差距）
        3. 如果不属于Type1和Type2，则归为Type3（适应性调整）
        
        T-0.5用于辅助分析，提供额外的置信度信息
        
        Args:
            v1_result: V-1版本执行结果
            v05_result: V-0.5版本执行结果
            t05_result: T-0.5版本执行结果
            v0_result: V0版本执行结果
            
        Returns:
            分类结果字典
        """
        # 确定场景
        scenario = self._determine_scenario(v05_result, t05_result)
        scenario_desc = self._get_scenario_description(scenario)
        
        # 检测Type1
        type1_result = self._detect_type1(v05_result, t05_result, v0_result)
        
        # 检测Type2
        type2_result = self._detect_type2(v05_result, t05_result, v0_result)
        
        # 检测Type3（兜底）
        is_type1 = type1_result.get('detected', False)
        is_type2 = type2_result.get('detected', False)
        type3_result = self._detect_type3(is_type1, is_type2, scenario)
        
        # 汇总
        all_types = []
        if is_type1:
            all_types.append('type1_execution_error')
        if is_type2:
            all_types.append('type2_coverage_decrease')
        if type3_result.get('detected', False):
            all_types.append('type3_adaptive_change')
        
        # 确定主要类型（优先级：Type1 > Type2 > Type3）
        primary_type = None
        if all_types:
            primary_type = all_types[0]
        
        return {
            'scenario': scenario,
            'scenario_description': scenario_desc,
            'type1_execution_error': type1_result,
            'type2_coverage_decrease': type2_result,
            'type3_adaptive_change': type3_result,
            'all_types': all_types,
            'primary_type': primary_type,
            'types_count': len(all_types)
        }
    
    def _determine_scenario(self, v05_result: Dict, t05_result: Dict) -> str:
        """
        确定属于哪个场景 (A/B/C/D)
        
        场景定义:
        - A: V-0.5失败，T-0.5失败
        - B: V-0.5失败，T-0.5通过
        - C: V-0.5通过，T-0.5失败
        - D: V-0.5通过，T-0.5通过
        """
        v05_state = self._get_version_state(v05_result)
        t05_state = self._get_version_state(t05_result)

        if v05_state == 'unknown' or t05_state == 'unknown':
            return 'U'

        v05_pass = v05_state == 'pass'
        t05_pass = t05_state == 'pass'

        if not v05_pass and not t05_pass:
            return 'A'
        elif not v05_pass and t05_pass:
            return 'B'
        elif v05_pass and not t05_pass:
            return 'C'
        else:
            return 'D'
    
    def _is_version_pass(self, result: Dict) -> bool:
        """判断版本是否通过（编译成功且测试成功）"""
        if not result:
            return False
        
        build_success = result.get('build', {}).get('success', False)
        test_status = self._get_test_status(result)
        
        return build_success and test_status == 'pass'

    def _get_version_state(self, result: Dict) -> str:
        """获取版本状态：pass / fail / unknown"""
        if not result:
            return 'unknown'

        build_success = result.get('build', {}).get('success', False)
        test_status = self._get_test_status(result)

        if not build_success:
            return 'fail'

        if test_status == 'pass':
            return 'pass'
        if test_status == 'fail':
            return 'fail'
        return 'unknown'

    def _get_test_status(self, result: Dict) -> str:
        """提取测试状态：pass / fail / skip / error / unknown"""
        test = result.get('test', {}) if result else {}
        status = test.get('status')
        if status:
            return status
        success = test.get('success')
        if success is True:
            return 'pass'
        if success is False:
            return 'fail'
        return 'unknown'
    
    def _get_scenario_description(self, scenario: str) -> str:
        """获取场景描述"""
        descriptions = {
            'A': 'V-0.5失败，T-0.5失败：源代码行为变更，新旧测试都不适配',
            'B': 'V-0.5失败，T-0.5通过：旧测试失败，但新测试在旧代码上可工作',
            'C': 'V-0.5通过，T-0.5失败：旧测试能通过，新测试针对新增功能',
            'D': 'V-0.5通过，T-0.5通过：小幅调整，可能是覆盖率变化或适应性修改',
            'U': 'V-0.5或T-0.5测试被跳过/结果未知：场景不确定'
        }
        return descriptions.get(scenario, 'Unknown scenario')
    
    def _detect_type1(self, v05_result: Dict, t05_result: Dict, v0_result: Dict) -> Dict:
        """
        检测Type1: 执行出错
        
        判定条件:
        - V-0.5编译失败 → Type1a (compile_failure)
        - V-0.5测试失败且V0测试通过 → Type1b (runtime_failure)
        
        T-0.5辅助分析:
        - 如果T-0.5也失败（场景A），置信度更高
        - 如果T-0.5通过（场景B），可能涉及测试重构
        """
        result = {
            'detected': False,
            'subtype': None,
            'confidence': None,
            'evidence': {}
        }
        
        v05_build = v05_result.get('build', {})
        v05_test = v05_result.get('test', {})
        v0_test = v0_result.get('test', {})
        t05_build = t05_result.get('build', {})
        t05_test = t05_result.get('test', {})
        
        # 情况1: V-0.5编译失败
        if not v05_build.get('success', False):
            result['detected'] = True
            result['subtype'] = 'compile_failure'
            result['confidence'] = 'high'
            result['evidence'] = {
                'v05_build_success': False,
                'error_message': v05_build.get('error_message'),
                'compile_errors': v05_build.get('compile_errors', []),
                't05_build_success': t05_build.get('success', False)
            }
            return result
        
        # 情况2: V-0.5测试编译失败
        v05_test_status = self._get_test_status(v05_result)
        v0_test_status = self._get_test_status(v0_result)
        v05_error_type = v05_test.get('error_type')

        if v05_test_status == 'error' and v05_error_type == 'test_compile':
            result['detected'] = True
            result['subtype'] = 'test_compile_failure'
            result['confidence'] = 'high'
            result['evidence'] = {
                'v05_test_status': v05_test_status,
                'v05_error_type': v05_error_type,
                'error_message': v05_test.get('error_message'),
                't05_test_status': self._get_test_status(t05_result),
                'v0_test_status': v0_test_status
            }
            return result

        # 情况3: V-0.5测试失败
        if v05_test_status == 'fail':
            # 确认V0测试是通过的（排除测试本身有问题的情况）
            if v0_test_status == 'pass':
                result['detected'] = True
                result['subtype'] = 'runtime_failure'
                
                # 根据T-0.5结果调整置信度
                t05_test_status = self._get_test_status(t05_result)
                
                if t05_test_status == 'fail':
                    # 场景A: T-0.5也失败，高置信度
                    result['confidence'] = 'high'
                    result['evidence']['t05_analysis'] = 'T-0.5也失败，确认是源代码行为变更导致'
                elif t05_test_status == 'pass':
                    # 场景B: T-0.5通过，中等置信度
                    result['confidence'] = 'medium'
                    result['evidence']['t05_analysis'] = 'T-0.5通过，新测试在旧代码上可工作，可能涉及测试重构'
                else:
                    result['confidence'] = 'low'
                    result['evidence']['t05_analysis'] = 'T-0.5测试被跳过或结果未知，置信度降低'
                
                result['evidence']['v05_test_status'] = v05_test_status
                result['evidence']['v0_test_status'] = v0_test_status
                result['evidence']['failed_tests_count'] = v05_test.get('failed', 0) + v05_test.get('errors', 0)
                result['evidence']['failed_tests'] = v05_test.get('failed_tests', [])[:10]
        elif v05_test_status in ('skip', 'error', 'unknown'):
            result['evidence']['note'] = f"V-0.5测试状态为{v05_test_status}，无法判定Type1运行时失败"
        
        return result
    
    def _detect_type2(self, v05_result: Dict, t05_result: Dict, v0_result: Dict) -> Dict:
        """
        检测Type2: 覆盖率差距
        
        判定条件:
        - V0相比V-0.5的变更方法覆盖率提升超过阈值
        - 或 V0相比V-0.5的变更方法分支覆盖率提升超过阈值
        
        T-0.5辅助分析:
        - T-0.5的变更方法覆盖率可以显示新测试增加了多少覆盖
        """
        result = {
            'detected': False,
            'confidence': None,
            'evidence': {}
        }
        
        # 如果V-0.5编译失败或测试未通过，不能准确分析覆盖率
        if not v05_result.get('build', {}).get('success', False):
            result['evidence']['note'] = 'V-0.5编译失败，无法分析覆盖率'
            return result
        v05_test_status = self._get_test_status(v05_result)
        if v05_test_status != 'pass':
            result['evidence']['note'] = f'V-0.5测试状态为{v05_test_status}，无法分析覆盖率'
            return result
        
        # 获取覆盖率数据
        v05_coverage = v05_result.get('coverage', {})
        v0_coverage = v0_result.get('coverage', {})
        t05_coverage = t05_result.get('coverage', {}) if t05_result.get('build', {}).get('success') else {}

        # 使用变更方法的行覆盖率（更严格）
        v05_method_cov = v05_coverage.get('method_line_coverage')
        v0_method_cov = v0_coverage.get('method_line_coverage')
        t05_method_cov = t05_coverage.get('method_line_coverage') if t05_coverage else None

        line_signal = None
        branch_signal = None

        if v05_method_cov and v0_method_cov and v05_method_cov.get('total_lines', 0) > 0:
            v05_ratio = v05_method_cov.get('coverage_ratio', 0)
            v0_ratio = v0_method_cov.get('coverage_ratio', 0)
            coverage_diff = v0_ratio - v05_ratio

            if coverage_diff >= self.coverage_threshold:
                line_signal = {
                    'metric': 'changed_methods_line_coverage',
                    'v05_coverage_ratio': round(v05_ratio, 4),
                    'v0_coverage_ratio': round(v0_ratio, 4),
                    'coverage_diff': round(coverage_diff, 4),
                    'total_lines': v05_method_cov.get('total_lines', 0),
                    'threshold': self.coverage_threshold
                }

                if t05_method_cov and t05_method_cov.get('total_lines', 0) > 0:
                    t05_ratio = t05_method_cov.get('coverage_ratio', 0)
                    line_signal['t05_coverage_ratio'] = round(t05_ratio, 4)

        # 分支覆盖率信号
        branch_threshold = getattr(AnalysisConfig, 'BRANCH_COVERAGE_INCREASE_THRESHOLD', self.coverage_threshold)
        v05_branch_cov = v05_coverage.get('method_branch_coverage')
        v0_branch_cov = v0_coverage.get('method_branch_coverage')
        if v05_branch_cov and v0_branch_cov and v05_branch_cov.get('total_branches', 0) > 0:
            v05_branch_ratio = v05_branch_cov.get('coverage_ratio', 0)
            v0_branch_ratio = v0_branch_cov.get('coverage_ratio', 0)
            branch_diff = v0_branch_ratio - v05_branch_ratio

            if branch_diff >= branch_threshold:
                branch_signal = {
                    'metric': 'changed_methods_branch_coverage',
                    'v05_branch_ratio': round(v05_branch_ratio, 4),
                    'v0_branch_ratio': round(v0_branch_ratio, 4),
                    'branch_coverage_diff': round(branch_diff, 4),
                    'total_branches': v05_branch_cov.get('total_branches', 0),
                    'threshold': branch_threshold
                }

        if line_signal or branch_signal:
            result['detected'] = True
            max_diff = 0.0
            if line_signal:
                max_diff = max(max_diff, line_signal.get('coverage_diff', 0))
            if branch_signal:
                max_diff = max(max_diff, branch_signal.get('branch_coverage_diff', 0))
            result['confidence'] = 'high' if max_diff >= 0.1 else 'medium'
            result['evidence'] = {'signals': []}
            if line_signal:
                result['evidence']['signals'].append(line_signal)
            if branch_signal:
                result['evidence']['signals'].append(branch_signal)

            primary_signal = line_signal or branch_signal
            if primary_signal:
                result['evidence'].update(primary_signal)
            if branch_signal and 'branch_coverage_diff' not in result['evidence']:
                result['evidence']['branch_coverage_diff'] = branch_signal.get('branch_coverage_diff')
            return result

        # 覆盖率不可用或无显著提升
        if not (v05_method_cov and v0_method_cov):
            result['evidence']['note'] = '变更方法覆盖率不可用'
        else:
            result['evidence']['note'] = '变更方法覆盖率提升不显著'
        
        return result
    
    def _detect_type3(self, is_type1: bool, is_type2: bool, scenario: str) -> Dict:
        """
        检测Type3: 适应性调整
        
        判定逻辑:
        - 不属于Type1且不属于Type2的合格commit
        - 这是一个兜底分类
        """
        result = {
            'detected': False,
            'confidence': None,
            'evidence': {}
        }
        
        # 只有不属于Type1和Type2的才归为Type3
        if not is_type1 and not is_type2:
            result['detected'] = True
            result['confidence'] = 'low' if scenario == 'U' else 'high'
            result['evidence'] = {
                'reason': '不属于Type1（执行出错）且不属于Type2（覆盖率差距），归类为适应性调整',
                'scenario': scenario,
                'scenario_meaning': self._get_type3_scenario_meaning(scenario)
            }
            if scenario == 'U':
                result['evidence']['note'] = 'V-0.5或T-0.5测试被跳过/结果未知，置信度降低'
        
        return result
    
    def _get_type3_scenario_meaning(self, scenario: str) -> str:
        """获取Type3在不同场景下的含义"""
        meanings = {
            'C': '新测试针对新增功能，旧测试仍可通过',
            'D': '小幅适应性调整，新旧测试都能通过',
            'U': '执行信息不足，场景不确定'
        }
        return meanings.get(scenario, '适应性调整')
