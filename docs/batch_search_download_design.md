# YouTube批量搜索下载功能设计文档

## 1. 项目概述

### 1.1 功能描述
为现有的YouTube下载器项目添加批量搜索下载功能，用户可以通过输入关键词搜索YouTube视频，并根据指定的参数（数量、时长等）批量下载符合条件的视频。

### 1.2 核心特性
- 🔍 **智能搜索**：支持关键词搜索YouTube视频
- 📊 **灵活过滤**：时长、质量、上传时间等多维度过滤
- 📥 **批量下载**：一键下载多个符合条件的视频
- 🎯 **精确控制**：用户可指定下载数量和各种限制条件
- 📈 **进度跟踪**：实时显示搜索和下载进度
- 🔄 **错误恢复**：完善的重试机制和错误处理

## 2. 技术架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                    GUI Layer                            │
│  ┌─────────────────┐  ┌─────────────────────────────────┐ │
│  │  Search Panel   │  │    Batch Progress Panel        │ │
│  └─────────────────┘  └─────────────────────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────────────────────┐ │
│  │  Result List    │  │    Settings Panel              │ │
│  └─────────────────┘  └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                   Service Layer                         │
│  ┌─────────────────┐  ┌─────────────────────────────────┐ │
│  │ Search Engine   │  │    Batch Download Manager      │ │
│  └─────────────────┘  └─────────────────────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────────────────────┐ │
│  │ Video Filter    │  │    Search Config Manager       │ │
│  └─────────────────┘  └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                    Core Layer                           │
│  ┌─────────────────┐  ┌─────────────────────────────────┐ │
│  │ Video Downloader│  │    YouTube API/yt-dlp          │ │
│  │   (existing)    │  │         Wrapper                │ │
│  └─────────────────┘  └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 2.2 核心模块设计

#### 2.2.1 搜索引擎模块 (SearchEngine)

**文件位置**: `src/youtube_downloader/core/search_engine.py`

**主要功能**:
- YouTube视频搜索
- 搜索结果解析和处理
- 多种搜索策略支持

**核心类设计**:
```python
class SearchEngine:
    def __init__(self, config: SearchConfig)
    def search_videos(self, query: str, max_results: int) -> List[VideoSearchResult]
    def get_video_details(self, video_ids: List[str]) -> List[VideoInfo]
    
class VideoSearchResult:
    video_id: str
    title: str
    duration: int
    uploader: str
    upload_date: str
    view_count: int
    thumbnail_url: str
```

#### 2.2.2 视频过滤器模块 (VideoFilter)

**文件位置**: `src/youtube_downloader/core/video_filter.py`

**主要功能**:
- 基于时长的过滤
- 基于质量的过滤
- 基于内容的过滤
- 自定义过滤规则

**核心类设计**:
```python
class VideoFilter:
    def __init__(self, filter_config: FilterConfig)
    def filter_by_duration(self, videos: List[VideoSearchResult], min_duration: int, max_duration: int) -> List[VideoSearchResult]
    def filter_by_quality(self, videos: List[VideoSearchResult], min_quality: str) -> List[VideoSearchResult]
    def apply_all_filters(self, videos: List[VideoSearchResult]) -> List[VideoSearchResult]

class FilterConfig:
    min_duration: Optional[int] = None  # 秒
    max_duration: Optional[int] = None  # 秒
    min_quality: Optional[str] = None   # "720p", "1080p", etc.
    exclude_shorts: bool = True
    exclude_live: bool = True
```

#### 2.2.3 批量下载管理器 (BatchDownloadManager)

**文件位置**: `src/youtube_downloader/core/batch_manager.py`

**主要功能**:
- 下载队列管理
- 并发下载控制
- 进度聚合和回调
- 错误处理和重试

**核心类设计**:
```python
class BatchDownloadManager:
    def __init__(self, downloader: VideoDownloader, config: BatchConfig)
    def add_to_queue(self, videos: List[VideoSearchResult])
    def start_batch_download(self) -> None
    def pause_download(self) -> None
    def resume_download(self) -> None
    def cancel_download(self) -> None
    def get_progress(self) -> BatchProgress

class BatchProgress:
    total_videos: int
    completed_videos: int
    failed_videos: int
    current_video: Optional[str]
    overall_progress: float
    download_speed: str
    eta: str
```

#### 2.2.4 搜索配置管理器 (SearchConfig)

**文件位置**: `src/youtube_downloader/core/search_config.py`

