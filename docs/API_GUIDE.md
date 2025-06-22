# YouTube Downloader API Guide

## 快速开始

### 启动API服务

```bash
# Python启动
python start_api.py

# Windows启动
start_api.bat

# 开发模式
python start_api.py --dev
```

### 访问文档

- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 主要端点

### 视频操作

```bash
# 获取视频信息
POST /api/v1/video/info
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}

# 下载视频
POST /api/v1/video/download
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "quality": "720p",
    "format": "mp4"
}
```

### 搜索功能

```bash
# 搜索视频
POST /api/v1/search/videos
{
    "query": "Python tutorial",
    "max_results": 10,
    "min_duration": 300,
    "max_duration": 1800
}
```

### 批量下载

```bash
# 开始批量下载
POST /api/v1/batch/download
{
    "urls": ["url1", "url2"],
    "quality": "720p"
}

# 查看进度
GET /api/v1/batch/progress/{task_id}
```

## Python客户端示例

```python
import requests

# 搜索视频
response = requests.post("http://localhost:8000/api/v1/search/videos",
                        json={"query": "Python tutorial", "max_results": 5})
results = response.json()

# 下载视频
response = requests.post("http://localhost:8000/api/v1/video/download",
                        json={"url": "https://www.youtube.com/watch?v=VIDEO_ID"})
download_info = response.json()
```

更多详细信息请查看 examples/api_usage_example.py 