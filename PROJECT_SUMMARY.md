测试演化数据集构建工具 - 项目完成报告
===========================================

## 项目概述

成功构建了一个自动化工具，用于从Java Maven项目的Git历史中提取和构建测试演化数据集。该工具能够识别同时修改测试代码和源代码的commits，并为每个commit生成四个版本（V-1、V-0.5、T-0.5、V0），其中V-0.5模拟“缺少测试更新”，T-0.5模拟“仅测试更新”。

## 完成状态

### ✅ 已完成功能

1. **初始筛选流程** (main.py)
   - 自动分析Git提交历史
   - 多条件过滤（测试+源代码同时修改、构建成功、覆盖率≥50%）
   - 方法级别的变更检测
   - 并行处理和断点续传支持

2. **Diff过滤模块** (diff_filter.py)
   - 自定义正则表达式解析Git diff
   - 按文件类型分离diff（测试文件 vs 源文件）
   - 生成只包含源代码变更的patch

3. **过滤版本生成** (filtered_version_generator.py)
   - 自动创建Git分支
   - 应用过滤后的patch
   - 编译验证
   - 生成V-0.5（仅源代码）与 T-0.5（仅测试代码）

4. **批处理脚本** (generate_filtered_versions.py)
   - 批量处理所有合格commits
   - 失败处理和统计
   - JSON数据集生成

5. **测试脚本** (test_diff_filter.py)
   - 验证diff过滤功能
   - 单个commit测试

## 实施结果

### Commons-CSV项目数据集（示例）

- **仓库**: Apache Commons CSV
- **分析时间范围**: 2016-01-01 至今
- **总commits数**: 164个
- **初始筛选通过**: 130个 (79.3%)
- **V-0.5/T-0.5 生成成功**: 以 `filtered_dataset.json` 的 `metadata` 统计为准
- **最终可用数据**: 四版本数据点（含 V-0.5 与 T-0.5）

### 成功率分析（字段级统计）

元数据中分别统计 `source_only` 与 `test_only` 的成功率，便于独立分析两类版本的构建情况。

### 失败原因

**初始筛选失败 (34个)**
- 只修改测试或源代码（不是同时修改）
- 构建失败
- 覆盖率不达标（<50%）

**V-0.5/T-0.5生成失败**
- 编译失败（常见原因：JDK版本不兼容）
- Patch应用失败
- 其他错误

## 技术实现

### 核心模块架构

```
modules/
├── git_analyzer.py              # Git仓库操作和commit分析
├── code_analyzer.py             # Java代码解析（基于javalang）
├── change_detector.py           # 方法级变更检测
├── maven_executor.py            # Maven构建和测试执行
├── coverage_analyzer.py         # JaCoCo覆盖率分析
├── commit_filter.py             # 多条件commit过滤
├── dataset_generator.py         # JSON数据集生成
├── diff_filter.py               # Diff过滤（新增）
└── filtered_version_generator.py # V-0.5/T-0.5版本生成（新增）
```

### 版本关系模型

```
V-1 (父commit)
  ├──> V-0.5 (仅源代码变更)
  └──> T-0.5 (仅测试代码变更)
                 └──> V0 (完整版本)
```

**V-1**: 父commit，作为baseline
**V-0.5**: 过滤版本，只包含源代码变更（模拟缺少测试更新）
**T-0.5**: 测试版本，只包含测试代码变更（模拟仅测试更新）
**V0**: 完整版本，包含所有变更（源代码+测试代码）

### 技术亮点

#### 1. 自定义Diff解析器

**问题**: unidiff库无法解析GitPython生成的diff格式，导致100%失败率

**解决方案**: 
- 使用正则表达式 `r'(diff --git [^\n]+\n)'` 分割diff
- 手动解析文件路径和变更内容
- 根据路径模式判断文件类型

**效果**: 成功率显著提升（以实际运行统计为准）

#### 2. 编译验证机制

每个生成的 V-0.5/T-0.5 版本都经过Maven编译验证，确保：
- 源代码可编译
- 依赖关系正确
- 语法无错误

#### 3. Git分支管理

- 每个V-0.5版本创建独立分支（`filtered/{commit_hash[:8]}`）
- 每个T-0.5版本创建独立分支（`test-only/{commit_hash[:8]}`）
- 便于追溯和对比
- 支持并行研究

## 输出文件

### 1. dataset.json
初始筛选结果，包含130个合格commits的详细信息。

### 2. filtered_dataset.json
最终数据集，包含 V-0.5 与 T-0.5 信息的四版本数据点。

**数据结构（示例，数值仅示意）**:
```json
{
  "metadata": {
    "total_processed": 130,
    "source_only": {
      "successful": 125,
      "success_rate": "96.15%"
    },
    "test_only": {
      "successful": 123,
      "success_rate": "94.62%"
    }
  },
  "commits": [
    {
      "original_commit": "V0的commit hash",
      "parent_commit": "V-1的commit hash",
      "filtered_version": {
        "success": true,
        "filtered_commit_hash": "V-0.5的commit hash",
        "branch_name": "filtered/..."
      },
      "test_only_version": {
        "success": true,
        "test_only_commit_hash": "T-0.5的commit hash",
        "branch_name": "test-only/..."
      },
      "changed_files": {...},
      "changed_methods": {...},
      "coverage_analysis": {...}
    }
  ]
}
```

