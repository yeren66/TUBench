"""
POM文件修改工具 - 用于动态添加JaCoCo插件
"""

import xml.etree.ElementTree as ET
import os
import shutil
from config import Config
from .logger import get_logger

logger = get_logger()

class PomModifier:
    """POM文件修改器"""
    
    # Maven命名空间
    MAVEN_NS = "http://maven.apache.org/POM/4.0.0"
    
    def __init__(self, pom_path):
        """
        初始化POM修改器
        
        Args:
            pom_path: pom.xml文件路径
        """
        self.pom_path = pom_path
        self.backup_path = pom_path + ".backup"
        
    def backup(self):
        """备份原始pom.xml"""
        if os.path.exists(self.pom_path):
            shutil.copy2(self.pom_path, self.backup_path)
            logger.debug(f"已备份POM文件: {self.backup_path}")
            return True
        return False
    
    def restore(self):
        """恢复原始pom.xml"""
        if os.path.exists(self.backup_path):
            shutil.copy2(self.backup_path, self.pom_path)
            os.remove(self.backup_path)
            logger.debug(f"已恢复POM文件: {self.pom_path}")
            return True
        return False
    
    def add_jacoco_plugin(self):
        """
        添加JaCoCo插件到pom.xml
        
        Returns:
            bool: 是否成功添加
        """
        try:
            # 注册命名空间
            ET.register_namespace('', self.MAVEN_NS)
            
            # 解析POM文件
            tree = ET.parse(self.pom_path)
            root = tree.getroot()
            
            # 检查是否已存在JaCoCo插件
            if self._has_jacoco_plugin(root):
                logger.debug("POM文件中已存在JaCoCo插件")
                return True
            
            # 查找或创建<build>节点
            build = root.find(f"{{{self.MAVEN_NS}}}build")
            if build is None:
                build = ET.SubElement(root, f"{{{self.MAVEN_NS}}}build")
            
            # 查找或创建<plugins>节点
            plugins = build.find(f"{{{self.MAVEN_NS}}}plugins")
            if plugins is None:
                plugins = ET.SubElement(build, f"{{{self.MAVEN_NS}}}plugins")
            
            # 创建JaCoCo插件配置
            jacoco_plugin = self._create_jacoco_plugin_xml()
            plugins.append(jacoco_plugin)
            
            # 保存修改后的POM
            tree.write(self.pom_path, encoding='utf-8', xml_declaration=True)
            logger.info(f"已添加JaCoCo插件到: {self.pom_path}")
            return True
            
        except Exception as e:
            logger.error(f"添加JaCoCo插件失败: {e}")
            return False
    
    def _has_jacoco_plugin(self, root):
        """检查是否已存在JaCoCo插件"""
        plugins = root.findall(f".//{{{self.MAVEN_NS}}}plugin")
        for plugin in plugins:
            artifact_id = plugin.find(f"{{{self.MAVEN_NS}}}artifactId")
            if artifact_id is not None and artifact_id.text == "jacoco-maven-plugin":
                return True
        return False
    
    def _create_jacoco_plugin_xml(self):
        """创建JaCoCo插件的XML配置"""
        # 创建plugin元素
        plugin = ET.Element(f"{{{self.MAVEN_NS}}}plugin")
        
        # groupId
        group_id = ET.SubElement(plugin, f"{{{self.MAVEN_NS}}}groupId")
        group_id.text = "org.jacoco"
        
        # artifactId
        artifact_id = ET.SubElement(plugin, f"{{{self.MAVEN_NS}}}artifactId")
        artifact_id.text = "jacoco-maven-plugin"
        
        # version
        version = ET.SubElement(plugin, f"{{{self.MAVEN_NS}}}version")
        version.text = Config.JACOCO_VERSION
        
        # executions
        executions = ET.SubElement(plugin, f"{{{self.MAVEN_NS}}}executions")
        
        # execution: prepare-agent
        execution1 = ET.SubElement(executions, f"{{{self.MAVEN_NS}}}execution")
        goals1 = ET.SubElement(execution1, f"{{{self.MAVEN_NS}}}goals")
        goal1 = ET.SubElement(goals1, f"{{{self.MAVEN_NS}}}goal")
        goal1.text = "prepare-agent"
        
        # execution: report
        execution2 = ET.SubElement(executions, f"{{{self.MAVEN_NS}}}execution")
        id2 = ET.SubElement(execution2, f"{{{self.MAVEN_NS}}}id")
        id2.text = "report"
        phase2 = ET.SubElement(execution2, f"{{{self.MAVEN_NS}}}phase")
        phase2.text = "test"
        goals2 = ET.SubElement(execution2, f"{{{self.MAVEN_NS}}}goals")
        goal2 = ET.SubElement(goals2, f"{{{self.MAVEN_NS}}}goal")
        goal2.text = "report"
        
        return plugin
    
    def __enter__(self):
        """上下文管理器入口"""
        self.backup()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.restore()
        return False
