# 测试演化数据集构建工具

这是一个用于构建测试演化数据集的Python工具，专门用于分析Java Maven项目的Git历史，筛选出符合条件的commits并生成结构化数据集。

## 功能特点

- 自动分析Git提交历史
- 识别测试代码和被测代码的变更
- 执行测试并分析覆盖率（基于JaCoCo）
- 智能过滤符合条件的commits
- **生成隐藏测试变更的版本（V-0.5）**
- 支持并行处理加速分析
- 支持断点续传

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 配置

编辑 `config.py` 文件，设置以下参数：

```python
# Git仓库路径
REPO_PATH = "/path/to/your/java/project"

# 日期过滤（只分析此日期后的commits）
DATE_FILTER = "2016-01-01"

# 覆盖率阈值（50%的测试需要覆盖变更的被测方法）
COVERAGE_THRESHOLD = 0.5

# 并行worker数量
PARALLEL_WORKERS = 4
```

### 2. 运行

```bash
# 方式1: 在config.py中设置REPO_PATH后运行
python main.py

# 方式2: 通过命令行参数指定仓库路径
python main.py /path/to/your/java/project
```

### 3. 输出

工具会生成以下文件：

- `output/dataset.json` - 最终的数据集
- `output/intermediate_results.json` - 中间结果（支持断点续传）
- `output/dataset_builder.log` - 详细日志

## 数据集格式

### 初步筛选数据集 (dataset.json)

```json
{
  "metadata": {
    "generated_at": "2025-12-15 10:30:00",
    "total_commits": 100,
    "qualified_commits": 25
  },
  "commits": [
    {
      "commit_hash": "abc123...",
      "parent_hash": "def456...",
      "author": "John Doe",
      "date": "2024-01-01 12:00:00",
      "message": "Fix bug in UserService",
      "changed_files": {
        "test_files": ["src/test/java/..."],
        "source_files": ["src/main/java/..."]
      },
      "changed_methods": {
        "test_methods": [...],
        "source_methods": [...]
      },
      "coverage_analysis": {
        "parent_commit": {...},
        "child_commit": {...}
      },
      "build_status": {
        "parent_success": true,
        "child_success": true
      },
      "qualified": true,
      "filter_reasons": []
    }
  ]
}
```

### 过滤版本数据集 (filtered_dataset.json)

```json
{
  "metadata": {
    "source_dataset": "output/dataset.json",
    "total_processed": 25,
    "successful": 20,
    "failed": {
      "apply_patch": 3,
      "compilation": 1,
      "other": 1
    },
    "success_rate": "80.00%"
  },
  "commits": [
    {
      "original_commit": "abc123...",  // V0
      "parent_commit": "def456...",     // V-1
      "filtered_version": {
        "success": true,
        "filtered_commit_hash": "xyz789...",  // V-0.5
        "branch_name": "filtered/abc12345",
        "test_changes_hidden": {
          "files": [...],
          "total_lines_added": 50,
          "total_lines_removed": 10
        },
        "filter_stats": {
          "source_files": 2,
          "test_files": 1
        }
      }
    }
  ]
}
```

## 工作流程

### 阶段1: 初步筛选

1. **提取Commits** - 获取指定日期后的所有commits
2. **快速预筛选** - 过滤出同时修改了测试和源代码的commits
3. **详细分析** - 对每个commit：
   - 识别变更的方法（测试方法和被测方法）
   - 在父commit和子commit中执行测试
   - 使用JaCoCo分析覆盖率
   - 判断测试是否覆盖变更的被测方法
4. **应用过滤条件**：
   - 必须同时修改测试和源代码
   - 必须有明确的方法级别变更
   - 父commit和子commit都能成功构建
   - 至少50%的变更测试覆盖了变更的被测方法
5. **生成数据集** - 输出JSON格式的结构化数据

### 阶段2: 生成过滤版本

```
原始: V-1 (parent) → V0 (child, 包含测试+源代码变更)
               ↓
          过滤diff (移除测试变更)
               ↓
      V-1 → V-0.5 (只包含源代码变更)
```

6. **Diff过滤** - 分离源代码和测试代码的变更
7. **创建分支** - 从V-1创建新分支并应用filtered diff
8. **验证编译** - 确保V-0.5可以成功编译
9. **记录信息** - 保存分支名、commit hash、隐藏的测试变更等
10. **生成最终数据集** - 包含V-1、V-0.5、V0的完整信息

## 项目结构

```
test_evolution_dataset/
├── main.py                 # 主程序
├── config.py              # 配置文件
├── requirements.txt       # Python依赖
├── modules/               # 核心模块
│   ├── git_analyzer.py
│   ├── code_analyzer.py
│   ├── change_detector.py
│   ├── maven_executor.py
│   ├── coverage_analyzer.py
│   ├── commit_filter.py
│   └── dataset_generator.py
├── utils/                 # 工具模块
│   ├── logger.py
│   └── pom_modifier.py
└── output/               # 输出目录
```

## 注意事项

1. 确保系统已安装Maven（`mvn`命令可用）
2. 项目必须是符合Maven标准的Java项目
3. 处理大型项目时可能需要较长时间
4. 建议在服务器上运行以充分利用并行处理能力
5. 支持断点续传，可随时中断和恢复

## 许可证

MIT
