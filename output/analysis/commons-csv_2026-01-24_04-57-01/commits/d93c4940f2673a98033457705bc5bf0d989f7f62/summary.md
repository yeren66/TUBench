# Commit d93c4940

- **Commit**: `d93c4940f2673a98033457705bc5bf0d989f7f62`
- **Parent**: `c36d6cdeabac051bc74c1490263df129e3c0750d`
- **Author**: Gary Gregory
- **Date**: 2025-03-14 20:29:53
- **Message**: CSVParser.parse(*) methods with a null Charset maps to

## Execution & Coverage

| Version | Description | Compile | Execute | Changed-Line Coverage | Changed-Branch Coverage | Tests Run | Error |
|---------|-------------|---------|---------|-----------------------|-------------------------|-----------|-------|
| V-1 | Parent commit (baseline) | PASS | PASS | 0.7188 (23/32) | 0.6250 (10/16) | 1/5 | - |
| V-0.5 | Parent + source-only patch | PASS | PASS | 0.7188 (23/32) | 0.6250 (10/16) | 1/5 | - |
| T-0.5 | Parent + test-only patch | PASS | PASS | 0.7188 (23/32) | 0.6250 (10/16) | 1/5 | - |
| V0 | Full commit (source + tests) | PASS | PASS | 0.7188 (23/32) | 0.6250 (10/16) | 1/5 | - |

- **Tests Run** 显示为 *选定用例数/实际执行用例数*；若显示 skipped，表示该版本未能识别到可执行的变更测试。

## 分类

- **主类型**: type3_adaptive_change
- **场景**: D

## Change Summary

- **Total lines**: +35 / -28
- **Source files**: +27 / -22
- **Test files**: +8 / -6

### File Changes

| File | Type | +Lines | -Lines |
|------|------|--------|--------|
| src/changes/changes.xml | other | 1 | 0 |
| src/main/java/org/apache/commons/csv/CSVParser.java | source | 26 | 22 |
| src/test/java/org/apache/commons/csv/CSVParserTest.java | test | 8 | 6 |

### Changed Methods (Source)

| Method | File | +Lines | -Lines | ΔLines | V-1 Line Cov | V-0.5 Line Cov | ΔCoverage |
|--------|------|--------|--------|--------|--------------|----------------|-----------|
| org.apache.commons.csv.CSVParser.parse | src/main/java/org/apache/commons/csv/CSVParser.java | 1 | 1 | 2 | 1.0000 | 1.0000 | +0.0000 |
| org.apache.commons.csv.CSVParser.nextRecord | src/main/java/org/apache/commons/csv/CSVParser.java | 0 | 0 | 0 | 0.7000 | 0.7000 | +0.0000 |

### Changed Methods (Tests)

| Method | File | +Lines | -Lines | ΔLines |
|--------|------|--------|--------|--------|
| org.apache.commons.csv.CSVParserTest.testParse | src/test/java/org/apache/commons/csv/CSVParserTest.java | 1 | 2 | 3 |
| org.apache.commons.csv.CSVParserTest.testParserUrlNullCharsetFormat | src/test/java/org/apache/commons/csv/CSVParserTest.java | 6 | 2 | 8 |
| org.apache.commons.csv.CSVParserTest.testParseUrlCharsetNullFormat | src/test/java/org/apache/commons/csv/CSVParserTest.java | 1 | 2 | 3 |

### Selected Tests

- `org.apache.commons.csv.CSVParserTest#testParse+testParsePathCharsetNullFormat+testParseStringNullFormat+testParseUrlCharsetNullFormat+testParserUrlNullCharsetFormat`
