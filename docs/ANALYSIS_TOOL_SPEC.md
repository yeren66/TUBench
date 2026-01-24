# TUBench Analysis Tool - 开发计划需求文档

## 1. 项目概述

### 1.1 背景
TUBench是一个测试演化数据集构建工具。在正式构建数据集之前，需要一个分析工具来评估候选项目中可用数据的数量和质量，帮助研究人员进行调研和决策。

### 1.2 目标
开发一个独立的分析工具 `analysis.py`，用于：
1. 分析17个defects4j-projects中的Java项目
2. 筛选符合条件的commits
3. 对每个合格commit进行三种类型分类（执行出错、覆盖率降低、适应性调整）
4. 生成详细的分析报告供研究人员查阅

### 1.3 与现有TUBench的关系
- **analysis.py**: 分析阶段，使用临时worktree（方案B），不污染原始仓库
- **main.py**: 数据集构建阶段，创建实际Git分支（方案A）

---

## 2. 核心概念

### 2.1 四个版本定义

```
V-1 (父commit) ─────────────────────────────────────────────────────────┐
    │                                                                    │
    ├──> V-0.5 (仅源代码变更)                                            │
    │    - 基于V-1，只应用源代码的diff                                   │
    │    - 模拟"开发者更新了代码，但忘记更新测试"的场景                  │
    │    - 用于检测Type1和Type2                                          │
    │                                                                    │
    ├──> T-0.5 (仅测试代码变更)                                          │
    │    - 基于V-1，只应用测试代码的diff                                 │
    │    - 模拟"只有测试更新"的场景                                      │
    │    - 用于辅助分析，不纳入最终数据集                                │
    │                                                                    │
    └──> V0 (完整版本，即原始commit)                                     │
         - 包含所有变更（源代码+测试代码）                               │
         - 作为"正确"版本的参照                                          │
```

### 2.2 三种过时测试用例类型

| 类型 | 名称 | 检测条件 | 含义 |
|------|------|----------|------|
| Type1 | 执行出错 | V-0.5编译失败或测试失败 | 旧测试无法在新代码上正常执行 |
| Type2 | 覆盖率降低 | V-0.5变更方法覆盖率比V-1下降 | 旧测试对新代码的覆盖不足 |
| Type3 | 适应性调整 | 不属于Type1和Type2 | 测试需要适应性修改 |

**分类规则**：
- Type1和Type2不互斥，一个commit可能同时属于两者
- Type3是兜底分类：合格commit中不属于Type1和Type2的都归为Type3
- 每个合格commit至少属于一种类型

### 2.3 场景矩阵

| 场景 | V-0.5结果 | T-0.5结果 | 典型分类 | 含义 |
|------|-----------|-----------|----------|------|
| A | ❌失败 | ❌失败 | Type1(高置信度) | 源代码行为变更，新旧测试都不适配旧/新代码 |
| B | ❌失败 | ✅通过 | Type1(中置信度) | 旧测试失败，但新测试在旧代码上可工作 |
| C | ✅通过 | ❌失败 | Type2/Type3 | 新测试针对新增功能，旧代码不具备 |
| D | ✅通过 | ✅通过 | Type2/Type3 | 小幅调整，可能是覆盖率变化或适应性修改 |

### 2.4 合格Commit的定义

一个commit被认为是"合格"的，需要满足以下全部条件：
1. **同时修改测试和源代码**: 变更文件中同时包含测试文件和源代码文件
2. **有方法级别的变更**: 能够检测到具体的方法变更（不只是注释或格式化）
3. **V-1构建成功**: 父commit能够成功编译和通过测试
4. **V0构建成功**: 当前commit能够成功编译和通过测试

---

## 3. 系统架构

### 3.1 目录结构

