# YouTube批量搜索下载功能

## 功能概述

YouTube下载器现在支持批量搜索下载功能，允许用户通过关键词搜索YouTube视频，并根据指定的参数（数量、时长等）批量下载符合条件的视频。

## 核心特性

- 🔍 **智能搜索**：支持关键词搜索YouTube视频
- 📊 **灵活过滤**：时长、质量、上传时间等多维度过滤
- 📥 **批量处理**：一键搜索多个符合条件的视频
- 🎯 **精确控制**：用户可指定下载数量和各种限制条件
- 📈 **进度跟踪**：实时显示搜索和过滤进度
- 🔄 **错误恢复**：完善的重试机制和错误处理

## 快速开始

### 基础搜索示例

```python
from youtube_downloader.core import SearchEngine, SearchConfig

# 创建搜索配置
config = SearchConfig(
    search_query="Python programming tutorial",
    max_results=10,
    sort_by="relevance"
)

# 执行搜索
engine = SearchEngine(config)
results = engine.search_videos("Python programming tutorial")

# 显示结果
for video in results:
    print(f"标题: {video.title}")
    print(f"时长: {video.get_duration_formatted()}")
    print(f"观看量: {video.view_count:,}")
    print(f"链接: {video.get_url()}")
    print("-" * 40)
```

### 高级过滤示例

```python
from youtube_downloader.core import SearchConfig, FilterConfig

# 创建过滤配置
filter_config = FilterConfig(
    min_duration=300,      # 至少5分钟
    max_duration=1800,     # 最多30分钟
    min_view_count=10000,  # 至少1万观看量
    exclude_shorts=True,   # 排除YouTube Shorts
    exclude_live=True,     # 排除直播
    min_upload_date="2023-01-01"  # 只要2023年后的视频
)

# 创建搜索配置
config = SearchConfig(
    search_query="机器学习教程",
    max_results=20,
    sort_by="view_count",
    filter_config=filter_config
)

# 执行搜索
engine = SearchEngine(config)
results = engine.search_videos("机器学习教程")

print(f"找到 {len(results)} 个符合条件的视频")
```

## 核心模块

### 1. SearchConfig - 搜索配置

搜索配置管理所有搜索相关的参数：

```python
from youtube_downloader.core import SearchConfig, FilterConfig

config = SearchConfig(
    search_query="",           # 搜索关键词
    max_results=10,            # 最大结果数量
    sort_by="relevance",       # 排序方式: relevance, upload_date, view_count, rating
    upload_date="any",         # 上传时间: hour, today, week, month, year, any
    filter_config=FilterConfig(),  # 过滤配置
    max_concurrent_downloads=3,    # 最大并发下载数
    retry_failed_downloads=True    # 是否重试失败的下载
)
```

#### 排序选项
- `relevance`: 相关性排序（默认）
- `upload_date`: 按上传时间排序
- `view_count`: 按观看量排序
- `rating`: 按评分排序

#### 上传时间过滤
- `hour`: 最近1小时
- `today`: 今天
- `week`: 最近一周
- `month`: 最近一个月
- `year`: 最近一年
- `any`: 不限制（默认）

### 2. FilterConfig - 过滤配置

过滤配置定义视频筛选条件：

```python
from youtube_downloader.core import FilterConfig

filter_config = FilterConfig(
    min_duration=None,         # 最小时长（秒）
    max_duration=None,         # 最大时长（秒）
    min_quality=None,          # 最小质量 (目前预留)
    exclude_shorts=True,       # 排除YouTube Shorts (<60秒)
    exclude_live=True,         # 排除直播流
    min_upload_date=None,      # 最早上传日期 (ISO格式)
    min_view_count=None        # 最小观看量
)
```

#### 时长过滤示例
```python
# 只要5-30分钟的视频
filter_config = FilterConfig(
    min_duration=300,   # 5分钟
    max_duration=1800   # 30分钟
)

# 只要长视频（超过1小时）
filter_config = FilterConfig(
    min_duration=3600   # 1小时
)
```

