"""
Setup configuration for YouTube Downloader package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
def read_requirements(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

requirements = read_requirements('requirements.txt')
dev_requirements = read_requirements('requirements-dev.txt')

setup(
    name="youtube-downloader",
    version="1.0.0",
    author="AI Assistant",
    author_email="ai@example.com",
    description="A high-quality Python script for downloading YouTube videos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/youtube-downloader",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
    },
    entry_points={
        "console_scripts": [
            "youtube-downloader=youtube_downloader.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "youtube_downloader": ["../config/*.yaml"],
    },
) 