```
TUBench/
├── analysis.py                          # 【新增】分析工具主入口
├── main.py                              # 数据集构建主入口（保留）
├── generate_filtered_versions.py        # 过滤版本生成（保留）
├── config.py                            # 配置文件（扩展）
│
├── modules/                             # 核心模块
│   ├── __init__.py
│   ├── git_analyzer.py                  # Git分析（已有，可能需增强）
│   ├── code_analyzer.py                 # 代码分析（已有）
│   ├── change_detector.py               # 变更检测（已有）
│   ├── maven_executor.py                # Maven执行（已有）
│   ├── coverage_analyzer.py             # 覆盖率分析（已有，需增强）
│   ├── commit_filter.py                 # Commit过滤（已有）
│   ├── diff_filter.py                   # Diff过滤（已有）
│   ├── filtered_version_generator.py    # 版本生成-方案A（已有）
│   ├── dataset_generator.py             # 数据集生成（已有）
│   │
│   ├── isolated_executor.py             # 【新增】隔离执行器-方案B
│   ├── test_result_analyzer.py          # 【新增】测试结果分析
│   └── commit_classifier.py             # 【新增】Commit三类型分类器
│
├── analysis/                            # 【新增】分析专用模块
│   ├── __init__.py
│   ├── project_analyzer.py              # 单项目分析器
│   ├── commit_analyzer.py               # 单commit分析器
│   ├── report_generator.py              # 报告生成器
│   └── cache_manager.py                 # 缓存管理器
│
├── utils/                               # 工具模块
│   ├── __init__.py
│   ├── logger.py                        # 日志（已有）
│   └── exceptions.py                    # 异常（已有）
│
├── docs/                                # 【新增】文档目录
│   └── ANALYSIS_TOOL_SPEC.md            # 本文档
│
└── output/
    └── analysis/                        # 【新增】分析输出目录
        ├── {project_name}/              # 每个项目一个子目录
        │   ├── analysis_result.json     # 项目完整分析结果
        │   ├── commits/                 # 每个commit的详细信息
        │   │   ├── {commit_hash}.json
        │   │   ├── {commit_hash}/       # 可视化辅助文件
        │   │   │   ├── summary.md        # commit级摘要（执行/覆盖率）
        │   │   │   ├── full.diff         # 完整diff
        │   │   │   ├── source_only.diff  # 仅源代码diff
        │   │   │   └── test_only.diff    # 仅测试diff
        │   │   └── ...
        │   └── summary.md               # 项目摘要报告
        │
        └── global_summary/              # 全局汇总
            ├── all_projects_stats.json  # 所有项目统计
            └── analysis_report.md       # 总报告
```

### 3.2 模块依赖关系

```
analysis.py
    │
    ├── analysis/project_analyzer.py
    │       │
    │       ├── analysis/commit_analyzer.py
    │       │       │
    │       │       ├── modules/git_analyzer.py
    │       │       ├── modules/code_analyzer.py
    │       │       ├── modules/change_detector.py
    │       │       ├── modules/diff_filter.py
    │       │       ├── modules/isolated_executor.py ──┐
    │       │       │       │                          │
    │       │       │       └── modules/maven_executor.py
    │       │       │                                  │
    │       │       ├── modules/coverage_analyzer.py ◄─┘
    │       │       ├── modules/test_result_analyzer.py
    │       │       └── modules/commit_classifier.py
    │       │
    │       └── analysis/report_generator.py
    │
    └── analysis/cache_manager.py
```

---

## 4. 详细设计

### 4.1 命令行接口

```bash
# 基本用法 - 分析单个项目
python analysis.py --project /work/defects4j-projects/commons-csv

# 分析指定目录下的所有项目
python analysis.py --projects-dir /work/defects4j-projects

# 指定输出目录
python analysis.py --project /path/to/project --output ./output/analysis

# 控制并发数（针对单个项目内的不同commit）
python analysis.py --project /path/to/project --workers 4

# 分阶段执行
python analysis.py --project /path/to/project --phase quick   # 仅快速扫描
python analysis.py --project /path/to/project --phase method  # 到方法分析
python analysis.py --project /path/to/project --phase full    # 完整分析（默认）

# 日期过滤
python analysis.py --project /path/to/project --since 2016-01-01

# 采样模式（用于快速测试）
python analysis.py --project /path/to/project --sample 10

# 断点续传
python analysis.py --project /path/to/project --resume

# 指定单个commit分析（调试用）
python analysis.py --project /path/to/project --commit abc123

# 详细日志
python analysis.py --project /path/to/project --verbose
```

### 4.2 配置扩展 (config.py)

```python
class AnalysisConfig:
    """分析工具配置"""
    
    # ========== 分析配置 ==========
    # 分析输出目录
    ANALYSIS_OUTPUT_DIR = "./output/analysis"
    
    # 临时worktree目录
    ANALYSIS_WORKTREE_DIR = "/tmp/tubench_analysis_worktrees"
    
    # ========== 并发配置 ==========
    # 单项目内commit并发数
    ANALYSIS_WORKERS = 4
    
    # 单个版本执行时，可以并行执行4个版本
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
    
    # ========== 缓存配置 ==========
    # 是否启用缓存
    ENABLE_CACHE = True
    
    # 缓存目录
    CACHE_DIR = "./cache/analysis"
```

### 4.3 核心数据结构

#### 4.3.1 CommitAnalysisResult（单个Commit的完整分析结果）

