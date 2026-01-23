"""
Maven执行模块 - 负责Maven构建、测试执行和JaCoCo集成
"""

import os
import subprocess
from config import Config
from utils.logger import get_logger
from utils.pom_modifier import PomModifier

logger = get_logger()


class MavenExecutor:
    """Maven执行器"""
    
    def __init__(self, project_path):
        """
        初始化Maven执行器
        
        Args:
            project_path: Maven项目路径
        """
        self.project_path = project_path
        self.pom_path = os.path.join(project_path, 'pom.xml')
    
    def has_pom(self):
        """检查是否存在pom.xml"""
        return os.path.exists(self.pom_path)
    
    def clean(self):
        """执行Maven clean"""
        return self._run_maven_command('clean')
    
    def compile(self):
        """执行Maven compile"""
        return self._run_maven_command('compile')
    
    def test(self):
        """执行Maven test"""
        return self._run_maven_command('test')
    
    def test_with_jacoco(self):
        """
        使用JaCoCo执行测试
        
        Returns:
            dict: {'success': bool, 'output': str, 'jacoco_report': str}
        """
        result = {
            'success': False,
            'output': '',
            'jacoco_report': None
        }
        
        # 修改pom.xml添加JaCoCo
        pom_modifier = PomModifier(self.pom_path)
        
        try:
            # 备份并修改POM
            if not pom_modifier.backup():
                logger.error("无法备份pom.xml")
                return result
            
            if not pom_modifier.add_jacoco_plugin():
                logger.error("无法添加JaCoCo插件")
                pom_modifier.restore()
                return result
            
            # 执行clean test
            success, output = self._run_maven_command('clean test')
            result['success'] = success
            result['output'] = output
            
            # 获取JaCoCo报告路径
            if success:
                jacoco_report_path = os.path.join(self.project_path, Config.JACOCO_REPORT_PATH)
                if os.path.exists(jacoco_report_path):
                    result['jacoco_report'] = jacoco_report_path
                    logger.debug(f"JaCoCo报告生成: {jacoco_report_path}")
                else:
                    logger.warning(f"JaCoCo报告未找到: {jacoco_report_path}")
            
        except Exception as e:
            logger.error(f"执行Maven测试失败: {e}")
        
        finally:
            # 恢复原始POM
            pom_modifier.restore()
        
        return result
    
    def _run_maven_command(self, goal):
        """
        执行Maven命令
        
        Args:
            goal: Maven目标（如：clean, test, compile）
            
        Returns:
            tuple: (success: bool, output: str)
        """
        try:
            # Add Maven options to skip RAT check (license validation fails after POM modification)
            # and ignore test failures to allow processing to continue
            cmd = [Config.MAVEN_CMD, '-Drat.skip=true', '-Dmaven.test.failure.ignore=true'] + goal.split()
            
            logger.debug(f"执行Maven命令: {' '.join(cmd)} @ {self.project_path}")
            
            process = subprocess.Popen(
                cmd,
                cwd=self.project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # 设置超时
            try:
                output, _ = process.communicate(timeout=Config.MAVEN_TIMEOUT)
                success = process.returncode == 0
                
                if success:
                    logger.debug(f"Maven命令执行成功: {goal}")
                else:
                    logger.warning(f"Maven命令执行失败 (返回码: {process.returncode}): {goal}")
                    # Log last part of output for debugging
                    logger.warning(f"Maven输出(最后3000字符): {output[-3000:]}")
                
                return success, output
            
            except subprocess.TimeoutExpired:
                process.kill()
                logger.error(f"Maven命令超时: {goal}")
                return False, "Timeout"
        
        except Exception as e:
            logger.error(f"执行Maven命令异常 [{goal}]: {e}")
            return False, str(e)
    
    def get_test_failures(self, test_output):
        """
        从测试输出中提取失败的测试用例
        
        Args:
            test_output: Maven test命令的输出
            
        Returns:
            list: 失败的测试用例列表
        """
        failures = []
        
        try:
            lines = test_output.split('\n')
            for line in lines:
                if 'FAILED' in line or 'ERROR' in line:
                    failures.append(line.strip())
        
        except Exception as e:
            logger.debug(f"解析测试失败信息异常: {e}")
        
        return failures
    
    def check_compilation(self):
        """
        检查项目是否能够编译
        
        Returns:
            bool: 是否编译成功
        """
        success, _ = self._run_maven_command('clean compile')
        return success
