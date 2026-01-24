# Commit 7bfb0cea

- **Commit**: `7bfb0ceaf708a649becb319a06a2d7f8e5022e9b`
- **Parent**: `7b4e1059ab87e29dc93e104d9ea2b4f5e002f1eb`
- **Author**: Gary Gregory
- **Date**: 2025-03-08 16:49:24
- **Message**: CSVParser.getRecords() knows how to use CSVFormat's maxRows

## Execution & Coverage

| Version | Description | Compile | Execute | Changed-Line Coverage | Changed-Branch Coverage | Tests Run | Error |
|---------|-------------|---------|---------|-----------------------|-------------------------|-----------|-------|
| V-1 | Parent commit (baseline) | PASS | PASS | 1.0000 (5/5) | 1.0000 (4/4) | 2/274 | - |
| V-0.5 | Parent + source-only patch | PASS | PASS | 1.0000 (6/6) | 1.0000 (4/4) | 2/274 | - |
| T-0.5 | Parent + test-only patch | PASS | PASS | 1.0000 (5/5) | 1.0000 (4/4) | 2/274 | - |
| V0 | Full commit (source + tests) | PASS | PASS | 1.0000 (6/6) | 1.0000 (4/4) | 2/288 | - |

- **Tests Run** 显示为 *选定用例数/实际执行用例数*；若显示 skipped，表示该版本未能识别到可执行的变更测试。

## 分类

- **主类型**: type3_adaptive_change
- **场景**: D

## Change Summary

- **Total lines**: +54 / -9
- **Source files**: +15 / -2
- **Test files**: +39 / -7

### File Changes

| File | Type | +Lines | -Lines |
|------|------|--------|--------|
| src/changes/changes.xml | other | 2 | 0 |
| src/main/java/org/apache/commons/csv/CSVFormat.java | source | 11 | 0 |
| src/main/java/org/apache/commons/csv/CSVParser.java | source | 1 | 1 |
| src/main/java/org/apache/commons/csv/CSVPrinter.java | source | 1 | 1 |
| src/test/java/org/apache/commons/csv/CSVParserTest.java | test | 32 | 0 |
| src/test/java/org/apache/commons/csv/CSVPrinterTest.java | test | 7 | 7 |

### Changed Methods (Source)

| Method | File | +Lines | -Lines | ΔLines | V-1 Line Cov | V-0.5 Line Cov | ΔCoverage |
|--------|------|--------|--------|--------|--------------|----------------|-----------|
| org.apache.commons.csv.CSVFormat.isQuoteCharacterSet | src/main/java/org/apache/commons/csv/CSVFormat.java | 0 | 0 | 0 | 1.0000 | 1.0000 | +0.0000 |
| org.apache.commons.csv.CSVFormat.limit | src/main/java/org/apache/commons/csv/CSVFormat.java | 3 | 0 | 3 | 0.0000 | 1.0000 | +1.0000 |
| org.apache.commons.csv.CSVFormat.withTrim | src/main/java/org/apache/commons/csv/CSVFormat.java | 0 | 0 | 0 | 1.0000 | 1.0000 | +0.0000 |
| org.apache.commons.csv.CSVParser.stream | src/main/java/org/apache/commons/csv/CSVParser.java | 1 | 1 | 2 | 1.0000 | 1.0000 | +0.0000 |
| org.apache.commons.csv.CSVPrinter.printRecords | src/main/java/org/apache/commons/csv/CSVPrinter.java | 1 | 1 | 2 | 1.0000 | 1.0000 | +0.0000 |

### Changed Methods (Tests)

| Method | File | +Lines | -Lines | ΔLines |
|--------|------|--------|--------|--------|
| org.apache.commons.csv.CSVParserTest.testGetRecordsMaxRows | src/test/java/org/apache/commons/csv/CSVParserTest.java | 11 | 0 | 11 |
| org.apache.commons.csv.CSVParserTest.testStreamMaxRows | src/test/java/org/apache/commons/csv/CSVParserTest.java | 14 | 0 | 14 |
| org.apache.commons.csv.CSVPrinterTest.testJdbcPrinterWithResultSet | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testJdbcPrinterWithResultSetHeader | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |

### Selected Tests

- `org.apache.commons.csv.CSVParserTest`
- `org.apache.commons.csv.CSVPrinterTest`