```python
@dataclass
class CommitAnalysisResult:
    """单个Commit的完整分析结果 - 所有字段都会保存到JSON"""
    
    # ===== 基础信息 =====
    basic_info: dict
    # {
    #     "project": str,           # 项目名
    #     "commit_hash": str,       # 完整hash
    #     "short_hash": str,        # 短hash（8位）
    #     "parent_hash": str,       # 父commit hash
    #     "parent_short_hash": str, # 父commit短hash
    #     "author": str,            # 作者
    #     "author_email": str,      # 作者邮箱
    #     "date": str,              # 提交日期 (ISO格式)
    #     "message": str,           # 完整提交信息
    #     "message_subject": str    # 提交信息首行
    # }
    
    # ===== 文件变更信息 =====
    file_changes: dict
    # {
    #     "source_files": [
    #         {
    #             "path": str,              # 文件路径
    #             "change_type": str,       # added/modified/deleted/renamed
    #             "old_path": str|None,     # 重命名时的旧路径
    #             "additions": int,         # 新增行数
    #             "deletions": int,         # 删除行数
    #             "is_java": bool           # 是否为Java文件
    #         }
    #     ],
    #     "test_files": [...],              # 同上
    #     "other_files": [...],             # 同上
    #     "summary": {
    #         "total_files": int,
    #         "source_count": int,
    #         "test_count": int,
    #         "other_count": int,
    #         "total_additions": int,
    #         "total_deletions": int
    #     }
    # }
    
    # ===== 方法变更信息 =====
    method_changes: dict
    # {
    #     "source_methods": [
    #         {
    #             "file": str,                    # 文件路径
    #             "class_name": str,              # 简单类名
    #             "full_class_name": str,         # 完整类名（含包）
    #             "method_name": str,             # 方法名
    #             "signature": str,               # 方法签名
    #             "change_type": str,             # added/modified/deleted
    #             "start_line": int,              # 起始行
    #             "end_line": int,                # 结束行
    #             "changed_lines": List[int],     # 变更的行号
    #             "diff_snippet": str,            # 该方法的diff片段
    #             "modifiers": List[str],         # 修饰符 [public, static, ...]
    #             "return_type": str,             # 返回类型
    #             "parameters": List[str]         # 参数列表
    #         }
    #     ],
    #     "test_methods": [
    #         {
    #             # 同上，额外字段：
    #             "annotations": List[str],       # 注解 [@Test, @Before, ...]
    #             "is_test_method": bool,         # 是否为测试方法
    #             "test_name": str                # 测试名（用于结果匹配）
    #         }
    #     ],
    #     "summary": {
    #         "source_methods_count": int,
    #         "test_methods_count": int,
    #         "source_added": int,
    #         "source_modified": int,
    #         "source_deleted": int,
    #         "test_added": int,
    #         "test_modified": int,
    #         "test_deleted": int
    #     }
    # }
    
    # ===== Diff信息 =====
    diff_info: dict
    # {
    #     "full_diff": str,                # 完整diff文本
    #     "source_only_diff": str,         # 仅源代码diff（用于生成V-0.5）
    #     "test_only_diff": str,           # 仅测试代码diff（用于生成T-0.5）
    #     "stats": {
    #         "files_changed": int,
    #         "insertions": int,
    #         "deletions": int
    #     }
    # }
    
    # ===== V-1执行结果 =====
    v1_execution: dict
    # {
    #     "version": "v1",
    #     "commit_used": str,              # 实际使用的commit hash
    #     "worktree_path": str,            # worktree路径（调试用）
    #     "build": {
    #         "success": bool,
    #         "duration_seconds": float,
    #         "command": str,              # 执行的命令
    #         "return_code": int,
    #         "stdout": str,               # 标准输出（可能截断）
    #         "stderr": str,               # 标准错误（可能截断）
    #         "error_message": str|None    # 解析出的错误信息
    #     },
    #     "test": {
    #         "success": bool,
    #         "duration_seconds": float,
    #         "total_tests": int,
    #         "passed": int,
    #         "failed": int,
    #         "skipped": int,
    #         "errors": int,
    #         "failed_tests": [            # 失败的测试详情
    #             {
    #                 "class": str,
    #                 "method": str,
    #                 "full_name": str,
    #                 "failure_type": str,  # AssertionError, NullPointerException, ...
    #                 "message": str,
    #                 "stack_trace": str
    #             }
    #         ],
    #         "error_tests": [...],        # 出错的测试详情
    #         "test_report_path": str      # 测试报告路径
    #     },
    #     "coverage": {
    #         "available": bool,           # 是否成功收集覆盖率
    #         "line_coverage": float,      # 行覆盖率 (0-1)
    #         "branch_coverage": float,    # 分支覆盖率
    #         "method_coverage": float,    # 方法覆盖率
    #         "class_coverage": float,     # 类覆盖率
    #         "covered_lines": int,
    #         "total_lines": int,
    #         "covered_branches": int,
    #         "total_branches": int,
    #         "jacoco_report_path": str,   # JaCoCo报告路径
    #         # 针对变更方法的覆盖情况
    #         "changed_methods_coverage": [
    #             {
    #                 "method": str,           # 方法签名
    #                 "covered": bool,         # 是否被覆盖
    #                 "line_coverage": float,  # 该方法的行覆盖率
    #                 "covered_lines": List[int],
    #                 "uncovered_lines": List[int]
    #             }
    #         ]
    #     }
    # }
    
    # ===== V-0.5执行结果 =====
    v05_execution: dict
    # {
    #     "version": "v05",
    #     "description": "源代码已更新，测试代码未更新",
    #     "generation": {
    #         "method": "patch",           # 生成方式：patch应用
    #         "base_commit": str,          # 基于哪个commit（parent_hash）
    #         "patch_applied": bool,       # patch是否成功应用
    #         "patch_errors": str|None     # patch应用错误（如有）
    #     },
    #     "build": { ... },                # 同v1_execution.build
    #     "test": { ... },                 # 同v1_execution.test
    #     "coverage": { ... }              # 同v1_execution.coverage
    # }
    
    # ===== T-0.5执行结果 =====
    t05_execution: dict
    # {
    #     "version": "t05",
    #     "description": "测试代码已更新，源代码未更新",
    #     "generation": {
    #         "method": "patch",
    #         "base_commit": str,
    #         "patch_applied": bool,
    #         "patch_errors": str|None
    #     },
    #     "build": { ... },
    #     "test": {
    #         # 额外字段：
    #         "new_tests": List[str],      # V0相比V-1新增的测试
    #         "modified_tests": List[str], # V0相比V-1修改的测试
    #         "deleted_tests": List[str],  # V0相比V-1删除的测试
    #         ...
    #     },
    #     "coverage": { ... }
    # }
    
    # ===== V0执行结果 =====
    v0_execution: dict
    # 结构同v1_execution
    
    # ===== 分类结果 =====
    classification: dict
    # {
    #     "scenario": str,                 # A/B/C/D
    #     "scenario_description": str,     # 场景描述
    #     
    #     "type1_execution_error": {
    #         "detected": bool,
    #         "confidence": str,           # high/medium/low
    #         "subtype": str|None,         # compile_failure/runtime_failure
    #         "evidence": {
    #             "v05_build_success": bool,
    #             "v05_test_success": bool,
    #             "v0_test_success": bool,
    #             "failed_tests": [...],
    #             "compile_errors": [...],
    #             "t05_status": str        # T-0.5的状态，用于辅助判断
    #         }
    #     },
    #     
    #     "type2_coverage_decrease": {
    #         "detected": bool,
    #         "confidence": str,
    #         "evidence": {
    #             "v1_line_coverage": float,
    #             "v05_line_coverage": float,
    #             "coverage_diff": float,
    #             "v1_branch_coverage": float,
    #             "v05_branch_coverage": float,
    #             "uncovered_new_methods": [...],
    #             "coverage_decreased_methods": [...],
    #             "t05_coverage": float     # T-0.5的覆盖率，供参考
    #         }
    #     },
    #     
    #     "type3_adaptive_change": {
    #         "detected": bool,
    #         "confidence": str,
    #         "evidence": {
    #             "reason": str,           # 归类原因
    #             "scenario": str
    #         }
    #     },
    #     
    #     "all_types": List[str],          # 所有检测到的类型
    #     "primary_type": str,             # 主要类型
    #     "types_count": int               # 类型数量
    # }
    
    # ===== 测试-源代码关联 =====
    test_source_mapping: dict
    # {
    #     "mappings": [
    #         {
    #             "test_method": str,
    #             "likely_source_methods": List[str],
    #             "confidence": str,
    #             "evidence": {
    #                 "name_similarity": bool,
    #                 "coverage_overlap": bool,
    #                 "call_graph": bool
    #             }
    #         }
    #     ]
    # }
    
    # ===== 分析元数据 =====
    analysis_metadata: dict
    # {
    #     "analysis_timestamp": str,       # ISO格式时间戳
    #     "analysis_duration_seconds": float,
    #     "tubench_version": str,
    #     "phases_completed": List[str],   # 完成的阶段
    #     "errors_encountered": List[str], # 遇到的错误
    #     "warnings": List[str],           # 警告信息
    #     "cache_used": bool,              # 是否使用了缓存
    #     "worker_id": str|None            # 处理该commit的worker ID
    # }
```