#### 观看量过滤示例
```python
# 只要热门视频（超过10万观看）
filter_config = FilterConfig(
    min_view_count=100000
)
```

### 3. SearchEngine - 搜索引擎

搜索引擎负责执行实际的视频搜索：

```python
from youtube_downloader.core import SearchEngine

engine = SearchEngine(config)

# 执行搜索
results = engine.search_videos("关键词", max_results=15)

# 获取搜索统计信息
stats = engine.get_search_statistics()
print(stats)
```

#### 错误处理
```python
from youtube_downloader.core import NetworkSearchError, YouTubeSearchError

try:
    results = engine.search_videos("关键词")
except NetworkSearchError as e:
    print(f"网络错误: {e}")
except YouTubeSearchError as e:
    print(f"YouTube错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

### 4. VideoSearchResult - 搜索结果

搜索结果包含视频的所有元数据：

```python
# VideoSearchResult 对象属性
video.video_id          # 视频ID
video.title             # 标题
video.duration          # 时长（秒）
video.uploader          # 上传者
video.upload_date       # 上传日期
video.view_count        # 观看量
video.thumbnail_url     # 缩略图URL
video.description       # 描述
video.like_count        # 点赞数

# 实用方法
video.get_url()                    # 获取YouTube URL
video.is_short()                   # 是否为YouTube Short
video.is_live_stream()             # 是否为直播
video.get_duration_formatted()     # 格式化时长显示
```

### 5. SearchConfigManager - 配置管理器

配置管理器提供配置验证和动态更新：

```python
from youtube_downloader.core import SearchConfigManager

# 初始化管理器
manager = SearchConfigManager()

# 更新配置
manager.update_config(
    search_query="新关键词",
    max_results=25,
    filter_min_duration=600,
    filter_exclude_shorts=True
)

# 获取配置
config = manager.get_config()

# 验证配置
manager.validate_config(config)

# 保存/加载配置
manager.save_config("search_config.yaml")
manager.load_config("search_config.yaml")
```

## 高级用法

### 配置文件支持

可以使用YAML配置文件来管理搜索设置：

```yaml
# search_config.yaml
search:
  query: "Python教程"
  max_results: 20
  sort_by: "view_count"
  upload_date: "month"

filter:
  min_duration: 300
  max_duration: 1800
  min_view_count: 5000
  exclude_shorts: true
  exclude_live: true
  min_upload_date: "2023-01-01"

batch:
  max_concurrent_downloads: 3
  retry_failed_downloads: true
```

```python
# 加载配置文件
manager = SearchConfigManager()
manager.load_config("search_config.yaml")
config = manager.get_config()
```

### 批量搜索不同关键词

```python
keywords = [
    "Python基础教程",
    "机器学习入门", 
    "数据分析实战",
    "深度学习课程"
]

all_results = []
for keyword in keywords:
    engine = SearchEngine(SearchConfig(
        search_query=keyword,
        max_results=5,
        filter_config=FilterConfig(min_duration=600)
    ))
    
    results = engine.search_videos(keyword)
    all_results.extend(results)
    print(f"{keyword}: 找到 {len(results)} 个视频")

print(f"总共找到 {len(all_results)} 个视频")
```

### 搜索结果分析

```python
# 分析过滤效果
filter_config = FilterConfig(min_view_count=10000)
engine = SearchEngine(SearchConfig(
    search_query="编程教程",
    filter_config=filter_config
))

# 获取过滤统计
raw_results = [...]  # 原始搜索结果
stats = engine.video_filter.count_filtered_by_criteria(raw_results)

print(f"总视频数: {stats['total']}")
print(f"短视频数: {stats['shorts']}")
print(f"直播数: {stats['live_streams']}")
print(f"观看量不足: {stats['view_count_too_low']}")
```

### 自定义过滤逻辑

```python
def custom_filter(videos):
    """自定义过滤函数"""
    filtered = []
    for video in videos:
        # 自定义过滤条件
        if ("教程" in video.title and 
            video.duration > 600 and
            video.view_count > 1000):
            filtered.append(video)
    return filtered