**主要功能**:
- 搜索参数配置
- 过滤条件配置
- 下载设置配置

**核心类设计**:
```python
class SearchConfig:
    # 搜索参数
    search_query: str
    max_results: int = 10
    sort_by: str = "relevance"  # "relevance", "upload_date", "view_count", "rating"
    upload_date: str = "any"    # "hour", "today", "week", "month", "year", "any"
    
    # 过滤参数
    filter_config: FilterConfig
    
    # 下载参数 (继承现有配置)
    download_config: DownloadConfig
    
    # 批量下载参数
    max_concurrent_downloads: int = 3
    retry_failed_downloads: bool = True
```

### 2.3 API集成策略

#### 2.3.1 主要方案：yt-dlp搜索功能

**优点**:
- 免费使用，无API限制
- 与现有下载功能无缝集成
- 不需要额外的API密钥配置

**实现方式**:
```python
# 使用yt-dlp的搜索功能
search_url = f"ytsearch{max_results}:{query}"
with yt_dlp.YoutubeDL(opts) as ydl:
    search_results = ydl.extract_info(search_url, download=False)
```

#### 2.3.2 备选方案：YouTube Data API v3

**优点**:
- 官方API，功能强大
- 搜索精度高
- 支持更多高级搜索选项

**实现方式**:
```python
# 预留接口，支持YouTube Data API
class YouTubeAPISearcher:
    def __init__(self, api_key: str)
    def search_videos(self, query: str, **kwargs) -> List[VideoSearchResult]
```

## 3. GUI界面设计

### 3.1 界面布局

采用标签页设计，在现有GUI基础上添加"批量搜索下载"标签页：

```
┌─────────────────────────────────────────────────────────┐
│ ┌─────────────────┐ ┌─────────────────────────────────┐ │
│ │  单视频下载      │ │      批量搜索下载              │ │
│ └─────────────────┘ └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 3.2 批量搜索下载界面组件

#### 3.2.1 搜索面板 (SearchPanel)

**文件位置**: `src/youtube_downloader/gui/components/search_panel.py`

**组件内容**:
- 搜索关键词输入框
- 下载数量选择器 (1-100)
- 时长限制设置 (最小/最大时长滑块)
- 排序方式选择 (相关性/上传时间/观看量)
- 高级选项折叠面板
- 搜索按钮

#### 3.2.2 搜索结果列表 (ResultList)

**文件位置**: `src/youtube_downloader/gui/components/result_list.py`

**组件内容**:
- 搜索结果表格：
  - 选择框
  - 缩略图
  - 标题 (可点击预览)
  - 时长
  - 上传者
  - 观看量
  - 上传时间
- 批量操作按钮：全选/全取消/反选
- 下载选中视频按钮

#### 3.2.3 批量下载进度面板 (BatchProgressPanel)

**文件位置**: `src/youtube_downloader/gui/components/batch_progress.py`

**组件内容**:
- 整体进度条和百分比
- 当前下载视频信息
- 详细下载列表：
  - 视频标题
  - 下载状态 (等待/下载中/完成/失败)
  - 个人进度条
  - 文件大小/下载速度
- 控制按钮：暂停/恢复/取消
- 实时日志显示区域

### 3.3 用户交互流程

```
用户输入搜索关键词
         ↓
    设置搜索参数
         ↓
      点击搜索
         ↓
   显示搜索结果
         ↓
   用户选择视频
         ↓
   点击批量下载
         ↓
   显示下载进度
         ↓
     下载完成
```

## 4. 文件结构规划

### 4.1 新增目录结构

```
src/youtube_downloader/
├── core/
│   ├── search_engine.py      # 搜索引擎
│   ├── video_filter.py       # 视频过滤器
│   ├── batch_manager.py      # 批量下载管理器
│   └── search_config.py      # 搜索配置管理
├── gui/
│   └── components/
│       ├── search_panel.py       # 搜索面板
│       ├── result_list.py        # 结果列表
│       └── batch_progress.py     # 批量进度
└── utils/
    ├── youtube_api.py        # YouTube API封装 (可选)
    └── video_metadata.py     # 视频元数据处理

