# 过滤版本生成器修复说明

## 修复的问题

### 问题1: Commit Message不完整
**原问题**: V-0.5版本的commit message没有包含原V0版本的完整内容

**修复方案**:
- 直接从Git获取原始commit的完整message (`commit.message`)
- 保持原始message在前，在末尾添加标识说明
- 格式: `{原始完整message}\n\n[Filtered Version - Source Code Changes Only]`

**代码修改**:
```python
# 获取原始commit的完整message
original_commit = self.repo.commit(commit_hash)
original_message = original_commit.message.strip()

# 创建新commit message
commit_message = f"{original_message}\n\n[Filtered Version - Source Code Changes Only]"
```

### 问题2: 工作区存在编译产物
**原问题**: 新创建的分支中包含target/目录等编译中间产物

**修复方案**:
1. 在创建分支前清理工作区: `git reset --hard && git clean -fd`
2. 在创建分支后再次清理: `git reset --hard && git clean -fd`
3. 在编译验证前清理: `git reset --hard && git clean -fd`
4. 在编译验证成功后删除target目录: `shutil.rmtree('target')`

**代码修改**:
```python
# 1. 创建分支前严格清理
self.repo.git.reset('--hard')
self.repo.git.clean('-fd')

# 2. 创建分支后再次清理
self.repo.git.checkout('-b', branch_name, parent_hash)
self.repo.git.reset('--hard')
self.repo.git.clean('-fd')

# 3. 编译验证后删除target
if success:
    target_dir = os.path.join(self.repo.working_dir, 'target')
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
```

## 验证结果

### 测试用例
- Commit: d93c4940 (CSVParser.parse with null Charset)
- Parent: c36d6cde

### 验证1: Commit Message
```
✓ 包含原始完整message
✓ 包含标识说明 [Filtered Version - Source Code Changes Only]
```

原始V0的message:
```
CSVParser.parse(*) methods with a null Charset maps to
Charset.defaultCharset()

Javadoc
```

新V-0.5的message:
```
CSVParser.parse(*) methods with a null Charset maps to
Charset.defaultCharset()

Javadoc

[Filtered Version - Source Code Changes Only]
```

### 验证2: 工作区清理
```
✓ target目录已清理
✓ 无未跟踪文件
✓ git status --short 输出为空
```

### 验证3: 版本差异
V-0.5和V0之间的差异只包含测试文件的变更：
```bash
$ git diff f4f5a229 d93c4940 --stat
 src/test/java/org/apache/commons/csv/CSVParserTest.java | 14 ++++++++------
 1 file changed, 8 insertions(+), 6 deletions(-)
```

## 修改的文件

- `modules/filtered_version_generator.py`
  - `generate_filtered_version()`: 获取原始commit的完整message
  - `_apply_filtered_diff()`: 增强工作区清理，使用原始message
  - `_verify_compilable()`: 编译后删除target目录

## 影响范围

这些修复会影响所有新生成的V-0.5版本：

1. **Commit Message**: 所有V-0.5版本都将包含完整的原始message
2. **工作区清理**: 所有V-0.5版本都将是干净的，无编译产物
3. **向后兼容**: 已经生成的旧分支不受影响

## 建议

如果需要重新生成所有V-0.5版本以应用这些修复：

```bash
# 1. 删除所有旧的filtered分支
cd /path/to/repo
git branch | grep "filtered/" | xargs git branch -D

# 2. 重新运行过滤版本生成
cd /path/to/TUBench
python generate_filtered_versions.py output/dataset.json output/filtered_dataset_new.json
```

## 测试

运行验证脚本：
```bash
python verify_fixes.py
```

预期输出：
```
================================================================================
验证过滤版本生成器的修复
================================================================================

[1/2] 测试: CSVParser.parse with null Charset
  Commit: d93c4940
  ✓ 验证通过

================================================================================
结果: 1/1 个测试通过
✓ 所有修复验证通过！
```

## 日期
2025-12-23