#### 4.3.2 ProjectAnalysisResult（项目级汇总）

```python
@dataclass
class ProjectAnalysisResult:
    """单个项目的分析汇总结果"""
    
    # ===== 项目信息 =====
    project_info: dict
    # {
    #     "name": str,                     # 项目名
    #     "path": str,                     # 项目路径
    #     "git_url": str|None,             # Git仓库URL
    #     "default_branch": str,           # 默认分支
    #     "total_commits": int,            # 总commit数
    #     "date_range": {
    #         "earliest": str,             # 最早commit日期
    #         "latest": str,               # 最晚commit日期
    #         "filter_since": str          # 过滤起始日期
    #     }
    # }
    
    # ===== 过滤漏斗 =====
    filter_funnel: dict
    # {
    #     "stage0_total": int,             # 总commits数
    #     "stage1_after_date_filter": int, # 日期过滤后
    #     "stage2_has_test_and_source": int,  # 同时修改测试和源代码
    #     "stage3_has_method_changes": int,   # 有方法级变更
    #     "stage4_v1_build_success": int,     # V-1构建成功
    #     "stage5_v0_build_success": int,     # V0构建成功
    #     "stage6_qualified": int,            # 最终合格
    #     
    #     "filter_rates": {
    #         "date_filter": str,          # "75.5%"
    #         "file_change_filter": str,
    #         "method_change_filter": str,
    #         "v1_build_filter": str,
    #         "v0_build_filter": str,
    #         "overall": str               # 总体通过率
    #     },
    #     
    #     "rejection_reasons": {           # 被拒绝的原因统计
    #         "no_test_changes": int,
    #         "no_source_changes": int,
    #         "no_method_changes": int,
    #         "v1_compile_failed": int,
    #         "v1_test_failed": int,
    #         "v0_compile_failed": int,
    #         "v0_test_failed": int
    #     }
    # }
    
    # ===== 类型统计 =====
    type_statistics: dict
    # {
    #     "type1_execution_error": {
    #         "count": int,
    #         "percentage": str,
    #         "subtypes": {
    #             "compile_failure": int,
    #             "runtime_failure": int
    #         },
    #         "examples": [str, str, str]  # 3个示例commit hash
    #     },
    #     "type2_coverage_decrease": {
    #         "count": int,
    #         "percentage": str,
    #         "avg_coverage_decrease": float,
    #         "max_coverage_decrease": float,
    #         "examples": [str, str, str]
    #     },
    #     "type3_adaptive_change": {
    #         "count": int,
    #         "percentage": str,
    #         "examples": [str, str, str]
    #     },
    #     "overlap": {
    #         "type1_only": int,
    #         "type2_only": int,
    #         "type3_only": int,
    #         "type1_and_type2": int,
    #         "type1_and_type3": int,
    #         "type2_and_type3": int,
    #         "all_types": int
    #     },
    #     "scenario_distribution": {
    #         "A": int,
    #         "B": int,
    #         "C": int,
    #         "D": int
    #     }
    # }
    
    # ===== 执行统计 =====
    execution_statistics: dict
    # {
    #     "v05_results": {
    #         "compile_success": int,
    #         "compile_failed": int,
    #         "test_success": int,
    #         "test_failed": int,
    #         "avg_test_duration": float
    #     },
    #     "t05_results": {
    #         "compile_success": int,
    #         "compile_failed": int,
    #         "test_success": int,
    #         "test_failed": int
    #     },
    #     "coverage_statistics": {
    #         "v1_avg_coverage": float,
    #         "v05_avg_coverage": float,
    #         "t05_avg_coverage": float,
    #         "v0_avg_coverage": float
    #     }
    # }
    
    # ===== Commits列表 =====
    qualified_commits: List[str]  # 合格commit的hash列表
    
    # ===== 分析元数据 =====
    analysis_metadata: dict
    # {
    #     "analysis_start_time": str,
    #     "analysis_end_time": str,
    #     "total_duration_seconds": float,
    #     "workers_used": int,
    #     "commits_analyzed": int,
    #     "commits_from_cache": int,
    #     "errors_count": int
    # }
```