# 使用自定义过滤
results = engine.search_videos("编程")
custom_results = custom_filter(results)
```

## 实际应用场景

### 场景1：学习资源收集

```python
# 收集编程学习资源
config = SearchConfig(
    search_query="Python零基础教程",
    max_results=30,
    sort_by="view_count",
    filter_config=FilterConfig(
        min_duration=1200,     # 至少20分钟的完整教程
        min_view_count=50000,  # 确保质量
        exclude_shorts=True,
        min_upload_date="2022-01-01"  # 相对较新的内容
    )
)
```

### 场景2：特定主题内容筛选

```python
# 筛选机器学习实战项目
config = SearchConfig(
    search_query="机器学习项目实战",
    max_results=15,
    sort_by="upload_date",  # 最新内容优先
    filter_config=FilterConfig(
        min_duration=1800,     # 至少30分钟
        max_duration=7200,     # 最多2小时
        min_view_count=10000,
        exclude_live=True
    )
)
```

### 场景3：快速概览内容

```python
# 快速了解某个主题的热门内容
config = SearchConfig(
    search_query="区块链技术",
    max_results=10,
    sort_by="view_count",
    filter_config=FilterConfig(
        min_duration=300,      # 至少5分钟
        max_duration=900,      # 最多15分钟
        min_view_count=100000  # 高质量内容
    )
)
```

## 性能优化建议

### 1. 合理设置搜索数量
```python
# 推荐的搜索数量设置
config = SearchConfig(
    max_results=20,  # 通常10-50个结果比较合适
    # 避免设置过大的数量，会影响搜索速度
)
```

### 2. 使用有效的过滤条件
```python
# 有效的过滤策略
filter_config = FilterConfig(
    exclude_shorts=True,    # 显著减少结果数量
    exclude_live=True,      # 排除不稳定的直播内容
    min_duration=120,       # 排除过短的视频
    min_view_count=1000     # 排除质量可能较低的视频
)
```

### 3. 错误处理和重试
```python
import time
from youtube_downloader.core import NetworkSearchError

def robust_search(query, max_retries=3):
    for attempt in range(max_retries):
        try:
            engine = SearchEngine(SearchConfig(search_query=query))
            return engine.search_videos(query)
        except NetworkSearchError as e:
            if attempt < max_retries - 1:
                print(f"网络错误，{2**attempt}秒后重试...")
                time.sleep(2**attempt)  # 指数退避
                continue
            raise e
```

## 注意事项

1. **API限制**：yt-dlp搜索功能依赖于YouTube的数据，请合理使用避免被限制
2. **网络环境**：确保网络连接稳定，某些地区可能需要代理
3. **内容变化**：YouTube内容实时变化，搜索结果可能不完全一致
4. **版权声明**：请确保下载的内容符合版权要求，仅用于个人学习使用

## 故障排除

### 常见问题

1. **搜索无结果**
   - 检查搜索关键词是否正确
   - 尝试放宽过滤条件
   - 确认网络连接正常

2. **过滤结果过少**
   - 降低最小观看量要求
   - 增加时长范围
   - 关闭某些过滤选项

3. **搜索速度慢**
   - 减少max_results数量
   - 检查网络连接速度
   - 避免过于复杂的过滤条件

### 日志调试

```python
import logging

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)

# 搜索时会输出详细的调试信息
engine = SearchEngine(config)
results = engine.search_videos("关键词")
```

## 更新日志

### 版本 1.0.0
- ✅ 基础搜索功能
- ✅ 视频过滤系统
- ✅ 配置管理
- ✅ 错误处理
- ✅ 集成测试
- ✅ 使用文档

### 计划功能
- 🔄 批量下载管理器集成
- 🔄 GUI界面支持
- �� 搜索历史记录
- 🔄 智能推荐功能 