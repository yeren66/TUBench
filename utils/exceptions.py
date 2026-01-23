"""
TUBench 异常定义模块

定义项目中使用的异常层次结构，区分可恢复和不可恢复错误。
"""


class TUBenchException(Exception):
    """TUBench 基础异常类"""
    
    def __init__(self, message, details=None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


# ============ 可恢复异常 ============
# 这类异常发生时，可以跳过当前项目继续处理其他项

class RecoverableError(TUBenchException):
    """可恢复错误 - 跳过当前项继续处理"""
    pass


class ParseError(RecoverableError):
    """解析错误 - Java代码、Diff、XML等解析失败"""
    pass


class GitOperationError(RecoverableError):
    """Git操作错误 - checkout、diff、apply等失败"""
    pass


class CompilationError(RecoverableError):
    """编译错误 - Maven编译失败"""
    pass


class CoverageError(RecoverableError):
    """覆盖率分析错误 - JaCoCo报告解析失败"""
    pass


# ============ 致命异常 ============
# 这类异常发生时，应该终止整个执行

class FatalError(TUBenchException):
    """致命错误 - 终止执行"""
    pass


class ConfigurationError(FatalError):
    """配置错误 - 无法继续运行"""
    pass


class RepositoryError(FatalError):
    """仓库错误 - 仓库不存在或损坏"""
    pass