---

## 5. 分析流程

### 5.1 总体流程

```
┌─────────────────────────────────────────────────────────────────┐
│                     analysis.py 主流程                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Phase 0: 初始化                                                 │
│ - 解析命令行参数                                                │
│ - 验证项目路径                                                  │
│ - 初始化日志、输出目录、缓存                                    │
│ - 预检查：Git仓库状态、Maven可用性                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Phase 1: 快速扫描 (Quick Scan)                                  │
│ 耗时: 秒级 | 无需checkout | 可独立运行                          │
│                                                                 │
│ - 获取所有commits（按日期过滤）                                 │
│ - 通过git show --stat快速检查文件变更                           │
│ - 筛选同时修改测试和源代码的commits                             │
│                                                                 │
│ 输出: candidate_commits[]                                       │
│ 保存: phase1_candidates.json                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Phase 2: 方法分析 (Method Analysis)                             │
│ 耗时: 分钟级 | 需要读取文件内容 | 可独立运行                    │
│                                                                 │
│ 对每个candidate_commit:                                         │
│ - 获取详细diff                                                  │
│ - 解析Java代码，识别变更的类和方法                              │
│ - 分离source_only_diff和test_only_diff                          │
│ - 分析测试方法的变更内容                                        │
│                                                                 │
│ 输出: method_analyzed_commits[]                                 │
│ 保存: phase2_method_analysis.json                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Phase 3: 执行分析 (Execution Analysis) 【核心阶段】             │
│ 耗时: 小时级 | 需要构建和执行测试 | 并发执行                    │
│                                                                 │
│ 使用ProcessPoolExecutor并发处理commits:                         │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 对每个commit (并发):                                        │ │
│ │                                                             │ │
│ │ 3.1 创建4个隔离worktree                                     │ │
│ │     - worktree_v1  = checkout(parent_hash)                  │ │
│ │     - worktree_v05 = checkout(parent) + apply(src_diff)     │ │
│ │     - worktree_t05 = checkout(parent) + apply(test_diff)    │ │
│ │     - worktree_v0  = checkout(commit_hash)                  │ │
│ │                                                             │ │
│ │ 3.2 并行执行4个版本 (可选，根据配置)                        │ │
│ │     - V-1:  compile → test → coverage                       │ │
│ │     - V-0.5: compile → test → coverage                      │ │
│ │     - T-0.5: compile → test → coverage                      │ │
│ │     - V0:   compile → test → coverage                       │ │
│ │                                                             │ │
│ │ 3.3 收集执行结果                                            │ │
│ │                                                             │ │
│ │ 3.4 清理worktree                                            │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ 输出: execution_results[]                                       │
│ 保存: 每个commit单独保存到 commits/{hash}.json                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Phase 4: 分类判定 (Classification)                              │
│ 耗时: 秒级 | 基于Phase 3的结果                                  │
│                                                                 │
│ 对每个execution_result:                                         │
│ - 判定场景 (A/B/C/D)                                            │
│ - 检测Type1 (执行出错)                                          │
│ - 检测Type2 (覆盖率降低)                                        │
│ - 检测Type3 (适应性调整 = 非Type1且非Type2)                     │
│                                                                 │
│ 输出: classified_commits[]                                      │
│ 保存: 更新 commits/{hash}.json                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Phase 5: 报告生成 (Report Generation)                           │
│                                                                 │
│ - 生成项目级汇总: analysis_result.json                          │
│ - 生成可读报告: summary.md                                      │
│ - 如果是多项目，生成全局汇总                                    │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 单个Commit的详细处理流程

```
process_single_commit(commit_hash):
    │
    ├── 1. 基础信息收集
    │   ├── git_analyzer.get_commit_info(commit_hash)
    │   └── git_analyzer.get_changed_files(commit_hash)
    │
    ├── 2. 方法变更分析
    │   ├── diff_filter.filter_test_changes(full_diff)
    │   │   └── 得到 source_only_diff, test_only_diff
    │   ├── code_analyzer.parse_java_file(file_content)
    │   └── change_detector.detect_changed_methods(...)
    │
    ├── 3. 版本执行 (isolated_executor)
    │   │
    │   ├── 3.1 执行V-1
    │   │   ├── create_worktree(parent_hash, path_v1)
    │   │   ├── maven_executor.compile(path_v1)
    │   │   ├── maven_executor.test_with_jacoco(path_v1)
    │   │   ├── coverage_analyzer.parse_report(path_v1)
    │   │   └── cleanup_worktree(path_v1)
    │   │
    │   ├── 3.2 执行V-0.5
    │   │   ├── create_worktree(parent_hash, path_v05)
    │   │   ├── apply_patch(source_only_diff, path_v05)
    │   │   ├── maven_executor.compile(path_v05)
    │   │   │   └── 如果失败 → Type1 (compile_failure)
    │   │   ├── maven_executor.test_with_jacoco(path_v05)
    │   │   │   └── 如果失败 → Type1 (runtime_failure)
    │   │   ├── coverage_analyzer.parse_report(path_v05)
    │   │   │   └── 对比V-1 → 可能Type2
    │   │   └── cleanup_worktree(path_v05)
    │   │
    │   ├── 3.3 执行T-0.5
    │   │   ├── create_worktree(parent_hash, path_t05)
    │   │   ├── apply_patch(test_only_diff, path_t05)
    │   │   ├── maven_executor.compile(path_t05)
    │   │   ├── maven_executor.test_with_jacoco(path_t05)
    │   │   ├── coverage_analyzer.parse_report(path_t05)
    │   │   └── cleanup_worktree(path_t05)
    │   │
    │   └── 3.4 执行V0
    │       ├── create_worktree(commit_hash, path_v0)
    │       ├── maven_executor.compile(path_v0)
    │       ├── maven_executor.test_with_jacoco(path_v0)
    │       ├── coverage_analyzer.parse_report(path_v0)
    │       └── cleanup_worktree(path_v0)
    │
    ├── 4. 分类判定 (commit_classifier)
    │   ├── determine_scenario(v05_result, t05_result)
    │   ├── detect_type1(v05_result, t05_result, v0_result)
    │   ├── detect_type2(v1_result, v05_result, t05_result)
    │   └── detect_type3(is_type1, is_type2)
    │
    └── 5. 保存结果
        └── save_commit_result(commit_hash, result)
