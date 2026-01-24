# Commit c75601d2

- **Commit**: `c75601d2a3426adf1671572766cc65906812fa73`
- **Parent**: `76981db68af50e0475a2d5d0fcc6bdf87efb18f1`
- **Author**: Gary Gregory
- **Date**: 2025-01-02 20:14:43
- **Message**: Use final

## Execution & Coverage

| Version | Description | Compile | Execute | Changed-Line Coverage | Changed-Branch Coverage | Tests Run | Error |
|---------|-------------|---------|---------|-----------------------|-------------------------|-----------|-------|
| V-1 | Parent commit (baseline) | PASS | PASS | 0.4545 (5/11) | 0.1667 (1/6) | 1/2 | - |
| V-0.5 | Parent + source-only patch | PASS | PASS | 0.4545 (5/11) | 0.1667 (1/6) | 1/2 | - |
| T-0.5 | Parent + test-only patch | PASS | PASS | 0.4545 (5/11) | 0.1667 (1/6) | 1/2 | - |
| V0 | Full commit (source + tests) | PASS | PASS | 0.4545 (5/11) | 0.1667 (1/6) | 1/2 | - |

- **Tests Run** 显示为 *选定用例数/实际执行用例数*；若显示 skipped，表示该版本未能识别到可执行的变更测试。

## 分类

- **主类型**: type3_adaptive_change
- **场景**: D

## Change Summary

- **Total lines**: +11 / -12
- **Source files**: +10 / -11
- **Test files**: +1 / -1

### File Changes

| File | Type | +Lines | -Lines |
|------|------|--------|--------|
| src/main/java/org/apache/commons/csv/ExtendedBufferedReader.java | source | 10 | 11 |
| src/test/java/org/apache/commons/csv/JiraCsv196Test.java | test | 1 | 1 |

### Changed Methods (Source)

| Method | File | +Lines | -Lines | ΔLines | V-1 Line Cov | V-0.5 Line Cov | ΔCoverage |
|--------|------|--------|--------|--------|--------------|----------------|-----------|
| org.apache.commons.csv.ExtendedBufferedReader.getEncodedCharLength | src/main/java/org/apache/commons/csv/ExtendedBufferedReader.java | 9 | 10 | 19 | 0.4545 | 0.4545 | +0.0000 |

### Changed Methods (Tests)

| Method | File | +Lines | -Lines | ΔLines |
|--------|------|--------|--------|--------|
| org.apache.commons.csv.JiraCsv196Test.getTestInput | src/test/java/org/apache/commons/csv/JiraCsv196Test.java | 1 | 1 | 2 |

### Selected Tests

- `org.apache.commons.csv.JiraCsv196Test`
