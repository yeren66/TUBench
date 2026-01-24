"""
报告生成器 - 生成各种格式的分析报告
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any

from utils.logger import get_logger

logger = get_logger()


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, output_dir: str):
        """
        初始化
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_project_summary_json(self, result: 'ProjectAnalysisResult', output_path: str):
        """生成项目JSON摘要"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"JSON报告已生成: {output_path}")
        except Exception as e:
            logger.error(f"生成JSON报告失败: {e}")
    
    def generate_project_summary_markdown(self, result: 'ProjectAnalysisResult', output_path: str):
        """生成项目Markdown报告"""
        try:
            md_content = self._build_project_markdown(result)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            logger.info(f"Markdown报告已生成: {output_path}")
        except Exception as e:
            logger.error(f"生成Markdown报告失败: {e}")
    
    def _build_project_markdown(self, result: 'ProjectAnalysisResult') -> str:
        """构建项目Markdown内容"""
        lines = []
        
        project_info = result.project_info
        filter_funnel = result.filter_funnel
        type_stats = result.type_statistics
        exec_stats = result.execution_statistics
        metadata = result.analysis_metadata
        
        # 标题
        lines.append(f"# {project_info.get('name', 'Unknown')} 分析报告\n")
        
        # 项目信息
        lines.append("## 项目信息\n")
        lines.append(f"- **项目名**: {project_info.get('name')}")
        lines.append(f"- **路径**: {project_info.get('path')}")
        lines.append(f"- **默认分支**: {project_info.get('default_branch')}")
        lines.append(f"- **分析日期**: {metadata.get('analysis_start_time', '')[:10]}")
        
        duration = metadata.get('total_duration_seconds', 0)
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        if hours > 0:
            lines.append(f"- **分析耗时**: {hours}小时{minutes}分钟{seconds}秒")
        elif minutes > 0:
            lines.append(f"- **分析耗时**: {minutes}分钟{seconds}秒")
        else:
            lines.append(f"- **分析耗时**: {seconds}秒")
        lines.append("")
        
        # 过滤漏斗
        lines.append("## 过滤漏斗\n")
        lines.append("| 阶段 | 数量 | 阶段通过率 | 累计通过率 |")
        lines.append("|------|------|------------|------------|")
        
        # 获取各阶段数量
        total = filter_funnel.get('stage0_total', 0)
        after_date = filter_funnel.get('stage1_after_date_filter', 0)
        has_test_src = filter_funnel.get('stage2_has_test_and_source', 0)
        has_method = filter_funnel.get('stage3_has_method_changes', 0)
        v1_build = filter_funnel.get('stage4_v1_build_success', 0)
        v0_build = filter_funnel.get('stage5_v0_build_success', 0)
        qualified = filter_funnel.get('stage6_qualified', 0)
        
        def pct(num, denom):
            return f"{num/denom*100:.1f}%" if denom > 0 else "-"
        
        # 如果 total 为 0，则使用 after_date 作为基准
        base_total = total if total > 0 else after_date
        
        lines.append(f"| 日期范围内Commits | {after_date} | - | - |")
        lines.append(f"| 同时修改测试和源代码 | {has_test_src} | {pct(has_test_src, after_date)} | {pct(has_test_src, base_total)} |")
        lines.append(f"| 有方法级变更 | {has_method} | {pct(has_method, has_test_src)} | {pct(has_method, base_total)} |")
        lines.append(f"| V-1构建成功 | {v1_build} | {pct(v1_build, has_method)} | {pct(v1_build, base_total)} |")
        lines.append(f"| V0构建成功 | {v0_build} | {pct(v0_build, v1_build)} | {pct(v0_build, base_total)} |")
        lines.append(f"| **最终合格** | {qualified} | {pct(qualified, v0_build)} | {pct(qualified, base_total)} |")
        lines.append("")
        
        # 类型分布
        lines.append("## 类型分布\n")
        lines.append("| 类型 | 数量 | 占比 | 说明 |")
        lines.append("|------|------|------|------|")
        
        type1 = type_stats.get('type1_execution_error', {})
        type2 = type_stats.get('type2_coverage_decrease', {})
        type3 = type_stats.get('type3_adaptive_change', {})
        
        lines.append(f"| Type1 (执行出错) | {type1.get('count', 0)} | {type1.get('percentage', '0%')} | V-0.5编译或测试失败 |")
        
        subtypes = type1.get('subtypes', {})
        lines.append(f"| ├─ 编译失败 | {subtypes.get('compile_failure', 0)} | - | |")
        lines.append(f"| └─ 运行时失败 | {subtypes.get('runtime_failure', 0)} | - | |")
        
        lines.append(f"| Type2 (覆盖率降低) | {type2.get('count', 0)} | {type2.get('percentage', '0%')} | V-0.5覆盖率下降 |")
        lines.append(f"| Type3 (适应性调整) | {type3.get('count', 0)} | {type3.get('percentage', '0%')} | 其他情况 |")
        lines.append("")
        
        # 场景分布
        lines.append("## 场景分布\n")
        lines.append("场景基于 V-0.5 和 T-0.5 的测试执行结果划分（V-1 和 V0 均已通过构建和测试）：\n")
        lines.append("| 场景 | V-0.5 | T-0.5 | 数量 | 说明 |")
        lines.append("|------|-------|-------|------|------|")
        
        scenarios = type_stats.get('scenario_distribution', {})
        lines.append(f"| A | 失败 | 失败 | {scenarios.get('A', 0)} | 新旧测试都不兼容旧代码 |")
        lines.append(f"| B | 失败 | 通过 | {scenarios.get('B', 0)} | 旧测试失败，新测试可在旧代码运行 |")
        lines.append(f"| C | 通过 | 失败 | {scenarios.get('C', 0)} | 旧测试通过，新测试针对新功能 |")
        lines.append(f"| D | 通过 | 通过 | {scenarios.get('D', 0)} | 新旧测试都能通过 |")
        lines.append("")
        
        # V-0.5和T-0.5执行统计
        lines.append("## 执行统计\n")
        lines.append("### V-0.5 (仅源代码变更)\n")
        v05 = exec_stats.get('v05_results', {})
        lines.append(f"- 编译成功: {v05.get('compile_success', 0)}")
        lines.append(f"- 编译失败: {v05.get('compile_failed', 0)}")
        lines.append(f"- 测试成功: {v05.get('test_success', 0)}")
        lines.append(f"- 测试失败: {v05.get('test_failed', 0)}")
        lines.append("")
        
        lines.append("### T-0.5 (仅测试变更)\n")
        t05 = exec_stats.get('t05_results', {})
        lines.append(f"- 编译成功: {t05.get('compile_success', 0)}")
        lines.append(f"- 编译失败: {t05.get('compile_failed', 0)}")
        lines.append(f"- 测试成功: {t05.get('test_success', 0)}")
        lines.append(f"- 测试失败: {t05.get('test_failed', 0)}")
        lines.append("")
        
        # 示例commits
        lines.append("## 示例Commits\n")
        
        if type1.get('examples'):
            lines.append("### Type1 示例 (执行出错)\n")
            for i, commit in enumerate(type1['examples'][:3], 1):
                short = commit[:8]
                lines.append(f"{i}. [{short}](commits/{short}/summary.md)")
            lines.append("")
        
        if type2.get('examples'):
            lines.append("### Type2 示例 (覆盖率降低)\n")
            for i, commit in enumerate(type2['examples'][:3], 1):
                short = commit[:8]
                lines.append(f"{i}. [{short}](commits/{short}/summary.md)")
            lines.append("")
        
        if type3.get('examples'):
            lines.append("### Type3 示例 (适应性调整)\n")
            for i, commit in enumerate(type3['examples'][:3], 1):
                short = commit[:8]
                lines.append(f"{i}. [{short}](commits/{short}/summary.md)")
            lines.append("")
        
        # 合格Commits列表
        qualified = result.qualified_commits
        lines.append(f"## 合格Commits列表 ({len(qualified)}个)\n")
        
        if len(qualified) <= 20:
            for commit in qualified:
                short = commit[:8]
                lines.append(f"- [{short}](commits/{short}/summary.md)")
        else:
            lines.append("<details>")
            lines.append(f"<summary>点击展开完整列表 ({len(qualified)}个)</summary>\n")
            for commit in qualified:
                short = commit[:8]
                lines.append(f"- [{short}](commits/{short}/summary.md)")
            lines.append("\n</details>")
        lines.append("")
        
        # 页脚
        lines.append("---")
        lines.append(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        lines.append("*Generated by TUBench Analysis Tool*")
        
        return '\n'.join(lines)
    
    def generate_commit_detail_json(self, result: 'CommitAnalysisResult', output_path: str):
        """生成commit详细JSON"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"生成commit JSON失败: {e}")

    def generate_commit_summary_markdown(self, commit_result: dict, output_path: str):
        """生成commit摘要Markdown，便于快速查看执行与覆盖率"""
        try:
            basic = commit_result.get('basic_info', {})
            v1 = commit_result.get('v1_execution', {})
            v05 = commit_result.get('v05_execution', {})
            t05 = commit_result.get('t05_execution', {})
            v0 = commit_result.get('v0_execution', {})
            file_changes = commit_result.get('file_changes', {})
            method_changes = commit_result.get('method_changes', {})
            diff_info = commit_result.get('diff_info', {})
            method_change_stats = commit_result.get('method_change_stats', {}) or \
                method_changes.get('method_change_stats', {})

            def _fmt_status(val, skipped=False):
                if skipped:
                    return "SKIP"
                return "PASS" if val else "FAIL"

            def _cov_method(cov):
                line_cov = cov.get('method_line_coverage') if cov else None
                if not line_cov or line_cov.get('total_lines', 0) == 0:
                    return "-"
                return f"{line_cov.get('coverage_ratio', 0):.4f} ({line_cov.get('covered_lines', 0)}/{line_cov.get('total_lines', 0)})"

            def _cov_branch(cov):
                branch_cov = cov.get('method_branch_coverage') if cov else None
                if not branch_cov or branch_cov.get('total_branches', 0) == 0:
                    return "-"
                return f"{branch_cov.get('coverage_ratio', 0):.4f} ({branch_cov.get('covered_branches', 0)}/{branch_cov.get('total_branches', 0)})"

            def _err_msg(data):
                build_err = data.get('build', {}).get('error_message')
                test_err = data.get('test', {}).get('error_message')
                if data.get('test', {}).get('selection_skipped'):
                    return data.get('test', {}).get('error_message') or 'Skipped'
                if build_err:
                    return build_err.strip().split('\n')[0][:200]
                if test_err:
                    return test_err.strip().split('\n')[0][:200]
                return "-"

            lines = []
            lines.append(f"# Commit {basic.get('short_hash', '')}\n")
            lines.append(f"- **Commit**: `{basic.get('commit_hash', '')}`")
            lines.append(f"- **Parent**: `{basic.get('parent_hash', '')}`")
            lines.append(f"- **Author**: {basic.get('author', '')}")
            lines.append(f"- **Date**: {basic.get('date', '')}")
            lines.append(f"- **Message**: {basic.get('message_subject', '')}")
            lines.append("")

            lines.append("## Execution & Coverage\n")
            lines.append("| Version | Description | Compile | Execute | Changed-Line Coverage | Changed-Branch Coverage | Tests Run | Error |")
            lines.append("|---------|-------------|---------|---------|-----------------------|-------------------------|-----------|-------|")

            def _count_selected_test_methods(selectors: list) -> int:
                """从Surefire选择器列表中统计实际选定的测试方法数量
                
                选择器格式:
                - "ClassName#method1+method2+method3" -> 3个方法
                - "ClassName" (整个类) -> 算作1个选择器
                """
                count = 0
                for selector in selectors:
                    if '#' in selector:
                        # 格式: ClassName#method1+method2+...
                        methods_part = selector.split('#', 1)[1]
                        count += len(methods_part.split('+'))
                    else:
                        # 整个类，算作1
                        count += 1
                return count

            def _row(label, data, desc):
                build_ok = data.get('build', {}).get('success', False)
                test_ok = data.get('test', {}).get('success', False)
                test_skipped = data.get('test', {}).get('selection_skipped', False)
                cov = data.get('coverage', {})
                total_tests = data.get('test', {}).get('total_tests', 0)
                selected_tests = data.get('test', {}).get('selected_tests', []) or []
                selected_count = _count_selected_test_methods(selected_tests)
                tests_display = f"{selected_count}/{total_tests}"
                if test_skipped:
                    tests_display = f"{selected_count}/{total_tests} (skipped)"
                return (
                    f"| {label} | {desc} | {_fmt_status(build_ok)} | {_fmt_status(test_ok, test_skipped)} | "
                    f"{_cov_method(cov)} | {_cov_branch(cov)} | {tests_display} | {_err_msg(data)} |"
                )

            lines.append(_row("V-1", v1, "Parent commit (baseline)"))
            lines.append(_row("V-0.5", v05, "Parent + source-only patch"))
            lines.append(_row("T-0.5", t05, "Parent + test-only patch"))
            lines.append(_row("V0", v0, "Full commit (source + tests)"))
            lines.append("")
            lines.append("- **Tests Run** 显示为 *选定用例数/实际执行用例数*；若显示 skipped，表示该版本未能识别到可执行的变更测试。\n")

            classification = commit_result.get('classification', {})
            if classification:
                lines.append("## 分类\n")
                lines.append(f"- **主类型**: {classification.get('primary_type', '-')}")
                lines.append(f"- **场景**: {classification.get('scenario', '-')}")
                lines.append("")

            change_stats = diff_info.get('change_stats', {})
            full_stats = change_stats.get('full', {})
            source_stats = change_stats.get('source', {})
            test_stats = change_stats.get('test', {})

            lines.append("## Change Summary\n")
            lines.append(f"- **Total lines**: +{full_stats.get('total_lines_added', 0)} / -{full_stats.get('total_lines_removed', 0)}")
            lines.append(f"- **Source files**: +{source_stats.get('total_lines_added', 0)} / -{source_stats.get('total_lines_removed', 0)}")
            lines.append(f"- **Test files**: +{test_stats.get('total_lines_added', 0)} / -{test_stats.get('total_lines_removed', 0)}")
            lines.append("")

            lines.append("### File Changes\n")
            lines.append("| File | Type | +Lines | -Lines |")
            lines.append("|------|------|--------|--------|")

            source_paths = {f.get('path') for f in file_changes.get('source_files', [])}
            test_paths = {f.get('path') for f in file_changes.get('test_files', [])}
            for f in full_stats.get('files', []):
                path = f.get('path')
                if path in source_paths:
                    ftype = "source"
                elif path in test_paths:
                    ftype = "test"
                else:
                    ftype = "other"
                lines.append(f"| {path} | {ftype} | {f.get('lines_added', 0)} | {f.get('lines_removed', 0)} |")
            lines.append("")

            v1_line_details = {}
            v05_line_details = {}
            v1_cov = v1.get('coverage', {}).get('method_line_coverage', {})
            v05_cov = v05.get('coverage', {}).get('method_line_coverage', {})
            for d in v1_cov.get('details', []) or []:
                v1_line_details[d.get('method')] = d.get('coverage_ratio', 0)
            for d in v05_cov.get('details', []) or []:
                v05_line_details[d.get('method')] = d.get('coverage_ratio', 0)

            lines.append("### Changed Methods (Source)\n")
            lines.append("| Method | File | +Lines | -Lines | ΔLines | V-1 Line Cov | V-0.5 Line Cov | ΔCoverage |")
            lines.append("|--------|------|--------|--------|--------|--------------|----------------|-----------|")

            changed_source = method_changes.get('source_methods', [])
            stats_source = method_change_stats.get('source', []) if method_change_stats else []
            stats_map = {}
            for s in stats_source:
                key = f"{s.get('package')}.{s.get('class')}.{s.get('method')}".strip('.')
                stats_map[key] = s

            for m in changed_source:
                key = f"{m.get('package')}.{m.get('class')}.{m.get('method')}".strip('.')
                s = stats_map.get(key, {})
                added = s.get('added_lines', 0)
                removed = s.get('removed_lines', 0)
                total = s.get('total_changed_lines', added + removed)
                full_name = key
                v1_ratio = v1_line_details.get(full_name, 0)
                v05_ratio = v05_line_details.get(full_name, 0)
                delta = v05_ratio - v1_ratio
                lines.append(
                    f"| {full_name} | {m.get('file','')} | {added} | {removed} | {total} | "
                    f"{v1_ratio:.4f} | {v05_ratio:.4f} | {delta:+.4f} |"
                )
            lines.append("")

            if method_change_stats and method_change_stats.get('test'):
                lines.append("### Changed Methods (Tests)\n")
                lines.append("| Method | File | +Lines | -Lines | ΔLines |")
                lines.append("|--------|------|--------|--------|--------|")
                for s in method_change_stats.get('test', []):
                    key = f"{s.get('package')}.{s.get('class')}.{s.get('method')}".strip('.')
                    lines.append(
                        f"| {key} | {s.get('file','')} | {s.get('added_lines',0)} | {s.get('removed_lines',0)} | {s.get('total_changed_lines',0)} |"
                    )
                lines.append("")

            selected_tests = []
            for data in (v1, v05, t05, v0):
                selected_tests.extend(data.get('test', {}).get('selected_tests', []) or [])
            selected_tests = sorted(set(selected_tests))
            if selected_tests:
                lines.append("### Selected Tests\n")
                for test in selected_tests:
                    lines.append(f"- `{test}`")
                lines.append("")

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

        except Exception as e:
            logger.error(f"生成commit Markdown失败: {e}")
    
    def generate_global_summary(self, project_results: List['ProjectAnalysisResult'], 
                               output_dir: str):
        """生成全局汇总报告"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 汇总统计
        summary = {
            'total_projects': len(project_results),
            'analysis_date': datetime.now().isoformat(),
            'projects': []
        }
        
        total_qualified = 0
        total_type1 = 0
        total_type2 = 0
        total_type3 = 0
        
        for result in project_results:
            project_info = result.project_info
            type_stats = result.type_statistics
            
            qualified_count = len(result.qualified_commits)
            type1_count = type_stats.get('type1_execution_error', {}).get('count', 0)
            type2_count = type_stats.get('type2_coverage_decrease', {}).get('count', 0)
            type3_count = type_stats.get('type3_adaptive_change', {}).get('count', 0)
            
            summary['projects'].append({
                'name': project_info.get('name'),
                'qualified_commits': qualified_count,
                'type1_count': type1_count,
                'type2_count': type2_count,
                'type3_count': type3_count
            })
            
            total_qualified += qualified_count
            total_type1 += type1_count
            total_type2 += type2_count
            total_type3 += type3_count
        
        summary['totals'] = {
            'qualified_commits': total_qualified,
            'type1_count': total_type1,
            'type2_count': total_type2,
            'type3_count': total_type3
        }
        
        # 保存JSON
        json_path = os.path.join(output_dir, 'all_projects_stats.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # 生成Markdown报告
        md_content = self._build_global_markdown(summary, project_results)
        md_path = os.path.join(output_dir, 'analysis_report.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"全局汇总报告已生成: {output_dir}")
    
    def _build_global_markdown(self, summary: dict, results: List['ProjectAnalysisResult']) -> str:
        """构建全局Markdown内容"""
        lines = []
        
        lines.append("# TUBench 全局分析报告\n")
        lines.append(f"**分析日期**: {summary['analysis_date'][:10]}")
        lines.append(f"**项目数量**: {summary['total_projects']}")
        lines.append("")
        
        # 总体统计
        lines.append("## 总体统计\n")
        totals = summary.get('totals', {})
        lines.append(f"- **合格Commits总数**: {totals.get('qualified_commits', 0)}")
        lines.append(f"- **Type1 (执行出错)**: {totals.get('type1_count', 0)}")
        lines.append(f"- **Type2 (覆盖率降低)**: {totals.get('type2_count', 0)}")
        lines.append(f"- **Type3 (适应性调整)**: {totals.get('type3_count', 0)}")
        lines.append("")
        
        # 项目明细表
        lines.append("## 项目明细\n")
        lines.append("| 项目 | 合格Commits | Type1 | Type2 | Type3 |")
        lines.append("|------|-------------|-------|-------|-------|")
        
        for proj in summary.get('projects', []):
            lines.append(
                f"| {proj['name']} | {proj['qualified_commits']} | "
                f"{proj['type1_count']} | {proj['type2_count']} | {proj['type3_count']} |"
            )
        
        # 汇总行
        lines.append(
            f"| **总计** | **{totals.get('qualified_commits', 0)}** | "
            f"**{totals.get('type1_count', 0)}** | **{totals.get('type2_count', 0)}** | "
            f"**{totals.get('type3_count', 0)}** |"
        )
        lines.append("")
        
        # 页脚
        lines.append("---")
        lines.append(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        lines.append("*Generated by TUBench Analysis Tool*")
        
        return '\n'.join(lines)
