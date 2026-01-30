"""
配置文件 - 测试演化数据集构建工具
"""

import os
from datetime import datetime


class AnalysisConfig:
    """分析工具配置"""
    
    # ========== 分析输出配置 ==========
    # 分析输出目录
    ANALYSIS_OUTPUT_DIR = "./output/analysis"
    
    # 临时worktree目录
    ANALYSIS_WORKTREE_DIR = "/tmp/tubench_analysis_worktrees"
    
    # ========== 并发配置 ==========
    # 单项目内commit并发数
    ANALYSIS_WORKERS = 4
    
    # 单个版本执行时，是否并行执行4个版本
    PARALLEL_VERSION_EXECUTION = True
    
    # ========== 超时配置 ==========
    # 单次编译超时（秒）
    COMPILE_TIMEOUT = 300  # 5分钟
    
    # 单次测试超时（秒）
    TEST_TIMEOUT = 900  # 15分钟
    
    # 单个commit总超时（秒）
    COMMIT_TIMEOUT = 1800  # 30分钟
    
    # ========== 覆盖率配置 ==========
    # 覆盖率下降阈值（低于此值判定为Type2）
    COVERAGE_DECREASE_THRESHOLD = 0.02  # 2%
    # 分支覆盖率提升阈值（高于此值判定为Type2-branch）
    BRANCH_COVERAGE_INCREASE_THRESHOLD = 0.02  # 2%
    
    # ========== 缓存配置 ==========
    # 是否启用缓存
    ENABLE_CACHE = True
    
    # 缓存目录
    CACHE_DIR = "./cache/analysis"
    
    # ========== 日志配置 ==========
    # 分析日志文件
    ANALYSIS_LOG_FILE = "analysis.log"
    
    # ========== 版本兼容性配置 ==========
    # Java版本（设置JAVA_HOME环境变量路径，None表示使用系统默认）
    # 示例: "/usr/lib/jvm/java-8-openjdk-amd64"
    JAVA_HOME = None
    
    # Maven可执行文件路径（None表示使用PATH中的mvn）
    # 示例: "/opt/maven-3.6.3/bin/mvn"
    MAVEN_EXECUTABLE = None
    
    # 额外的Maven参数（用于解决兼容性问题）
    # 示例: "-Dmaven.compiler.source=1.8 -Dmaven.compiler.target=1.8"
    MAVEN_EXTRA_ARGS = ""
    
    # 是否在遇到兼容性问题时跳过commit（而不是标记为失败）
    SKIP_INCOMPATIBLE_COMMITS = False
    
    # 是否尝试自动修复常见的兼容性问题
    # 目前支持：自动调整source/target版本
    AUTO_FIX_COMPATIBILITY = False


class Config:
    """全局配置"""
    
    # ========== 基础配置 ==========
    # Git仓库路径（需要用户指定）
    REPO_PATH = "/Users/mac/Desktop/java-project/tu/temp/commons-csv"
    
    # 输出目录
    OUTPUT_DIR = "./output"
    OUTPUT_FILE = "dataset.json"
    INTERMEDIATE_FILE = "intermediate_results.json"
    LOG_FILE = "dataset_builder.log"
    
    # ========== 过滤条件 ==========
    # 只处理此日期之后的commits（格式：YYYY-MM-DD）
    DATE_FILTER = "2016-01-01"
    
    # 覆盖率阈值（50%的测试用例需要覆盖变更的被测函数）
    COVERAGE_THRESHOLD = 0.5
    
    # ========== 路径识别规则 ==========
    # 测试代码路径模式
    TEST_PATH_PATTERNS = ["src/test/java", "test/java", "src/test"]
    
    # 源代码路径模式
    SOURCE_PATH_PATTERNS = ["src/main/java", "main/java", "src/main"]
    
    # ========== Maven配置 ==========
    # Maven命令
    MAVEN_CMD = "mvn"
    
    # Maven超时时间（秒）
    MAVEN_TIMEOUT = 300
    
    # Maven参数
    MAVEN_OPTS = "-DskipTests=false -Dmaven.test.failure.ignore=true"
    
    # ========== JaCoCo配置 ==========
    JACOCO_VERSION = "0.8.11"
    JACOCO_REPORT_PATH = "target/site/jacoco/jacoco.xml"
    
    # ========== 并行处理配置 ==========
    # 并行worker数量
    PARALLEL_WORKERS = 10
    
    # 单个commit处理超时（秒）
    PROCESS_TIMEOUT = 900
    
    # ========== 高级选项 ==========
    # 是否保存中间结果（支持断点续传）
    SAVE_INTERMEDIATE = True
    
    # 中间结果保存间隔（处理多少个commit后保存一次）
    SAVE_INTERVAL = 10
    
    # 是否详细日志
    VERBOSE = True
    
    # 临时worktree目录前缀
    WORKTREE_PREFIX = "/tmp/test_evolution_worktree_"
    
    @classmethod
    def validate(cls):
        """验证配置"""
        if not cls.REPO_PATH:
            raise ValueError("REPO_PATH 未设置！请指定Git仓库路径。")
        
        if not os.path.exists(cls.REPO_PATH):
            raise ValueError(f"Git仓库路径不存在: {cls.REPO_PATH}")
        
        # 创建输出目录
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        
        return True
    
    @classmethod
    def get_output_path(cls, filename):
        """获取输出文件的完整路径"""
        return os.path.join(cls.OUTPUT_DIR, filename)
    
    @classmethod
    def get_date_filter(cls):
        """获取日期过滤器的datetime对象"""
        try:
            return datetime.strptime(cls.DATE_FILTER, "%Y-%m-%d")
        except:
            return None
