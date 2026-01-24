# Commit 931531bc

- **Commit**: `931531bcd8e333372f05fc19f670dd5a9ecfd219`
- **Parent**: `41362db16e59cf41c122d63337372657f4bde7b7`
- **Author**: Gary Gregory
- **Date**: 2025-03-14 20:01:45
- **Message**: CSVParser.parse(String, CSVFormat) with a null CSVFormat maps to

## Execution & Coverage

| Version | Description | Compile | Execute | Changed-Line Coverage | Changed-Branch Coverage | Tests Run | Error |
|---------|-------------|---------|---------|-----------------------|-------------------------|-----------|-------|
| V-1 | Parent commit (baseline) | PASS | SKIP | 1.0000 (3/3) | - | 152 (skipped) | Skipped |
| V-0.5 | Parent + source-only patch | PASS | SKIP | 1.0000 (2/2) | - | 152 (skipped) | Skipped |
| T-0.5 | Parent + test-only patch | PASS | SKIP | 1.0000 (3/3) | - | 152 (skipped) | Skipped |
| V0 | Full commit (source + tests) | PASS | SKIP | 1.0000 (2/2) | - | 152 (skipped) | Skipped |

- **Tests Run** 表示本次仅执行的变更测试用例数量；若显示 skipped，表示该版本未能识别到可执行的变更测试。

## 分类

- **主类型**: type3_adaptive_change
- **场景**: D

## Change Summary

- **Total lines**: +14 / -5
- **Source files**: +3 / -3
- **Test files**: +11 / -2

### File Changes

| File | Type | +Lines | -Lines |
|------|------|--------|--------|
| src/changes/changes.xml | other | 2 | 1 |
| src/main/java/org/apache/commons/csv/CSVParser.java | source | 1 | 2 |
| src/test/java/org/apache/commons/csv/CSVParserTest.java | test | 11 | 2 |

### Changed Methods (Source)

| Method | File | +Lines | -Lines | ΔLines | V-1 Line Cov | V-0.5 Line Cov | ΔCoverage |
|--------|------|--------|--------|--------|--------------|----------------|-----------|
| org.apache.commons.csv.CSVParser.parse | src/main/java/org/apache/commons/csv/CSVParser.java | 0 | 1 | 1 | 1.0000 | 1.0000 | +0.0000 |

### Changed Methods (Tests)

| Method | File | +Lines | -Lines | ΔLines |
|--------|------|--------|--------|--------|
| org.apache.commons.csv.CSVParserTest.testParseStringNullFormat | src/test/java/org/apache/commons/csv/CSVParserTest.java | 11 | 2 | 13 |
