# Commit 0b0003e3

- **Commit**: `0b0003e3b3cdad863092390b4d4ed5dbf78779a5`
- **Parent**: `c75601d2a3426adf1671572766cc65906812fa73`
- **Author**: Gary Gregory
- **Date**: 2025-01-02 20:19:20
- **Message**: Simplify new API name and parameter names

## Execution & Coverage

| Version | Description | Compile | Execute | Changed-Line Coverage | Changed-Branch Coverage | Tests Run | Error |
|---------|-------------|---------|---------|-----------------------|-------------------------|-----------|-------|
| V-1 | Parent commit (baseline) | PASS | PASS | - | - | 2/4 | - |
| V-0.5 | Parent + source-only patch | PASS | FAIL | - | - | 2/0 | - |
| T-0.5 | Parent + test-only patch | PASS | PASS | - | - | 2/4 | - |
| V0 | Full commit (source + tests) | PASS | PASS | - | - | 2/4 | - |

- **Tests Run** 显示为 *选定用例数/实际执行用例数*；若显示 skipped，表示该版本未能识别到可执行的变更测试。

## 分类

- **主类型**: type1_execution_error
- **场景**: B

## Change Summary

- **Total lines**: +24 / -24
- **Source files**: +20 / -20
- **Test files**: +4 / -4

### File Changes

| File | Type | +Lines | -Lines |
|------|------|--------|--------|
| src/main/java/org/apache/commons/csv/CSVParser.java | source | 17 | 17 |
| src/main/java/org/apache/commons/csv/ExtendedBufferedReader.java | source | 3 | 3 |
| src/test/java/org/apache/commons/csv/CSVParserTest.java | test | 2 | 2 |
| src/test/java/org/apache/commons/csv/JiraCsv196Test.java | test | 2 | 2 |

### Changed Methods (Source)

| Method | File | +Lines | -Lines | ΔLines | V-1 Line Cov | V-0.5 Line Cov | ΔCoverage |
|--------|------|--------|--------|--------|--------------|----------------|-----------|
| org.apache.commons.csv.Builder.get | src/main/java/org/apache/commons/csv/CSVParser.java | 1 | 1 | 2 | 0.0000 | 0.0000 | +0.0000 |
| org.apache.commons.csv.Builder.setCharacterOffset | src/main/java/org/apache/commons/csv/CSVParser.java | 0 | 0 | 0 | 0.0000 | 0.0000 | +0.0000 |
| org.apache.commons.csv.Builder.setRecordNumber | src/main/java/org/apache/commons/csv/CSVParser.java | 0 | 0 | 0 | 0.0000 | 0.0000 | +0.0000 |
| org.apache.commons.csv.Builder.setTrackBytes | src/main/java/org/apache/commons/csv/CSVParser.java | 4 | 0 | 4 | 0.0000 | 0.0000 | +0.0000 |

### Changed Methods (Tests)

| Method | File | +Lines | -Lines | ΔLines |
|--------|------|--------|--------|--------|
| org.apache.commons.csv.CSVParserTest.testGetRecordFourBytesRead | src/test/java/org/apache/commons/csv/CSVParserTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.CSVParserTest.testGetRecordThreeBytesRead | src/test/java/org/apache/commons/csv/CSVParserTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.JiraCsv196Test.testParseFourBytes | src/test/java/org/apache/commons/csv/JiraCsv196Test.java | 1 | 1 | 2 |
| org.apache.commons.csv.JiraCsv196Test.testParseThreeBytes | src/test/java/org/apache/commons/csv/JiraCsv196Test.java | 1 | 1 | 2 |

### Selected Tests

- `org.apache.commons.csv.CSVParserTest#testGetRecordFourBytesRead+testGetRecordThreeBytesRead`
- `org.apache.commons.csv.JiraCsv196Test#testParseFourBytes+testParseThreeBytes`
