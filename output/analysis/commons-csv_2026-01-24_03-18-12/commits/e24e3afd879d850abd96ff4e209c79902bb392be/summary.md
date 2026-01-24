# Commit e24e3afd

- **Commit**: `e24e3afd879d850abd96ff4e209c79902bb392be`
- **Parent**: `b25b2509c839f490546586d70f360448bb17e449`
- **Author**: Gary Gregory
- **Date**: 2025-03-08 00:56:41
- **Message**: CSVPrinter.printRecords(Stream) knows how to use CSVFormat's maxRows

## Execution & Coverage

| Version | Description | Compile | Execute | Changed-Line Coverage | Changed-Branch Coverage | Tests Run | Error |
|---------|-------------|---------|---------|-----------------------|-------------------------|-----------|-------|
| V-1 | Parent commit (baseline) | PASS | SKIP | 1.0000 (11/11) | 1.0000 (6/6) | 140 (skipped) | Skipped |
| V-0.5 | Parent + source-only patch | PASS | SKIP | 1.0000 (8/8) | 1.0000 (6/6) | 140 (skipped) | Skipped |
| T-0.5 | Parent + test-only patch | PASS | SKIP | 1.0000 (11/11) | 1.0000 (6/6) | 140 (skipped) | Skipped |
| V0 | Full commit (source + tests) | PASS | SKIP | 1.0000 (8/8) | 1.0000 (6/6) | 144 (skipped) | Skipped |

- **Tests Run** 表示本次仅执行的变更测试用例数量；若显示 skipped，表示该版本未能识别到可执行的变更测试。

## 分类

- **主类型**: type3_adaptive_change
- **场景**: D

## Change Summary

- **Total lines**: +28 / -20
- **Source files**: +8 / -6
- **Test files**: +20 / -14

### File Changes

| File | Type | +Lines | -Lines |
|------|------|--------|--------|
| src/changes/changes.xml | other | 1 | 0 |
| src/main/java/org/apache/commons/csv/CSVPrinter.java | source | 7 | 6 |
| src/test/java/org/apache/commons/csv/CSVPrinterTest.java | test | 18 | 12 |
| src/test/java/org/apache/commons/csv/Utils.java | test | 2 | 2 |

### Changed Methods (Source)

| Method | File | +Lines | -Lines | ΔLines | V-1 Line Cov | V-0.5 Line Cov | ΔCoverage |
|--------|------|--------|--------|--------|--------------|----------------|-----------|
| org.apache.commons.csv.CSVPrinter.printRecordObject | src/main/java/org/apache/commons/csv/CSVPrinter.java | 0 | 0 | 0 | 1.0000 | 1.0000 | +0.0000 |
| org.apache.commons.csv.CSVPrinter.printRecords | src/main/java/org/apache/commons/csv/CSVPrinter.java | 1 | 1 | 2 | 1.0000 | 1.0000 | +0.0000 |

### Changed Methods (Tests)

| Method | File | +Lines | -Lines | ΔLines |
|--------|------|--------|--------|--------|
| org.apache.commons.csv.CSVPrinterTest.testExcelPrintAllStreamOfArrays | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 8 | 0 | 8 |
| org.apache.commons.csv.CSVPrinterTest.testExcelPrintAllStreamOfArrays | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 0 | 3 | 3 |
| org.apache.commons.csv.CSVPrinterTest.testJdbcPrinterWithResultSet | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 0 | 1 |
| org.apache.commons.csv.CSVPrinterTest.testJdbcPrinterWithResultSet | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 0 | 1 | 1 |
| org.apache.commons.csv.CSVPrinterTest.testJdbcPrinterWithResultSetHeader | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 0 | 1 |
| org.apache.commons.csv.CSVPrinterTest.testJdbcPrinterWithResultSetHeader | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 0 | 1 | 1 |
| org.apache.commons.csv.CSVPrinterTest.testJdbcPrinterWithResultSetMetaData | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 0 | 1 |
| org.apache.commons.csv.CSVPrinterTest.testJdbcPrinterWithResultSetMetaData | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 0 | 1 | 1 |
| org.apache.commons.csv.CSVPrinterTest.testPrintCSVRecords | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 0 | 1 |
| org.apache.commons.csv.CSVPrinterTest.testPrintCSVRecords | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 0 | 1 | 1 |
| org.apache.commons.csv.Utils.compare | src/test/java/org/apache/commons/csv/Utils.java | 2 | 0 | 2 |
| org.apache.commons.csv.Utils.compare | src/test/java/org/apache/commons/csv/Utils.java | 0 | 2 | 2 |