tests/
├── test_search_engine.py     # 搜索引擎测试
├── test_batch_manager.py     # 批量管理器测试
└── test_video_filter.py      # 过滤器测试
```

### 4.2 依赖更新

在 `requirements.txt` 中添加：
```
google-api-python-client>=2.0.0  # YouTube Data API (可选)
aiohttp>=3.8.0                   # 异步HTTP请求
asyncio>=3.4.3                   # 异步支持
```

## 5. 开发实施计划

### 5.1 开发阶段

#### 阶段1：核心搜索功能
- [ ] 实现 `SearchEngine` 类
- [ ] 实现 `VideoFilter` 类  
- [ ] 实现 `SearchConfig` 类
- [ ] 编写单元测试
- [ ] 集成测试验证搜索功能

#### 阶段2：批量下载管理
- [ ] 实现 `BatchDownloadManager` 类
- [ ] 实现队列管理和并发控制
- [ ] 实现进度聚合和回调机制
- [ ] 错误处理和重试机制
- [ ] 编写单元测试和集成测试

#### 阶段3：GUI界面开发
- [ ] 实现 `SearchPanel` 组件
- [ ] 实现 `ResultList` 组件
- [ ] 实现 `BatchProgressPanel` 组件
- [ ] 集成到主界面
- [ ] 界面样式和用户体验优化

#### 阶段4：集成测试和优化
- [ ] 端到端功能测试
- [ ] 性能测试和优化
- [ ] 内存使用优化
- [ ] 错误处理完善

#### 阶段5：文档和发布准备
- [ ] 用户文档编写
- [ ] API文档完善
- [ ] 代码注释补充
- [ ] 发布版本准备

### 5.2 关键里程碑

- **里程碑1**: 完成核心搜索功能，能够搜索并过滤YouTube视频
- **里程碑2**: 完成批量下载管理器，支持队列下载
- **里程碑3**: 完成GUI界面，提供完整的用户交互体验
- **里程碑4**: 通过所有测试，准备正式发布

## 6. 风险评估与应对策略

### 6.1 技术风险

#### 风险1：YouTube搜索API稳定性
**风险描述**: yt-dlp搜索功能可能不稳定或被限制
**应对策略**: 
- 实现多种搜索源的备选方案
- 添加重试机制和错误恢复
- 预留YouTube Data API接口

#### 风险2：批量下载性能问题
**风险描述**: 大量并发下载可能导致被YouTube限制或系统性能问题
**应对策略**:
- 实现智能的并发控制机制
- 添加请求频率限制
- 监控系统资源使用情况

#### 风险3：内存管理问题
**风险描述**: 大批量搜索结果可能占用过多内存
**应对策略**:
- 实现分页加载机制
- 及时释放不必要的数据
- 添加内存使用监控

### 6.2 用户体验风险

#### 风险1：界面复杂性
**风险描述**: 新增功能可能使界面过于复杂
**应对策略**:
- 采用渐进式披露设计原则
- 提供简化模式和高级模式
- 充分的用户测试和反馈收集

#### 风险2：学习成本
**风险描述**: 用户需要学习新功能的使用方法
**应对策略**:
- 提供详细的使用文档
- 添加界面提示和引导
- 设计直观的用户界面

## 7. 质量保证策略

### 7.1 测试策略

#### 单元测试
- 搜索引擎功能测试
- 视频过滤器测试
- 批量下载管理器测试
- 配置管理测试
- 目标覆盖率：≥80%

#### 集成测试
- 搜索到下载的完整流程测试
- GUI与后端的集成测试
- 错误处理流程测试

#### 性能测试
- 大批量搜索性能测试
- 并发下载性能测试
- 内存使用压力测试
- 网络异常恢复测试

### 7.2 代码质量

#### 代码规范
- 遵循PEP 8编码规范
- 使用类型注解提高代码可读性
- 充分的代码注释和文档字符串

#### 代码审查
- 所有代码变更需要经过代码审查
- 关注安全性、性能和可维护性
- 确保遵循现有的架构模式

## 8. 总结

本设计文档详细规划了YouTube批量搜索下载功能的完整实现方案。通过模块化的架构设计、清晰的开发计划和完善的质量保证策略，确保新功能能够高质量地集成到现有项目中。

### 8.1 预期收益

- **用户体验提升**: 用户可以快速批量下载感兴趣的视频
- **功能完整性**: 从单视频下载扩展到批量智能下载
- **代码质量**: 保持高质量的代码结构和测试覆盖率
- **可维护性**: 模块化设计便于后续功能扩展

### 8.2 后续扩展方向

- 支持播放列表批量下载
- 智能推荐相关视频
- 下载历史和统计功能
- 云存储集成
- 移动端适配
