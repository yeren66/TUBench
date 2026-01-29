# 版本兼容性处理指南

当分析年代久远的 commits 时，可能会遇到以下兼容性问题：

## 常见问题

### 1. Java 版本不兼容

**症状：**
```
[ERROR] Source option 5 is no longer supported. Use 7 or later.
[ERROR] Target option 5 is no longer supported. Use 7 or later.
[ERROR] invalid target release: 1.5
```

**原因：** 
- 现代 JDK (11+) 不再支持编译 Java 5/6 源代码
- 项目 pom.xml 中指定了过低的 source/target 版本

**解决方案：**

1. **使用旧版 JDK（推荐）**
   
   在 `config.py` 中设置 `JAVA_HOME`：
   ```python
   class AnalysisConfig:
       JAVA_HOME = "/usr/lib/jvm/java-8-openjdk-amd64"
   ```

2. **使用 SDKMAN 管理多版本 Java**
   ```bash
   # 安装 SDKMAN
   curl -s "https://get.sdkman.io" | bash
   
   # 安装旧版 Java
   sdk install java 8.0.382-zulu
   
   # 在配置中使用
   JAVA_HOME = "/home/user/.sdkman/candidates/java/8.0.382-zulu"
   ```

3. **使用 Maven 参数强制覆盖**
   ```python
   MAVEN_EXTRA_ARGS = "-Dmaven.compiler.source=8 -Dmaven.compiler.target=8"
   ```

### 2. Maven 插件版本问题

**症状：**
```
[ERROR] Could not find artifact org.apache.maven.plugins:maven-compiler-plugin:jar:2.3.2
[ERROR] Plugin org.apache.maven.plugins:maven-xxx-plugin:1.0 not found
```

**解决方案：**

1. **使用旧版 Maven**
   ```python
   # 下载旧版 Maven
   # wget https://archive.apache.org/dist/maven/maven-3/3.6.3/binaries/apache-maven-3.6.3-bin.tar.gz
   
   MAVEN_EXECUTABLE = "/opt/apache-maven-3.6.3/bin/mvn"
   ```

2. **使用 Maven Wrapper（如果项目提供）**
   - 许多现代项目包含 `mvnw` 脚本，会自动使用正确版本

### 3. 依赖获取失败

**症状：**
```
[ERROR] Could not resolve dependencies for project
[ERROR] Could not find artifact com.example:library:jar:1.0.0
[ERROR] Connection refused
```

**原因：**
- 依赖库已从公共仓库移除
- 仓库 URL 已变更或关闭
- SSL 证书问题

**解决方案：**

1. **配置镜像仓库**
   
   创建或修改 `~/.m2/settings.xml`：
   ```xml
   <settings>
     <mirrors>
       <mirror>
         <id>aliyun</id>
         <mirrorOf>central</mirrorOf>
         <url>https://maven.aliyun.com/repository/central</url>
       </mirror>
     </mirrors>
   </settings>
   ```

2. **添加额外仓库**
   
   某些旧版依赖可能需要从特定仓库获取。

3. **处理 SSL 问题**
   ```python
   MAVEN_EXTRA_ARGS = "-Dmaven.wagon.http.ssl.insecure=true"
   ```

## 配置选项说明

在 `config.py` 的 `AnalysisConfig` 类中：

```python
# ========== 版本兼容性配置 ==========

# Java版本（设置JAVA_HOME环境变量路径，None表示使用系统默认）
JAVA_HOME = None

# Maven可执行文件路径（None表示使用PATH中的mvn）
MAVEN_EXECUTABLE = None

# 额外的Maven参数（用于解决兼容性问题）
MAVEN_EXTRA_ARGS = ""

# 是否在遇到兼容性问题时跳过commit（而不是标记为失败）
SKIP_INCOMPATIBLE_COMMITS = False

# 是否尝试自动修复常见的兼容性问题
AUTO_FIX_COMPATIBILITY = False
```

## 诊断输出

当遇到兼容性问题时，工具会在错误信息中添加诊断提示：

```
[COMPATIBILITY ISSUES DETECTED]
⚠️  Java版本不兼容: 源代码版本过低，当前JDK不支持
⚠️  依赖解析失败: 无法解析项目依赖

[ERROR] ...具体错误信息...
```

## 推荐的多版本环境配置

### 方案一：Docker 容器（最隔离）

```dockerfile
FROM maven:3.6.3-jdk-8

WORKDIR /app
COPY . .

# 运行分析
RUN python analysis.py
```

### 方案二：使用 SDKMAN（推荐）

```bash
# 安装多版本 Java
sdk install java 8.0.382-zulu
sdk install java 11.0.20-zulu
sdk install java 17.0.8-zulu

# 切换版本
sdk use java 8.0.382-zulu

# 然后运行分析
python analysis.py
```

### 方案三：项目级配置

创建项目特定的配置：

```python
# 针对特定项目的配置
PROJECT_CONFIGS = {
    'old-project-2010': {
        'JAVA_HOME': '/opt/jdk1.6.0_45',
        'MAVEN_EXECUTABLE': '/opt/apache-maven-2.2.1/bin/mvn'
    },
    'modern-project': {
        'JAVA_HOME': None,  # 使用系统默认
        'MAVEN_EXECUTABLE': None
    }
}
```

## 最佳实践

1. **先尝试默认配置** - 许多项目使用 Maven Wrapper 或有兼容的配置

2. **检查项目文档** - README 通常会说明所需的 Java 版本

3. **查看 pom.xml** - 检查 `maven.compiler.source` 和 `maven.compiler.target`

4. **考虑跳过过旧 commits** - 如果只关注较新的测试演化，可以调整 `DATE_FILTER`

5. **使用日期过滤** - 在 `config.py` 中设置合理的起始日期：
   ```python
   DATE_FILTER = "2016-01-01"  # 只分析 2016 年之后的 commits
   ```

## 常见项目的推荐配置

| 项目 | 推荐 Java | 说明 |
|------|----------|------|
| commons-* 2015前 | Java 6/7 | Apache Commons 旧版本 |
| commons-* 2015后 | Java 8+ | 现代 Apache Commons |
| Spring 4.x | Java 7/8 | Spring Framework 4 |
| Spring 5.x | Java 8+ | Spring Framework 5 |
| Mockito 2.x | Java 8+ | Mockito 2 系列 |
