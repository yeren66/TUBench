"""
测试diff过滤功能
"""

import sys
sys.path.insert(0, '/Users/mac/Desktop/TestUpdate/TUBench')

from config import Config
from modules import GitAnalyzer, DiffFilter

# 使用配置文件中的仓库路径
# 初始化
git_analyzer = GitAnalyzer(Config.REPO_PATH)
diff_filter = DiffFilter()

# 测试第一个合格的commit
commit_hash = "d93c4940f2673a98033457705bc5bf0d989f7f62"
parent_hash = "c36d6cdeabac051bc74c1490263df129e3c0750d"

print(f"测试commit: {commit_hash[:8]}")
print(f"父commit: {parent_hash[:8]}")
print("=" * 80)

# 获取diff
try:
    diff_text = git_analyzer.repo.git.diff(parent_hash, commit_hash)
    print(f"\n✓ 成功获取diff，长度: {len(diff_text)} 字符")
    print(f"\n前500字符预览:")
    print(diff_text[:500])
    print("\n" + "=" * 80)
    
    # 过滤diff
    filtered_diff, test_diff, stats = diff_filter.filter_test_changes(diff_text)
    
    print(f"\n过滤结果:")
    print(f"  源代码文件: {stats['source_files']}")
    print(f"  测试文件: {stats['test_files']}")
    print(f"  过滤后的diff长度: {len(filtered_diff)}")
    print(f"  测试diff长度: {len(test_diff)}")
    
    if filtered_diff:
        print(f"\n✓ 过滤成功！")
        print(f"\n源代码diff前500字符:")
        print(filtered_diff[:500])
    else:
        print(f"\n✗ 警告：过滤后没有源代码变更")
    
    if test_diff:
        print(f"\n测试diff前500字符:")
        print(test_diff[:500])
        
except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
