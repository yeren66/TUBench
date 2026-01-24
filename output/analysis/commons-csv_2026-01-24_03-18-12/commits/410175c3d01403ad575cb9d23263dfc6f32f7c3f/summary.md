# Commit 410175c3

- **Commit**: `410175c3d01403ad575cb9d23263dfc6f32f7c3f`
- **Parent**: `bf09a8b676e6d3077b62df034209e875b45f112b`
- **Author**: Gary Gregory
- **Date**: 2025-05-06 21:46:14
- **Message**: [CSV-318] CSVPrinter.printRecord(Stream) hangs if given a parallel

## Execution & Coverage

| Version | Description | Compile | Execute | Changed-Line Coverage | Changed-Branch Coverage | Tests Run | Error |
|---------|-------------|---------|---------|-----------------------|-------------------------|-----------|-------|
| V-1 | Parent commit (baseline) | PASS | SKIP | 0.3333 (3/9) | 0.0000 (0/4) | 6 (skipped) | Skipped |
| V-0.5 | Parent + source-only patch | PASS | SKIP | 0.4545 (5/11) | 0.0000 (0/4) | 6 (skipped) | Skipped |
| T-0.5 | Parent + test-only patch | PASS | SKIP | 0.3333 (3/9) | 0.0000 (0/4) | 6 (skipped) | Skipped |
| V0 | Full commit (source + tests) | PASS | PASS | 0.4545 (5/11) | 0.0000 (0/4) | 5 | - |

- **Tests Run** 表示本次仅执行的变更测试用例数量；若显示 skipped，表示该版本未能识别到可执行的变更测试。

## 分类

- **主类型**: type3_adaptive_change
- **场景**: D

## Change Summary

- **Total lines**: +12 / -23
- **Source files**: +12 / -3
- **Test files**: +0 / -20

### File Changes

| File | Type | +Lines | -Lines |
|------|------|--------|--------|
| src/changes/changes.xml | other | 1 | 0 |
| src/main/java/org/apache/commons/csv/CSVPrinter.java | source | 11 | 3 |
| src/test/java/org/apache/commons/csv/JiraCsv318Test.java | test | 0 | 20 |

### Changed Methods (Source)

| Method | File | +Lines | -Lines | ΔLines | V-1 Line Cov | V-0.5 Line Cov | ΔCoverage |
|--------|------|--------|--------|--------|--------------|----------------|-----------|
| org.apache.commons.csv.CSVPrinter.printRecord | src/main/java/org/apache/commons/csv/CSVPrinter.java | 8 | 3 | 11 | 1.0000 | 1.0000 | +0.0000 |
| org.apache.commons.csv.CSVPrinter.printRecordObject | src/main/java/org/apache/commons/csv/CSVPrinter.java | 0 | 0 | 0 | 0.0000 | 0.0000 | +0.0000 |

### Changed Methods (Tests)

| Method | File | +Lines | -Lines | ΔLines |
|--------|------|--------|--------|--------|
| org.apache.commons.csv.JiraCsv318Test.printRecord | src/test/java/org/apache/commons/csv/JiraCsv318Test.java | 0 | 3 | 3 |
| org.apache.commons.csv.JiraCsv318Test.testParallelIOStreamSynchronizedPrinter | src/test/java/org/apache/commons/csv/JiraCsv318Test.java | 0 | 10 | 10 |