```

---

## 6. 新增模块详细设计

### 6.1 isolated_executor.py

```python
"""
隔离执行器 - 在临时worktree中执行构建和测试，不污染原始仓库
"""

class IsolatedExecutor:
    """隔离执行器"""
    
    def __init__(self, repo_path: str, work_dir: str = None):
        """
        初始化
        
        Args:
            repo_path: 原始仓库路径
            work_dir: 工作目录，默认为 /tmp/tubench_analysis_worktrees
        """
        pass
    
    def execute_version(self, 
                       commit_hash: str,
                       version_type: str,  # 'v1', 'v05', 't05', 'v0'
                       patch_content: str = None) -> dict:
        """
        在隔离环境中执行指定版本
        
        Args:
            commit_hash: 基础commit hash
            version_type: 版本类型
            patch_content: 需要应用的patch（v05和t05需要）
            
        Returns:
            执行结果字典
        """
        pass
    
    def _create_worktree(self, commit_hash: str, worktree_path: str) -> bool:
        """创建git worktree"""
        pass
    
    def _apply_patch(self, patch_content: str, worktree_path: str) -> dict:
        """应用patch到worktree"""
        pass
    
    def _run_maven_compile(self, worktree_path: str) -> dict:
        """执行Maven编译"""
        pass
    
    def _run_maven_test(self, worktree_path: str) -> dict:
        """执行Maven测试并收集覆盖率"""
        pass
    
    def _cleanup_worktree(self, worktree_path: str):
        """清理worktree"""
        pass
    
    def cleanup_all(self):
        """清理所有临时文件"""
        pass
