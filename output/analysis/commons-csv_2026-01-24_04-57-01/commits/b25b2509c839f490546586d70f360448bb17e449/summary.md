# Commit b25b2509

- **Commit**: `b25b2509c839f490546586d70f360448bb17e449`
- **Parent**: `a557344f3d2f5b9c2f58a8859533914772a2dbf1`
- **Author**: Gary Gregory
- **Date**: 2025-03-07 21:11:27
- **Message**: CSVPrinter.printRecords(Iterable) knows how to use CSVFormat's maxRows

## Execution & Coverage

| Version | Description | Compile | Execute | Changed-Line Coverage | Changed-Branch Coverage | Tests Run | Error |
|---------|-------------|---------|---------|-----------------------|-------------------------|-----------|-------|
| V-1 | Parent commit (baseline) | PASS | PASS | 1.0000 (2/2) | - | 3/7 | - |
| V-0.5 | Parent + source-only patch | PASS | PASS | 0.8000 (4/5) | 0.5000 (1/2) | 3/7 | - |
| T-0.5 | Parent + test-only patch | PASS | PASS | 1.0000 (2/2) | - | 3/7 | - |
| V0 | Full commit (source + tests) | PASS | PASS | 1.0000 (5/5) | 1.0000 (2/2) | 3/11 | - |

- **Tests Run** 显示为 *选定用例数/实际执行用例数*；若显示 skipped，表示该版本未能识别到可执行的变更测试。

## 分类

- **主类型**: type2_coverage_decrease
- **场景**: D

## Change Summary

- **Total lines**: +24 / -17
- **Source files**: +7 / -2
- **Test files**: +17 / -15

### File Changes

| File | Type | +Lines | -Lines |
|------|------|--------|--------|
| src/changes/changes.xml | other | 2 | 1 |
| src/main/java/org/apache/commons/csv/CSVPrinter.java | source | 5 | 1 |
| src/test/java/org/apache/commons/csv/CSVParserTest.java | test | 4 | 4 |
| src/test/java/org/apache/commons/csv/CSVPrinterTest.java | test | 10 | 9 |
| src/test/java/org/apache/commons/csv/Utils.java | test | 3 | 2 |

### Changed Methods (Source)

| Method | File | +Lines | -Lines | ΔLines | V-1 Line Cov | V-0.5 Line Cov | ΔCoverage |
|--------|------|--------|--------|--------|--------------|----------------|-----------|
| org.apache.commons.csv.CSVPrinter.printRecords | src/main/java/org/apache/commons/csv/CSVPrinter.java | 5 | 1 | 6 | 1.0000 | 0.8000 | -0.2000 |

### Changed Methods (Tests)

| Method | File | +Lines | -Lines | ΔLines |
|--------|------|--------|--------|--------|
| org.apache.commons.csv.CSVParserTest.testBackslashEscaping | src/test/java/org/apache/commons/csv/CSVParserTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVParserTest.testBackslashEscaping2 | src/test/java/org/apache/commons/csv/CSVParserTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVParserTest.testDefaultFormat | src/test/java/org/apache/commons/csv/CSVParserTest.java | 2 | 2 | 4 |
| org.apache.commons.csv.CSVPrinterTest.doOneRandom | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testPrintCSVParser | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testPrintCSVRecord | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVPrinterTest.testPrintCSVRecords | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 4 | 0 | 4 |
| org.apache.commons.csv.CSVPrinterTest.testPrintCSVRecords | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 0 | 4 | 4 |
| org.apache.commons.csv.CSVPrinterTest.testPrintRecordStream | src/test/java/org/apache/commons/csv/CSVPrinterTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.Utils.compare | src/test/java/org/apache/commons/csv/Utils.java | 2 | 0 | 2 |
| org.apache.commons.csv.Utils.compare | src/test/java/org/apache/commons/csv/Utils.java | 0 | 2 | 2 |

### Selected Tests

- `org.apache.commons.csv.CSVParserTest#testBackslashEscaping+testBackslashEscaping2+testDefaultFormat`
- `org.apache.commons.csv.CSVPrinterTest#testPrintCSVParser+testPrintCSVRecord+testPrintCSVRecords+testPrintRecordStream`
- `org.apache.commons.csv.Utils`
