# Commit 76981db6

- **Commit**: `76981db68af50e0475a2d5d0fcc6bdf87efb18f1`
- **Parent**: `5e5512fd068213d099920b00971ca3fe1185511c`
- **Author**: Gary Gregory
- **Date**: 2025-01-02 20:14:13
- **Message**: Sort members

## Execution & Coverage

| Version | Description | Compile | Execute | Changed-Line Coverage | Changed-Branch Coverage | Tests Run | Error |
|---------|-------------|---------|---------|-----------------------|-------------------------|-----------|-------|
| V-1 | Parent commit (baseline) | PASS | PASS | 0.8478 (39/46) | 0.8462 (22/26) | 1/130 | - |
| V-0.5 | Parent + source-only patch | PASS | PASS | 0.8478 (39/46) | 0.8462 (22/26) | 1/130 | - |
| T-0.5 | Parent + test-only patch | PASS | PASS | 0.8478 (39/46) | 0.8462 (22/26) | 1/130 | - |
| V0 | Full commit (source + tests) | PASS | PASS | 0.8478 (39/46) | 0.8462 (22/26) | 1/130 | - |

- **Tests Run** 显示为 *选定用例数/实际执行用例数*；若显示 skipped，表示该版本未能识别到可执行的变更测试。

## 分类

- **主类型**: type3_adaptive_change
- **场景**: D

## Change Summary

- **Total lines**: +154 / -154
- **Source files**: +84 / -84
- **Test files**: +70 / -70

### File Changes

| File | Type | +Lines | -Lines |
|------|------|--------|--------|
| src/main/java/org/apache/commons/csv/CSVParser.java | source | 12 | 12 |
| src/main/java/org/apache/commons/csv/CSVRecord.java | source | 10 | 10 |
| src/main/java/org/apache/commons/csv/ExtendedBufferedReader.java | source | 54 | 54 |
| src/main/java/org/apache/commons/csv/Lexer.java | source | 8 | 8 |
| src/test/java/org/apache/commons/csv/CSVParserTest.java | test | 70 | 70 |

### Changed Methods (Source)

| Method | File | +Lines | -Lines | ΔLines | V-1 Line Cov | V-0.5 Line Cov | ΔCoverage |
|--------|------|--------|--------|--------|--------------|----------------|-----------|
| org.apache.commons.csv.Builder.setCharacterOffset | src/main/java/org/apache/commons/csv/CSVParser.java | 0 | 0 | 0 | 0.0000 | 0.0000 | +0.0000 |
| org.apache.commons.csv.Builder.setEnableByteTracking | src/main/java/org/apache/commons/csv/CSVParser.java | 4 | 4 | 8 | 0.0000 | 0.0000 | +0.0000 |
| org.apache.commons.csv.Builder.setRecordNumber | src/main/java/org/apache/commons/csv/CSVParser.java | 0 | 0 | 0 | 0.0000 | 0.0000 | +0.0000 |
| org.apache.commons.csv.CSVRecord.get | src/main/java/org/apache/commons/csv/CSVRecord.java | 0 | 0 | 0 | 0.4545 | 0.4545 | +0.0000 |
| org.apache.commons.csv.CSVRecord.getBytePosition | src/main/java/org/apache/commons/csv/CSVRecord.java | 0 | 0 | 0 | 1.0000 | 1.0000 | +0.0000 |
| org.apache.commons.csv.CSVRecord.getCharacterPosition | src/main/java/org/apache/commons/csv/CSVRecord.java | 3 | 3 | 6 | 1.0000 | 1.0000 | +0.0000 |
| org.apache.commons.csv.ExtendedBufferedReader.close | src/main/java/org/apache/commons/csv/ExtendedBufferedReader.java | 0 | 0 | 0 | 1.0000 | 1.0000 | +0.0000 |
| org.apache.commons.csv.ExtendedBufferedReader.getBytesRead | src/main/java/org/apache/commons/csv/ExtendedBufferedReader.java | 3 | 3 | 6 | 1.0000 | 1.0000 | +0.0000 |
| org.apache.commons.csv.ExtendedBufferedReader.getEncodedCharLength | src/main/java/org/apache/commons/csv/ExtendedBufferedReader.java | 18 | 18 | 36 | 0.9091 | 0.9091 | +0.0000 |
| org.apache.commons.csv.ExtendedBufferedReader.read | src/main/java/org/apache/commons/csv/ExtendedBufferedReader.java | 0 | 0 | 0 | 1.0000 | 1.0000 | +0.0000 |
| org.apache.commons.csv.ExtendedBufferedReader.reset | src/main/java/org/apache/commons/csv/ExtendedBufferedReader.java | 0 | 0 | 0 | 1.0000 | 1.0000 | +0.0000 |
| org.apache.commons.csv.Lexer.close | src/main/java/org/apache/commons/csv/Lexer.java | 0 | 0 | 0 | 1.0000 | 1.0000 | +0.0000 |
| org.apache.commons.csv.Lexer.getBytesRead | src/main/java/org/apache/commons/csv/Lexer.java | 2 | 2 | 4 | 1.0000 | 1.0000 | +0.0000 |
| org.apache.commons.csv.Lexer.getCharacterPosition | src/main/java/org/apache/commons/csv/Lexer.java | 2 | 2 | 4 | 1.0000 | 1.0000 | +0.0000 |

### Changed Methods (Tests)

| Method | File | +Lines | -Lines | ΔLines |
|--------|------|--------|--------|--------|
| org.apache.commons.csv.CSVParserTest.testGetRecordThreeBytesRead | src/test/java/org/apache/commons/csv/CSVParserTest.java | 34 | 34 | 68 |
| org.apache.commons.csv.CSVParserTest.testGetRecordFourBytesRead | src/test/java/org/apache/commons/csv/CSVParserTest.java | 32 | 32 | 64 |

### Selected Tests

- `org.apache.commons.csv.CSVParserTest`