```

### 6.2 commit_classifier.py

```python
"""
Commit分类器 - 基于执行结果进行三种类型分类
"""

class CommitClassifier:
    """Commit分类器"""
    
    def __init__(self, coverage_threshold: float = 0.02):
        """
        初始化
        
        Args:
            coverage_threshold: 覆盖率下降阈值，默认2%
        """
        pass
    
    def classify(self, 
                v1_result: dict,
                v05_result: dict,
                t05_result: dict,
                v0_result: dict) -> dict:
        """
        对commit进行分类
        
        Returns:
            分类结果字典
        """
        pass
    
    def _determine_scenario(self, v05_result: dict, t05_result: dict) -> str:
        """确定场景 (A/B/C/D)"""
        pass
    
    def _detect_type1(self, 
                     v05_result: dict,
                     t05_result: dict,
                     v0_result: dict) -> dict:
        """检测Type1: 执行出错"""
        pass
    
    def _detect_type2(self,
                     v1_result: dict,
                     v05_result: dict,
                     t05_result: dict) -> dict:
        """检测Type2: 覆盖率降低"""
        pass
    
    def _detect_type3(self, is_type1: bool, is_type2: bool) -> dict:
        """检测Type3: 适应性调整（兜底）"""
        pass
```

### 6.3 analysis/project_analyzer.py

```python
"""
项目分析器 - 负责分析单个项目的所有commits
"""

class ProjectAnalyzer:
    """项目分析器"""
    
    def __init__(self, 
                 project_path: str,
                 output_dir: str,
                 workers: int = 4,
                 resume: bool = False):
        """
        初始化
        
        Args:
            project_path: 项目路径
            output_dir: 输出目录
            workers: 并发worker数
            resume: 是否断点续传
        """
        pass
    
    def analyze(self, 
               since_date: str = None,
               sample: int = None,
               phase: str = 'full') -> ProjectAnalysisResult:
        """
        执行分析
        
        Args:
            since_date: 起始日期
            sample: 采样数量
            phase: 执行阶段 ('quick', 'method', 'full')
            
        Returns:
            项目分析结果
        """
        pass
    
    def _phase1_quick_scan(self, commits) -> List[str]:
        """Phase 1: 快速扫描"""
        pass
    
    def _phase2_method_analysis(self, candidates) -> List[dict]:
        """Phase 2: 方法分析"""
        pass
    
    def _phase3_execution_analysis(self, analyzed_commits) -> List[dict]:
        """Phase 3: 执行分析（并发）"""
        pass
    
    def _phase4_classification(self, execution_results) -> List[dict]:
        """Phase 4: 分类判定"""
        pass
    
    def _phase5_report_generation(self, classified_commits):
        """Phase 5: 报告生成"""
        pass
```

### 6.4 analysis/commit_analyzer.py

```python
"""
Commit分析器 - 负责分析单个commit的完整信息
"""

class CommitAnalyzer:
    """单个Commit分析器"""
    
    def __init__(self, 
                 repo_path: str,
                 output_dir: str):
        """初始化"""
        pass
    
    def analyze(self, commit_hash: str) -> CommitAnalysisResult:
        """
        分析单个commit
        
        Args:
            commit_hash: commit hash
            
        Returns:
            完整分析结果
        """
        pass
    
    def _collect_basic_info(self, commit_hash: str) -> dict:
        """收集基础信息"""
        pass
    
    def _analyze_file_changes(self, commit_hash: str) -> dict:
        """分析文件变更"""
        pass
    
    def _analyze_method_changes(self, commit_hash: str, file_changes: dict) -> dict:
        """分析方法变更"""
        pass
    
    def _execute_versions(self, commit_hash: str, diff_info: dict) -> dict:
        """执行4个版本"""
        pass
    
    def _classify(self, execution_results: dict) -> dict:
        """分类"""
        pass
```

### 6.5 analysis/report_generator.py

```python
"""
报告生成器 - 生成各种格式的分析报告
"""

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, output_dir: str):
        """初始化"""
        pass
    
    def generate_project_summary_json(self, 
                                      result: ProjectAnalysisResult,
                                      output_path: str):
        """生成项目JSON摘要"""
        pass
    
    def generate_project_summary_markdown(self,
                                          result: ProjectAnalysisResult,
                                          output_path: str):
        """生成项目Markdown报告"""
        pass
    
    def generate_commit_detail_json(self,
                                    result: CommitAnalysisResult,
                                    output_path: str):
        """生成commit详细JSON"""
        pass
    
    def generate_global_summary(self,
                               project_results: List[ProjectAnalysisResult],
                               output_dir: str):
        """生成全局汇总报告"""
        pass