### 3. Git分支
在commons-csv仓库中创建分支：
- 命名格式: `filtered/{commit_hash[:8]}` 与 `test-only/{commit_hash[:8]}`
- 分别指向对应的 V-0.5 / T-0.5 版本
- 可通过 `git branch | grep filtered/` 与 `git branch | grep test-only/` 查看

## 应用场景

### 1. 测试演化研究
分析测试用例如何随源代码演化，研究测试更新的模式和策略。

### 2. 测试生成
基于V-0.5版本自动生成测试，与V0版本的测试对比，评估测试生成工具的效果。

### 3. 测试修复
检测和修复不完整的测试更新，提高测试维护质量。

### 4. 覆盖率分析
分析代码变更对覆盖率的影响，优化测试策略。

### 5. 代码理解
研究代码变更与测试的关系，辅助代码审查和质量保证。

## 使用指南

### 环境要求
- Python 3.8+
- Git
- Maven
- JDK (与项目兼容的版本)

### 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置仓库路径
# 编辑 config.py，设置 REPO_PATH

# 3. 运行初始筛选
python main.py

# 4. 生成过滤版本（V-0.5/T-0.5）
python generate_filtered_versions.py output/dataset.json output/filtered_dataset.json

# 5. 查看结果
cat output/filtered_dataset.json | jq '.metadata'
```

### 查看生成的分支

```bash
cd /path/to/your/java-project
git branch | grep "filtered/"
git branch | grep "test-only/"
git log filtered/d93c4940
```

### 对比版本差异

```bash
# V-0.5 vs V0 (应主要是测试文件的差异)
git diff ab0f7745 d93c4940

# V-1 vs V-0.5 (应主要是源代码的差异)
git diff c36d6cde ab0f7745

# V-1 vs T-0.5 (应主要是测试代码的差异)
git diff c36d6cde 5e5d1c2a

# T-0.5 vs V0 (应主要是源代码的差异)
git diff 5e5d1c2a d93c4940
```

## 配置说明

### config.py

```python
class Config:
    # Git仓库路径
    REPO_PATH = "/path/to/your/java-project"
    
    # 日期过滤（只分析此日期后的commits）
    DATE_FILTER = "2016-01-01"
    
    # 覆盖率阈值（50%的测试需要覆盖变更的方法）
    COVERAGE_THRESHOLD = 0.5
    
    # 并行worker数量
    PARALLEL_WORKERS = 4
    
    # 测试代码路径模式
    TEST_PATH_PATTERNS = ["src/test/java", "test/java", "src/test"]
    
    # Maven设置
    MAVEN_TIMEOUT = 600
    JACOCO_VERSION = "0.8.11"
```

## 注意事项

1. **仓库状态**: 运行前确保Git仓库clean（无未提交的变更）
2. **JDK版本**: 确保安装了与项目兼容的JDK版本
3. **磁盘空间**: 生成的分支会占用额外的磁盘空间
4. **处理时间**: 初始筛选可能需要较长时间（取决于commits数量）
5. **网络连接**: Maven需要下载依赖，确保网络畅通

## 已知限制

1. **JDK版本兼容性**: 旧项目（使用Java 6/7）可能在新JDK上编译失败
2. **Maven clean失败**: 偶尔会遇到文件被占用的情况
3. **只支持Maven项目**: 不支持Gradle等其他构建工具
4. **Java语言限制**: 只支持Java项目

## 未来改进方向

1. 支持Gradle项目
2. 支持其他编程语言（Python, JavaScript等）
3. 增加更多的过滤条件
4. 优化处理速度
5. 提供Web界面

## 依赖项

```
GitPython==3.1.40      # Git仓库操作
javalang==0.13.0       # Java代码解析
lxml==5.1.0            # XML解析（JaCoCo报告）
```

注意：已移除 `unidiff==0.7.5`，改用自定义正则表达式解析。

## 项目统计

- **代码行数**: ~2000行Python代码
- **模块数量**: 9个核心模块
- **测试脚本**: 1个
- **开发时间**: 约2天
- **构建成功率**: 见 `filtered_dataset.json` 的 `metadata`（`source_only`/`test_only`）

## 总结

该项目成功实现了测试演化数据集的自动化构建，从Git历史中提取了高质量的四版本数据点（含 V-0.5 与 T-0.5）。工具具有良好的可扩展性和稳定性，可以应用于其他Java Maven项目。

关键成就：
✅ 自动化的端到端流程
✅ 高成功率（以实际运行统计为准）
✅ 清晰的版本关系模型
✅ 完整的数据集导出
✅ 良好的文档和示例

该数据集可用于测试演化、测试生成、测试修复等多个研究方向，为相关领域提供了宝贵的实验数据。

---

**项目状态**: ✅ 已完成
**最后更新**: 2025-12-16
**版本**: 1.0
