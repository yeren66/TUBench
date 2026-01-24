# Commit 41362db1

- **Commit**: `41362db16e59cf41c122d63337372657f4bde7b7`
- **Parent**: `1ac1eec07747101c0dd9b6a7a75ba114de5925c6`
- **Author**: Gary Gregory
- **Date**: 2025-03-14 19:55:57
- **Message**: CSVParser.parse(URL, Charset, CSVFormat) with a null CSVFormat maps to

## Execution & Coverage

| Version | Description | Compile | Execute | Changed-Line Coverage | Changed-Branch Coverage | Tests Run | Error |
|---------|-------------|---------|---------|-----------------------|-------------------------|-----------|-------|
| V-1 | Parent commit (baseline) | PASS | PASS | 1.0000 (3/3) | - | 1/152 | - |
| V-0.5 | Parent + source-only patch | PASS | PASS | 1.0000 (2/2) | - | 1/152 | - |
| T-0.5 | Parent + test-only patch | PASS | PASS | 1.0000 (3/3) | - | 1/152 | - |
| V0 | Full commit (source + tests) | PASS | PASS | 1.0000 (2/2) | - | 1/152 | - |

- **Tests Run** 显示为 *选定用例数/实际执行用例数*；若显示 skipped，表示该版本未能识别到可执行的变更测试。

## 分类

- **主类型**: type3_adaptive_change
- **场景**: D

## Change Summary

- **Total lines**: +9 / -5
- **Source files**: +3 / -3
- **Test files**: +6 / -2

### File Changes

| File | Type | +Lines | -Lines |
|------|------|--------|--------|
| src/changes/changes.xml | other | 1 | 0 |
| src/main/java/org/apache/commons/csv/CSVParser.java | source | 2 | 3 |
| src/test/java/org/apache/commons/csv/CSVParserTest.java | test | 6 | 2 |

### Changed Methods (Source)

| Method | File | +Lines | -Lines | ΔLines | V-1 Line Cov | V-0.5 Line Cov | ΔCoverage |
|--------|------|--------|--------|--------|--------------|----------------|-----------|
| org.apache.commons.csv.CSVParser.parse | src/main/java/org/apache/commons/csv/CSVParser.java | 0 | 1 | 1 | 1.0000 | 1.0000 | +0.0000 |

### Changed Methods (Tests)

| Method | File | +Lines | -Lines | ΔLines |
|--------|------|--------|--------|--------|
| org.apache.commons.csv.CSVParserTest.testParseUrlCharsetNullFormat | src/test/java/org/apache/commons/csv/CSVParserTest.java | 6 | 2 | 8 |

### Selected Tests

- `org.apache.commons.csv.CSVParserTest`
