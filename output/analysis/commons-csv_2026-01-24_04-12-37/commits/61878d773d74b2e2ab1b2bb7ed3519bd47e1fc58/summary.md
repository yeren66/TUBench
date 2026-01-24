# Commit 61878d77

- **Commit**: `61878d773d74b2e2ab1b2bb7ed3519bd47e1fc58`
- **Parent**: `054dc9140ddfba0f4e3f4a0243b7ce1a0b934e51`
- **Author**: Gary D. Gregory
- **Date**: 2025-03-15 15:01:23
- **Message**: Add missing test cases for CSVFormat.CSVFormat(char|String)

## Execution & Coverage

| Version | Description | Compile | Execute | Changed-Line Coverage | Changed-Branch Coverage | Tests Run | Error |
|---------|-------------|---------|---------|-----------------------|-------------------------|-----------|-------|
| V-1 | Parent commit (baseline) | PASS | PASS | 0.9583 (23/24) | 0.9545 (42/44) | 1/105 | - |
| V-0.5 | Parent + source-only patch | PASS | PASS | 1.0000 (22/22) | 0.9762 (41/42) | 1/105 | - |
| T-0.5 | Parent + test-only patch | PASS | PASS | 0.9583 (23/24) | 0.9545 (42/44) | 1/105 | - |
| V0 | Full commit (source + tests) | PASS | PASS | 1.0000 (22/22) | 0.9762 (41/42) | 1/109 | - |

- **Tests Run** 显示为 *选定用例数/实际执行用例数*；若显示 skipped，表示该版本未能识别到可执行的变更测试。

## 分类

- **主类型**: type3_adaptive_change
- **场景**: D

## Change Summary

- **Total lines**: +20 / -3
- **Source files**: +0 / -3
- **Test files**: +20 / -0

### File Changes

| File | Type | +Lines | -Lines |
|------|------|--------|--------|
| src/main/java/org/apache/commons/csv/CSVFormat.java | source | 0 | 3 |
| src/test/java/org/apache/commons/csv/CSVFormatTest.java | test | 20 | 0 |

### Changed Methods (Source)

| Method | File | +Lines | -Lines | ΔLines | V-1 Line Cov | V-0.5 Line Cov | ΔCoverage |
|--------|------|--------|--------|--------|--------------|----------------|-----------|
| org.apache.commons.csv.CSVFormat.validate | src/main/java/org/apache/commons/csv/CSVFormat.java | 0 | 3 | 3 | 0.9583 | 1.0000 | +0.0417 |

### Changed Methods (Tests)

| Method | File | +Lines | -Lines | ΔLines |
|--------|------|--------|--------|--------|
| org.apache.commons.csv.CSVFormatTest.testDelimiterCharLineBreakCrThrowsException1 | src/test/java/org/apache/commons/csv/CSVFormatTest.java | 3 | 0 | 3 |
| org.apache.commons.csv.CSVFormatTest.testDelimiterCharLineBreakLfThrowsException1 | src/test/java/org/apache/commons/csv/CSVFormatTest.java | 3 | 0 | 3 |
| org.apache.commons.csv.CSVFormatTest.testDelimiterStringLineBreakCrThrowsException1 | src/test/java/org/apache/commons/csv/CSVFormatTest.java | 3 | 0 | 3 |
| org.apache.commons.csv.CSVFormatTest.testDelimiterStringLineBreakLfThrowsException1 | src/test/java/org/apache/commons/csv/CSVFormatTest.java | 3 | 0 | 3 |

### Selected Tests

- `org.apache.commons.csv.CSVFormatTest`
