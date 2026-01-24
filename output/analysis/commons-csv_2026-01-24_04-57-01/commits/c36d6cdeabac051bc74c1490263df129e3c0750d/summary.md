# Commit c36d6cde

- **Commit**: `c36d6cdeabac051bc74c1490263df129e3c0750d`
- **Parent**: `088672f6f93dc5784e5e01478639706ac7ec41f9`
- **Author**: Gary Gregory
- **Date**: 2025-03-14 20:13:42
- **Message**: CSVParser.parse(InputStream, Charset, CSVFormat) with a null CSVFormat

## Execution & Coverage

| Version | Description | Compile | Execute | Changed-Line Coverage | Changed-Branch Coverage | Tests Run | Error |
|---------|-------------|---------|---------|-----------------------|-------------------------|-----------|-------|
| V-1 | Parent commit (baseline) | PASS | PASS | 1.0000 (2/2) | - | 1/2 | - |
| V-0.5 | Parent + source-only patch | PASS | PASS | 1.0000 (1/1) | - | 1/2 | - |
| T-0.5 | Parent + test-only patch | PASS | PASS | 1.0000 (2/2) | - | 1/2 | - |
| V0 | Full commit (source + tests) | PASS | PASS | 1.0000 (1/1) | - | 1/3 | - |

- **Tests Run** 显示为 *选定用例数/实际执行用例数*；若显示 skipped，表示该版本未能识别到可执行的变更测试。

## 分类

- **主类型**: type3_adaptive_change
- **场景**: D

## Change Summary

- **Total lines**: +13 / -4
- **Source files**: +3 / -4
- **Test files**: +10 / -0

### File Changes

| File | Type | +Lines | -Lines |
|------|------|--------|--------|
| src/changes/changes.xml | other | 1 | 0 |
| src/main/java/org/apache/commons/csv/CSVParser.java | source | 2 | 4 |
| src/test/java/org/apache/commons/csv/CSVParserTest.java | test | 10 | 0 |

### Changed Methods (Source)

| Method | File | +Lines | -Lines | ΔLines | V-1 Line Cov | V-0.5 Line Cov | ΔCoverage |
|--------|------|--------|--------|--------|--------------|----------------|-----------|
| org.apache.commons.csv.CSVParser.parse | src/main/java/org/apache/commons/csv/CSVParser.java | 0 | 1 | 1 | 1.0000 | 1.0000 | +0.0000 |

### Changed Methods (Tests)

| Method | File | +Lines | -Lines | ΔLines |
|--------|------|--------|--------|--------|
| org.apache.commons.csv.CSVParserTest.testParseInputStreamCharsetNullFormat | src/test/java/org/apache/commons/csv/CSVParserTest.java | 7 | 0 | 7 |

### Selected Tests

- `org.apache.commons.csv.CSVParserTest#testParseFileCharsetNullFormat+testParseInputStreamCharsetNullFormat+testParseNullFileFormat`
- `org.apache.commons.csv.CSVParserTest#testParseFileCharsetNullFormat+testParseNullFileFormat`