```

---

## 7. 输出示例

### 7.1 项目Markdown报告示例 (summary.md)

```markdown
# Commons-CSV 分析报告

## 项目信息
- **项目名**: commons-csv
- **路径**: /work/defects4j-projects/commons-csv
- **分析日期**: 2026-01-23
- **分析耗时**: 2小时15分钟

## 过滤漏斗

| 阶段 | 数量 | 通过率 |
|------|------|--------|
| 总Commits | 1,234 | - |
| 日期过滤后 (≥2016-01-01) | 856 | 69.4% |
| 同时修改测试和源代码 | 312 | 36.4% |
| 有方法级变更 | 278 | 89.1% |
| V-1构建成功 | 265 | 95.3% |
| V0构建成功 | 258 | 97.4% |
| **最终合格** | **258** | **20.9%** |

## 类型分布

| 类型 | 数量 | 占比 | 说明 |
|------|------|------|------|
| Type1 (执行出错) | 85 | 32.9% | V-0.5编译或测试失败 |
| ├─ 编译失败 | 23 | 8.9% | |
| └─ 运行时失败 | 62 | 24.0% | |
| Type2 (覆盖率降低) | 67 | 26.0% | V-0.5变更方法覆盖率下降 |
| Type3 (适应性调整) | 142 | 55.0% | 其他情况 |

### 重叠统计
- 仅Type1: 45
- 仅Type2: 31
- 仅Type3: 106
- Type1 + Type2: 24
- Type1 + Type3: 16
- Type2 + Type3: 12
- 全部三种: 24

## 场景分布

| 场景 | V-0.5 | T-0.5 | 数量 | 占比 |
|------|-------|-------|------|------|
| A | ❌失败 | ❌失败 | 45 | 17.4% |
| B | ❌失败 | ✅通过 | 40 | 15.5% |
| C | ✅通过 | ❌失败 | 52 | 20.2% |
| D | ✅通过 | ✅通过 | 121 | 46.9% |

## 示例Commits

### Type1 示例 (执行出错)
1. **abc12345** - 2024-03-15 - "Fix CSV parsing for quoted fields"
   - 失败测试: `CSVParserTest.testParseQuotedFields`
   - 错误信息: `AssertionError: expected:<5> but was:<6>`

2. **def67890** - 2024-02-20 - "Add new parse options"
   - 编译错误: `cannot find symbol: method parseNew(...)`

### Type2 示例 (覆盖率降低)
1. **ghi11111** - 2024-01-10 - "Refactor CSVFormat"
   - V-1覆盖率: 85.2%
   - V-0.5覆盖率: 78.6%
   - 下降: 6.6%

## 合格Commits列表

<details>
<summary>点击展开完整列表 (258个)</summary>

| # | Hash | 日期 | 类型 | 场景 |
|---|------|------|------|------|
| 1 | abc12345 | 2024-03-15 | Type1 | A |
| 2 | def67890 | 2024-02-20 | Type1,Type2 | A |
| ... | ... | ... | ... | ... |

</details>
```

---

## 8. 开发计划

### 8.1 阶段一：基础框架 (预计2天)
- [ ] 创建 `analysis.py` 主入口和命令行解析
- [ ] 扩展 `config.py` 添加分析配置
- [ ] 创建 `analysis/` 目录结构
- [ ] 实现基础的 `ProjectAnalyzer` 框架

### 8.2 阶段二：核心执行模块 (预计3天)
- [ ] 实现 `isolated_executor.py` - 隔离执行器
- [ ] 增强 `maven_executor.py` - 添加测试结果解析
- [ ] 增强 `coverage_analyzer.py` - 添加覆盖率对比功能
- [ ] 实现 `commit_classifier.py` - 三类型分类器

### 8.3 阶段三：分析流程 (预计2天)
- [ ] 实现 `commit_analyzer.py` - 单commit完整分析
- [ ] 实现 Phase 1-5 的完整流程
- [ ] 实现并发处理和断点续传

### 8.4 阶段四：报告生成 (预计1天)
- [ ] 实现 `report_generator.py`
- [ ] JSON输出格式
- [ ] Markdown报告生成

### 8.5 阶段五：测试和优化 (预计2天)
- [ ] 单元测试
- [ ] 在commons-csv上进行端到端测试
- [ ] 性能优化
- [ ] 文档完善

### 总计：约10个工作日

---

## 9. 待确认事项

1. ✅ 四个版本都需要执行
2. ✅ 分类逻辑：Type1 → Type2 → Type3（兜底）
3. ✅ T-0.5用于辅助分析
4. ✅ 合格标准已明确
5. ✅ 并发针对单项目内的commits
6. ✅ 输出需要完整详细信息

---

*文档版本: 1.0*
*创建日期: 2026-01-23*
*最后更新: 2026-01-23*
