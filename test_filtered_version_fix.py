"""
测试修复后的过滤版本生成功能
"""

import sys
sys.path.insert(0, '/Users/mac/Desktop/TestUpdate/TUBench')

from config import Config
from modules import GitAnalyzer, FilteredVersionGenerator
import json

# 初始化
git_analyzer = GitAnalyzer(Config.REPO_PATH)
generator = FilteredVersionGenerator(git_analyzer)

# 加载第一个测试commit
with open('output/dataset.json', 'r') as f:
    data = json.load(f)

# 获取第一个合格的commit
test_commit = data['commits'][0]

print("=" * 80)
print("测试修复后的功能")
print("=" * 80)
print(f"\n测试commit: {test_commit['commit_hash'][:8]}")
print(f"父commit: {test_commit['parent_hash'][:8]}")
print(f"原始消息: {test_commit['message'][:60]}...")

# 检查当前仓库状态
print(f"\n检查仓库状态...")
repo = git_analyzer.repo
print(f"  当前分支: {repo.active_branch.name if not repo.head.is_detached else 'DETACHED'}")
print(f"  是否有未提交变更: {repo.is_dirty()}")

# 删除可能存在的旧测试分支
branch_name = f"filtered/{test_commit['commit_hash'][:8]}"
try:
    repo.git.branch('-D', branch_name)
    print(f"  已删除旧测试分支: {branch_name}")
except:
    print(f"  测试分支不存在: {branch_name}")

print(f"\n开始生成过滤版本...")
result = generator.generate_filtered_version(test_commit)

if result['success']:
    print(f"\n✓ 成功生成过滤版本！")
    print(f"  V-0.5 commit: {result['filtered_commit_hash'][:8]}")
    print(f"  分支: {result['branch_name']}")
    
    # 验证commit message
    print(f"\n验证commit message:")
    filtered_commit = repo.commit(result['filtered_commit_hash'])
    print(f"  原始V0消息: {test_commit['message'][:100]}")
    print(f"  V-0.5消息: {filtered_commit.message[:150]}...")
    
    # 检查是否包含原始message
    if test_commit['message'].strip() in filtered_commit.message:
        print(f"  ✓ V-0.5消息包含原始完整消息")
    else:
        print(f"  ✗ V-0.5消息不包含原始完整消息")
    
    # 检查分支状态
    print(f"\n检查分支状态:")
    repo.git.checkout(result['branch_name'])
    
    # 检查是否有未跟踪的文件
    untracked = repo.untracked_files
    if untracked:
        print(f"  ✗ 发现未跟踪文件: {len(untracked)}个")
        for f in untracked[:5]:
            print(f"    - {f}")
    else:
        print(f"  ✓ 没有未跟踪文件")
    
    # 检查target/目录
    import os
    target_dir = os.path.join(repo.working_dir, 'target')
    if os.path.exists(target_dir):
        # 检查target/是否在gitignore中
        print(f"  ! target/目录存在（这可能是正常的，如果在父commit中也存在）")
        
        # 对比父commit的target/
        repo.git.checkout(test_commit['parent_hash'])
        parent_has_target = os.path.exists(target_dir)
        repo.git.checkout(result['branch_name'])
        
        if parent_has_target:
            print(f"  ✓ 父commit中也有target/目录")
        else:
            print(f"  ✗ 父commit中没有target/目录，V-0.5不应该有！")
    else:
        print(f"  ✓ 没有target/目录")
    
    # 对比V-0.5和V0的差异
    print(f"\n对比V-0.5和V0的差异:")
    diff_stat = repo.git.diff(result['filtered_commit_hash'], test_commit['commit_hash'], '--stat')
    print(diff_stat)
    
else:
    print(f"\n✗ 生成失败: {result.get('error', 'Unknown error')}")

print("\n" + "=" * 80)
