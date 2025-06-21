# YouTube Video Downloader

A high-quality Python script for downloading YouTube videos with proper error handling, configuration management, and progress tracking.

## Features

- **URL Validation**: Supports various YouTube URL formats
- **Quality Selection**: Choose from different video qualities (best, worst, 720p, 1080p, etc.)
- **Format Support**: Download in MP4, WebM, or MKV formats
- **Configuration Management**: Flexible YAML-based configuration
- **Progress Tracking**: Real-time download progress display
- **Error Handling**: Robust error handling with retry mechanism
- **Logging**: Comprehensive logging system
- **Command Line Interface**: Easy-to-use CLI

## Phase 1 Implementation Status

✅ **Core Functionality Completed:**
- URL Validator: Validates and processes YouTube URLs
- Video Downloader: Downloads videos using yt-dlp
- Configuration Manager: Manages download settings
- Unit Tests: Comprehensive test coverage
- Integration Tests: End-to-end workflow testing

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd youtube-downloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. For development:
```bash
pip install -r requirements-dev.txt
```

## Usage

### Command Line Interface

Basic usage:
```bash
python -m src.youtube_downloader.main "https://www.youtube.com/watch?v=VIDEO_ID"
```

With options:
```bash
python -m src.youtube_downloader.main \
    "https://www.youtube.com/shorts/FwYhFQHUn9g" \
    --quality 720p \
    --format mp4 \
    --output ./my_downloads
```

Show video information only:
```bash
python -m src.youtube_downloader.main \
    "https://www.youtube.com/watch?v=VIDEO_ID" \
    --info-only
```

Use custom configuration:
```bash
python -m src.youtube_downloader.main \
    "https://www.youtube.com/watch?v=VIDEO_ID" \
    --config my_config.yaml
```

### Command Line Options

- `url`: YouTube video URL (required)
- `-q, --quality`: Video quality (best, worst, 720p, 1080p, 480p, 360p)
- `-f, --format`: Output format (mp4, webm, mkv)
- `-o, --output`: Output directory
- `-c, --config`: Configuration file path
- `--info-only`: Show video information without downloading
- `-v, --verbose`: Enable verbose logging

### Programmatic Usage

```python
from src.youtube_downloader.core.validator import URLValidator
from src.youtube_downloader.core.downloader import VideoDownloader
from src.youtube_downloader.core.config import ConfigManager

# Validate URL
validator = URLValidator()
if validator.validate_youtube_url(url):
    video_id = validator.extract_video_id(url)

# Configure downloader
config_manager = ConfigManager()
config = config_manager.get_config()
downloader = VideoDownloader(config)

# Download video
result = downloader.download_video(url)
if result.success:
    print(f"Downloaded: {result.output_path}")
else:
    print(f"Error: {result.error_message}")
```

## Configuration

Create a YAML configuration file:

```yaml
download:
  quality: "720p"
  format: "mp4"
  audio_format: "mp3"

output:
  directory: "./downloads"
  naming_pattern: "{title}-{id}.{ext}"
  create_subdirs: false

network:
  concurrent_downloads: 3
  retry_attempts: 3
  timeout: 30
  rate_limit: null

logging:
  level: "INFO"
  file: "downloader.log"
  max_size: "10MB"
  backup_count: 5
```

## Testing

Run unit tests:
```bash
pytest tests/unit/ -v
```

Run integration tests:
```bash
pytest tests/integration/ -v
```

Run all tests with coverage:
```bash
pytest --cov=src/youtube_downloader --cov-report=html
```

## Architecture

The project follows clean architecture principles with clear separation of concerns:

- **Core Module**: Business logic (validator, downloader, config)
- **Utils Module**: Utility functions (planned for Phase 2)
- **CLI Module**: Command-line interface (planned for Phase 3)
- **Tests**: Comprehensive unit and integration tests

## Legal Notice

This tool is for educational and personal use only. Please respect YouTube's Terms of Service and copyright laws. Users are responsible for ensuring they have the right to download content.

## License

MIT License - see LICENSE file for details.

## Development Status

- **Phase 1**: ✅ Core functionality (URL validation, downloading, configuration)
- **Phase 2**: 🔄 Enhanced features (progress tracking, error handling, logging)
- **Phase 3**: 📋 User interface (CLI, batch processing)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for your changes
4. Ensure all tests pass
5. Submit a pull request

## Troubleshooting

### Common Issues

1. **yt-dlp import error**: Ensure yt-dlp is installed: `pip install yt-dlp`
2. **Permission denied**: Check write permissions for output directory
3. **Network errors**: Check internet connection and retry

### Logging

Check the `downloader.log` file for detailed error information and debugging.

For more help, please create an issue in the repository. 