# Commit 30f0e1d6

- **Commit**: `30f0e1d6cafb2f6bec24b82493d850e5ae787173`
- **Parent**: `c62d12a8ec5f987c3107674c03c8577fbbb70033`
- **Author**: Gary Gregory
- **Date**: 2025-03-07 17:06:57
- **Message**: CSVPrinter.printRecords(ResultSet) knows how to use CSVFormat's maxRows

## Execution & Coverage

| Version | Description | Compile | Execute | Changed-Line Coverage | Changed-Branch Coverage | Tests Run | Error |
|---------|-------------|---------|---------|-----------------------|-------------------------|-----------|-------|
| V-1 | Parent commit (baseline) | PASS | PASS | 0.6667 (16/24) | 1.0000 (8/8) | 1/122 | - |
| V-0.5 | Parent + source-only patch | PASS | PASS | 0.7200 (18/25) | 0.7500 (9/12) | 1/122 | - |
| T-0.5 | Parent + test-only patch | PASS | PASS | 0.6667 (16/24) | 1.0000 (8/8) | 1/122 | - |
| V0 | Full commit (source + tests) | PASS | PASS | 0.7200 (18/25) | 1.0000 (12/12) | 1/136 | - |

- **Tests Run** 显示为 *选定用例数/实际执行用例数*；若显示 skipped，表示该版本未能识别到可执行的变更测试。

## 分类

- **主类型**: type3_adaptive_change
- **场景**: D

## Change Summary

- **Total lines**: +148 / -95
- **Source files**: +73 / -33
- **Test files**: +75 / -62

### File Changes

| File | Type | +Lines | -Lines |
|------|------|--------|--------|
| src/changes/changes.xml | other | 3 | 0 |
| src/main/java/org/apache/commons/csv/CSVFormat.java | source | 56 | 26 |
| src/main/java/org/apache/commons/csv/CSVPrinter.java | source | 14 | 7 |
| src/test/java/org/apache/commons/csv/CSVPrinterTest.java | test | 75 | 62 |

### Changed Methods (Source)

| Method | File | +Lines | -Lines | ΔLines | V-1 Line Cov | V-0.5 Line Cov | ΔCoverage |
|--------|------|--------|--------|--------|--------------|----------------|-----------|
| org.apache.commons.csv.Builder.setLenientEof | src/main/java/org/apache/commons/csv/CSVFormat.java | 0 | 0 | 0 | 0.0000 | 0.0000 | +0.0000 |
| org.apache.commons.csv.Builder.setMaxRows | src/main/java/org/apache/commons/csv/CSVFormat.java | 4 | 0 | 4 | 0.0000 | 0.0000 | +0.0000 |
| org.apache.commons.csv.Builder.setTrailingDelimiter | src/main/java/org/apache/commons/csv/CSVFormat.java | 0 | 0 | 0 | 0.0000 | 0.0000 | +0.0000 |
| org.apache.commons.csv.CSVFormat.append | src/main/java/org/apache/commons/csv/CSVFormat.java | 0 | 0 | 0 | 1.0000 | 1.0000 | +0.0000 |
| org.apache.commons.csv.CSVFormat.getLenientEof | src/main/java/org/apache/commons/csv/CSVFormat.java | 0 | 0 | 0 | 1.0000 | 1.0000 | +0.0000 |
| org.apache.commons.csv.CSVFormat.getMaxRows | src/main/java/org/apache/commons/csv/CSVFormat.java | 3 | 0 | 3 | 0.0000 | 1.0000 | +1.0000 |
| org.apache.commons.csv.CSVFormat.hashCode | src/main/java/org/apache/commons/csv/CSVFormat.java | 1 | 2 | 3 | 0.0000 | 0.0000 | +0.0000 |
| org.apache.commons.csv.CSVPrinter.printRecords | src/main/java/org/apache/commons/csv/CSVPrinter.java | 2 | 1 | 3 | 1.0000 | 1.0000 | +0.0000 |

### Changed Methods (Tests)

| Method | File | +Lines | -Lines | ΔLines |
|--------|------|--------|--------|--------|
| org.apache.commons.csv.CSVPrinterTest.testCRComment | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 2 | 2 | 4 |
| org.apache.commons.csv.CSVPrinterTest.testDontQuoteEuroFirstChar | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testExcelPrintAllArrayOfArrays | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testExcelPrintAllArrayOfArraysWithFirstEmptyValue2 | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testExcelPrintAllArrayOfArraysWithFirstSpaceValue1 | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testExcelPrintAllArrayOfArraysWithFirstTabValue1 | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testExcelPrintAllArrayOfLists | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testExcelPrintAllArrayOfListsWithFirstEmptyValue2 | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testExcelPrintAllIterableOfArrays | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testExcelPrintAllIterableOfArraysWithFirstEmptyValue2 | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testExcelPrintAllIterableOfLists | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testExcelPrintAllStreamOfArrays | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testExcelPrinter1 | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testExcelPrinter2 | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testJdbcPrinter | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 2 | 2 | 4 |
| org.apache.commons.csv.CSVPrinterTest.testJdbcPrinterWithFirstEmptyValue2 | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testJdbcPrinterWithResultSet | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 14 | 0 | 14 |
| org.apache.commons.csv.CSVPrinterTest.testJdbcPrinterWithResultSet | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 0 | 5 | 5 |
| org.apache.commons.csv.CSVPrinterTest.testJdbcPrinterWithResultSetHeader | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 4 | 0 | 4 |
| org.apache.commons.csv.CSVPrinterTest.testJdbcPrinterWithResultSetMetaData | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 3 | 0 | 3 |
| org.apache.commons.csv.CSVPrinterTest.testJdbcPrinterWithResultSetHeader | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 0 | 4 | 4 |
| org.apache.commons.csv.CSVPrinterTest.testJdbcPrinterWithResultSetMetaData | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 0 | 3 | 3 |
| org.apache.commons.csv.CSVPrinterTest.testMongoDbCsvBasic | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testMongoDbCsvCommaInValue | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testMongoDbCsvDoubleQuoteInValue | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testMongoDbCsvTabInValue | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testMongoDbTsvBasic | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testMongoDbTsvCommaInValue | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testMongoDbTsvTabInValue | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testMultiLineComment | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testNotFlushable | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testParseCustomNullValues | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testPrint | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testPrintCustomNullValues | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testPrinter1 | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testPrinter2 | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testPrinter3 | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testPrinter4 | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testPrinter5 | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testPrinter6 | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testPrinter7 | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testPrintNullValues | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testPrintToFileWithCharsetUtf16Be | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testPrintToFileWithDefaultCharset | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testPrintToPathWithDefaultCharset | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testQuoteAll | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testQuoteCommaFirstChar | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testQuoteNonNumeric | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testSingleLineComment | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |

### Selected Tests

- `org.apache.commons.csv.CSVPrinterTest`
