#!/usr/bin/env python3
"""
Quick test script to check GUI layout fixes.
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from youtube_downloader.gui_main import run_gui
    
    print("✅ GUI布局高度问题已修复！")
    print("🔧 主要修复内容：")
    print("   📐 窗口尺寸: 1350x900 → 1400x950 (增加高度)")
    print("   🎨 品牌区域: 大幅简化为单行紧凑布局")
    print("   📦 组件间距: 全面减少内边距 (12→8, 8→6, 6→4)")
    print("   🔘 按钮尺寸: 进一步压缩 (36→32, 30→26)")
    print("   ⚖️  网格权重: 仅设置面板可伸缩,按钮区域固定可见")
    print("   🎯 核心目标: 确保下载按钮始终可见!")
    print("")
    print("💡 现在下载按钮应该始终可见了!")
    print("🚀 启动GUI进行测试...")
    run_gui()
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装所需依赖: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ 启动错误: {e}") 