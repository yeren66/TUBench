# Commit cf393fc6

- **Commit**: `cf393fc6a2a46953fa02fe7453db4aa6c9c9fae0`
- **Parent**: `9b75f05c9934cad8cc0886a7215e5c936e92662d`
- **Author**: Gary Gregory
- **Date**: 2025-03-09 18:24:30
- **Message**: CSVParser.iterator() knows how to use CSVFormat's maxRows

## Execution & Coverage

| Version | Description | Compile | Execute | Changed-Line Coverage | Changed-Branch Coverage | Tests Run | Error |
|---------|-------------|---------|---------|-----------------------|-------------------------|-----------|-------|
| V-1 | Parent commit (baseline) | PASS | PASS | 0.2222 (4/18) | 0.2778 (5/18) | 1/144 | - |
| V-0.5 | Parent + source-only patch | PASS | PASS | 0.3158 (6/19) | 0.5000 (11/22) | 1/144 | - |
| T-0.5 | Parent + test-only patch | PASS | PASS | 0.2222 (4/18) | 0.2778 (5/18) | 1/144 | - |
| V0 | Full commit (source + tests) | PASS | PASS | 0.3158 (6/19) | 0.5000 (11/22) | 1/152 | - |

- **Tests Run** 显示为 *选定用例数/实际执行用例数*；若显示 skipped，表示该版本未能识别到可执行的变更测试。

## 分类

- **主类型**: type3_adaptive_change
- **场景**: D

## Change Summary

- **Total lines**: +47 / -7
- **Source files**: +19 / -7
- **Test files**: +28 / -0

### File Changes

| File | Type | +Lines | -Lines |
|------|------|--------|--------|
| src/changes/changes.xml | other | 1 | 0 |
| src/main/java/org/apache/commons/csv/CSVFormat.java | source | 10 | 2 |
| src/main/java/org/apache/commons/csv/CSVParser.java | source | 7 | 3 |
| src/main/java/org/apache/commons/csv/CSVPrinter.java | source | 1 | 2 |
| src/test/java/org/apache/commons/csv/CSVParserTest.java | test | 28 | 0 |

### Changed Methods (Source)

| Method | File | +Lines | -Lines | ΔLines | V-1 Line Cov | V-0.5 Line Cov | ΔCoverage |
|--------|------|--------|--------|--------|--------------|----------------|-----------|
| org.apache.commons.csv.CSVFormat.isQuoteCharacterSet | src/main/java/org/apache/commons/csv/CSVFormat.java | 0 | 0 | 0 | 1.0000 | 1.0000 | +0.0000 |
| org.apache.commons.csv.CSVFormat.limit | src/main/java/org/apache/commons/csv/CSVFormat.java | 1 | 1 | 2 | 1.0000 | 1.0000 | +0.0000 |
| org.apache.commons.csv.CSVFormat.trim | src/main/java/org/apache/commons/csv/CSVFormat.java | 0 | 0 | 0 | 1.0000 | 1.0000 | +0.0000 |
| org.apache.commons.csv.CSVFormat.useMaxRows | src/main/java/org/apache/commons/csv/CSVFormat.java | 3 | 0 | 3 | 0.0000 | 1.0000 | +1.0000 |
| org.apache.commons.csv.CSVFormat.useRow | src/main/java/org/apache/commons/csv/CSVFormat.java | 3 | 0 | 3 | 0.0000 | 1.0000 | +1.0000 |
| org.apache.commons.csv.CSVRecordIterator.getNextRecord | src/main/java/org/apache/commons/csv/CSVParser.java | 5 | 1 | 6 | 0.0000 | 0.0000 | +0.0000 |
| org.apache.commons.csv.CSVRecordIterator.hasNext | src/main/java/org/apache/commons/csv/CSVParser.java | 0 | 0 | 0 | 0.0000 | 0.0000 | +0.0000 |
| org.apache.commons.csv.CSVParser.stream | src/main/java/org/apache/commons/csv/CSVParser.java | 1 | 1 | 2 | 1.0000 | 1.0000 | +0.0000 |
| org.apache.commons.csv.CSVPrinter.printRecords | src/main/java/org/apache/commons/csv/CSVPrinter.java | 1 | 2 | 3 | 0.0000 | 0.0000 | +0.0000 |

### Changed Methods (Tests)

| Method | File | +Lines | -Lines | ΔLines |
|--------|------|--------|--------|--------|
| org.apache.commons.csv.CSVParserTest.testIteratorMaxRows | src/test/java/org/apache/commons/csv/CSVParserTest.java | 25 | 0 | 25 |

### Selected Tests

- `org.apache.commons.csv.CSVParserTest`
