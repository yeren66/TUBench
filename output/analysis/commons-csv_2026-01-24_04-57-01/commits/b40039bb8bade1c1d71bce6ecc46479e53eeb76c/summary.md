# Commit b40039bb

- **Commit**: `b40039bb8bade1c1d71bce6ecc46479e53eeb76c`
- **Parent**: `dd7b4b3e7753d177e18c4c0ef90fa89a1f66b673`
- **Author**: Gary Gregory
- **Date**: 2025-01-02 19:58:51
- **Message**: Merge pull request #502 from marklogic/CSV-196-master

## Execution & Coverage

| Version | Description | Compile | Execute | Changed-Line Coverage | Changed-Branch Coverage | Tests Run | Error |
|---------|-------------|---------|---------|-----------------------|-------------------------|-----------|-------|
| V-1 | Parent commit (baseline) | PASS | PASS | 0.7872 (37/47) | 0.7667 (23/30) | 2/3 | - |
| V-0.5 | Parent + source-only patch | PASS | FAIL | - | - | 2/0 | - |
| T-0.5 | Parent + test-only patch | PASS | FAIL | - | - | 3/0 | - |
| V0 | Full commit (source + tests) | PASS | PASS | 0.8485 (56/66) | 0.7895 (30/38) | 3/7 | - |

- **Tests Run** 显示为 *选定用例数/实际执行用例数*；若显示 skipped，表示该版本未能识别到可执行的变更测试。

## 分类

- **主类型**: type1_execution_error
- **场景**: A

## Change Summary

- **Total lines**: +321 / -7
- **Source files**: +164 / -6
- **Test files**: +157 / -1

### File Changes

| File | Type | +Lines | -Lines |
|------|------|--------|--------|
| pom.xml | other | 2 | 0 |
| src/main/java/org/apache/commons/csv/CSVParser.java | source | 49 | 3 |
| src/main/java/org/apache/commons/csv/CSVRecord.java | source | 18 | 3 |
| src/main/java/org/apache/commons/csv/ExtendedBufferedReader.java | source | 86 | 0 |
| src/main/java/org/apache/commons/csv/Lexer.java | source | 9 | 0 |
| src/test/java/org/apache/commons/csv/CSVParserTest.java | test | 70 | 0 |
| src/test/java/org/apache/commons/csv/CSVRecordTest.java | test | 1 | 1 |
| src/test/java/org/apache/commons/csv/JiraCsv196Test.java | test | 77 | 0 |
| src/test/resources/org/apache/commons/csv/CSV-196/emoji.csv | other | 5 | 0 |
| src/test/resources/org/apache/commons/csv/CSV-196/japanese.csv | other | 4 | 0 |

### Changed Methods (Source)

| Method | File | +Lines | -Lines | ΔLines | V-1 Line Cov | V-0.5 Line Cov | ΔCoverage |
|--------|------|--------|--------|--------|--------------|----------------|-----------|
| org.apache.commons.csv.Builder.get | src/main/java/org/apache/commons/csv/CSVParser.java | 1 | 1 | 2 | 0.0000 | 0.0000 | +0.0000 |
| org.apache.commons.csv.Builder.setRecordNumber | src/main/java/org/apache/commons/csv/CSVParser.java | 0 | 0 | 0 | 0.0000 | 0.0000 | +0.0000 |
| org.apache.commons.csv.Builder.setEnableByteTracking | src/main/java/org/apache/commons/csv/CSVParser.java | 4 | 0 | 4 | 0.0000 | 0.0000 | +0.0000 |
| org.apache.commons.csv.CSVParser.nextRecord | src/main/java/org/apache/commons/csv/CSVParser.java | 2 | 1 | 3 | 0.6897 | 0.0000 | -0.6897 |
| org.apache.commons.csv.CSVRecord.getCharacterPosition | src/main/java/org/apache/commons/csv/CSVRecord.java | 0 | 0 | 0 | 0.0000 | 0.0000 | +0.0000 |
| org.apache.commons.csv.CSVRecord.getBytePosition | src/main/java/org/apache/commons/csv/CSVRecord.java | 3 | 0 | 3 | 0.0000 | 0.0000 | +0.0000 |
| org.apache.commons.csv.ExtendedBufferedReader.mark | src/main/java/org/apache/commons/csv/ExtendedBufferedReader.java | 1 | 0 | 1 | 1.0000 | 0.0000 | -1.0000 |
| org.apache.commons.csv.ExtendedBufferedReader.read | src/main/java/org/apache/commons/csv/ExtendedBufferedReader.java | 3 | 0 | 3 | 1.0000 | 0.0000 | -1.0000 |
| org.apache.commons.csv.ExtendedBufferedReader.getEncodedCharLength | src/main/java/org/apache/commons/csv/ExtendedBufferedReader.java | 18 | 0 | 18 | 0.0000 | 0.0000 | +0.0000 |
| org.apache.commons.csv.ExtendedBufferedReader.reset | src/main/java/org/apache/commons/csv/ExtendedBufferedReader.java | 1 | 0 | 1 | 1.0000 | 0.0000 | -1.0000 |
| org.apache.commons.csv.ExtendedBufferedReader.getBytesRead | src/main/java/org/apache/commons/csv/ExtendedBufferedReader.java | 3 | 0 | 3 | 0.0000 | 0.0000 | +0.0000 |
| org.apache.commons.csv.Lexer.getCharacterPosition | src/main/java/org/apache/commons/csv/Lexer.java | 0 | 0 | 0 | 1.0000 | 0.0000 | -1.0000 |
| org.apache.commons.csv.Lexer.getBytesRead | src/main/java/org/apache/commons/csv/Lexer.java | 3 | 0 | 3 | 0.0000 | 0.0000 | +0.0000 |

### Changed Methods (Tests)

| Method | File | +Lines | -Lines | ΔLines |
|--------|------|--------|--------|--------|
| org.apache.commons.csv.CSVParserTest.testGetRecordThreeBytesRead | src/test/java/org/apache/commons/csv/CSVParserTest.java | 34 | 0 | 34 |
| org.apache.commons.csv.CSVParserTest.testGetRecordFourBytesRead | src/test/java/org/apache/commons/csv/CSVParserTest.java | 32 | 0 | 32 |
| org.apache.commons.csv.CSVRecordTest.testCSVRecordNULLValues | src/test/java/org/apache/commons/csv/CSVRecordTest.java | 1 | 1 | 2 |
| org.apache.commons.csv.JiraCsv196Test.parseThreeBytes | src/test/java/org/apache/commons/csv/JiraCsv196Test.java | 18 | 0 | 18 |
| org.apache.commons.csv.JiraCsv196Test.parseFourBytes | src/test/java/org/apache/commons/csv/JiraCsv196Test.java | 18 | 0 | 18 |
| org.apache.commons.csv.JiraCsv196Test.getTestInput | src/test/java/org/apache/commons/csv/JiraCsv196Test.java | 4 | 0 | 4 |

### Selected Tests

- `org.apache.commons.csv.CSVParserTest#testGetHeaderComment_NoComment3+testGetHeaderMap`
- `org.apache.commons.csv.CSVParserTest#testGetHeaderComment_NoComment3+testGetHeaderMap+testGetRecordFourBytesRead+testGetRecordThreeBytesRead`
- `org.apache.commons.csv.CSVRecordTest#testCSVRecordNULLValues`
- `org.apache.commons.csv.JiraCsv196Test`
