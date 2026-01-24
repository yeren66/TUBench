# Commit 088672f6

- **Commit**: `088672f6f93dc5784e5e01478639706ac7ec41f9`
- **Parent**: `931531bcd8e333372f05fc19f670dd5a9ecfd219`
- **Author**: Gary Gregory
- **Date**: 2025-03-14 20:08:06
- **Message**: CSVParser.parse(File, Charset, CSVFormat) with a null CSVFormat maps to

## Execution & Coverage

| Version | Description | Compile | Execute | Changed-Line Coverage | Changed-Branch Coverage | Tests Run | Error |
|---------|-------------|---------|---------|-----------------------|-------------------------|-----------|-------|
| V-1 | Parent commit (baseline) | PASS | PASS | 1.0000 (3/3) | - | 1/7 | - |
| V-0.5 | Parent + source-only patch | PASS | PASS | 1.0000 (2/2) | - | 1/7 | - |
| T-0.5 | Parent + test-only patch | PASS | PASS | 1.0000 (3/3) | - | 1/7 | - |
| V0 | Full commit (source + tests) | PASS | PASS | 1.0000 (2/2) | - | 1/9 | - |

- **Tests Run** 显示为 *选定用例数/实际执行用例数*；若显示 skipped，表示该版本未能识别到可执行的变更测试。

## 分类

- **主类型**: type3_adaptive_change
- **场景**: D

## Change Summary

- **Total lines**: +20 / -11
- **Source files**: +4 / -3
- **Test files**: +16 / -8

### File Changes

| File | Type | +Lines | -Lines |
|------|------|--------|--------|
| src/changes/changes.xml | other | 2 | 0 |
| src/main/java/org/apache/commons/csv/CSVParser.java | source | 2 | 3 |
| src/test/java/org/apache/commons/csv/CSVParserTest.java | test | 16 | 8 |

### Changed Methods (Source)

| Method | File | +Lines | -Lines | ΔLines | V-1 Line Cov | V-0.5 Line Cov | ΔCoverage |
|--------|------|--------|--------|--------|--------------|----------------|-----------|
| org.apache.commons.csv.CSVParser.parse | src/main/java/org/apache/commons/csv/CSVParser.java | 0 | 1 | 1 | 1.0000 | 1.0000 | +0.0000 |

### Changed Methods (Tests)

| Method | File | +Lines | -Lines | ΔLines |
|--------|------|--------|--------|--------|
| org.apache.commons.csv.CSVParserTest.testParseFileCharsetNullFormat | src/test/java/org/apache/commons/csv/CSVParserTest.java | 6 | 0 | 6 |
| org.apache.commons.csv.CSVParserTest.testParseFileNullFormat | src/test/java/org/apache/commons/csv/CSVParserTest.java | 0 | 2 | 2 |
| org.apache.commons.csv.CSVParserTest.testParsePathCharsetNullFormat | src/test/java/org/apache/commons/csv/CSVParserTest.java | 7 | 0 | 7 |
| org.apache.commons.csv.CSVParserTest.testParseUrlCharsetNullFormat | src/test/java/org/apache/commons/csv/CSVParserTest.java | 1 | 0 | 1 |
| org.apache.commons.csv.CSVParserTest.testProvidedHeader | src/test/java/org/apache/commons/csv/CSVParserTest.java | 0 | 3 | 3 |
| org.apache.commons.csv.CSVParserTest.testProvidedHeaderAuto | src/test/java/org/apache/commons/csv/CSVParserTest.java | 0 | 3 | 3 |

### Selected Tests

- `org.apache.commons.csv.CSVParserTest#testParse+testParseFileCharsetNullFormat+testParseNullFileFormat+testParseNullUrlCharsetFormat+testParsePathCharsetNullFormat+testParseUrlCharsetNullFormat+testParserUrlNullCharsetFormat+testProvidedHeader+testProvidedHeaderAuto`
- `org.apache.commons.csv.CSVParserTest#testParse+testParseNullFileFormat+testParseNullUrlCharsetFormat+testParseUrlCharsetNullFormat+testParserUrlNullCharsetFormat+testProvidedHeader+testProvidedHeaderAuto`
