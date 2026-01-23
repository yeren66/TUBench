"""
验证两个关键修复：
1. V-0.5的commit message包含原V0的完整内容
2. 生成的分支工作区干净，无编译产物
"""

import sys
sys.path.insert(0, '/Users/mac/Desktop/TestUpdate/TUBench')

from config import Config
from modules import GitAnalyzer
from modules.filtered_version_generator import FilteredVersionGenerator

def verify_single_commit(git_analyzer, generator, commit_hash, parent_hash):
    """验证单个commit的处理结果"""
    
    branch_name = f"filtered/{commit_hash[:8]}"
    
    # 删除可能存在的旧分支
    try:
        git_analyzer.repo.git.branch('-D', branch_name)
    except:
        pass
    
    # 生成过滤版本
    commit_info = {
        'commit_hash': commit_hash,
        'parent_hash': parent_hash
    }
    
    result = generator.generate_filtered_version(commit_info)
    
    if not result['success']:
        return False, f"生成失败: {result['error']}"
    
    # 验证1: Message完整性
    original_commit = git_analyzer.repo.commit(commit_hash)
    new_commit = git_analyzer.repo.commit(result['filtered_commit_hash'])
    
    original_msg = original_commit.message.strip()
    new_msg = new_commit.message
    
    if original_msg not in new_msg:
        return False, "新commit message未包含原始完整内容"
    
    if "[Filtered Version - Source Code Changes Only]" not in new_msg:
        return False, "新commit message缺少标识说明"
    
    # 验证2: 工作区干净
    git_analyzer.repo.git.checkout(result['filtered_commit_hash'])
    status = git_analyzer.repo.git.status('--short')
    
    if status:
        return False, f"工作区不干净，有 {len(status.split(chr(10)))} 个未跟踪文件"
    
    return True, "验证通过"


if __name__ == "__main__":
    print("=" * 80)
    print("验证过滤版本生成器的修复")
    print("=" * 80)
    
    # 初始化
    git_analyzer = GitAnalyzer(Config.REPO_PATH)
    generator = FilteredVersionGenerator(git_analyzer)
    
    # 测试用例
    test_cases = [
        {
            'name': 'CSVParser.parse with null Charset',
            'commit': 'd93c4940f2673a98033457705bc5bf0d989f7f62',
            'parent': 'c36d6cdeabac051bc74c1490263df129e3c0750d'
        },
        {
            'name': 'Fix NullPointerException',
            'commit': '42ded1cfdab6bbbc22305fef70e6f2fe217d98cf',
            'parent': '5d4a5ac8a03cc76893d2fb5a27e67ca39db0a53a'
        }
    ]
    
    success_count = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] 测试: {test['name']}")
        print(f"  Commit: {test['commit'][:8]}")
        
        passed, message = verify_single_commit(
            git_analyzer,
            generator,
            test['commit'],
            test['parent']
        )
        
        if passed:
            print(f"  ✓ {message}")
            success_count += 1
        else:
            print(f"  ✗ {message}")
    
    print("\n" + "=" * 80)
    print(f"结果: {success_count}/{len(test_cases)} 个测试通过")
    
    if success_count == len(test_cases):
        print("✓ 所有修复验证通过！")
        sys.exit(0)
    else:
        print("✗ 部分测试失败")
        sys.exit(1)
