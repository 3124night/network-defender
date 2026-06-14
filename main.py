#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络守护者 (Network Defender)
Python网络自动化课程设计项目

游戏简介:
    一款融合网络自动化概念的塔防游戏。玩家扮演网络安全工程师，
    通过部署各种网络防御设施来保护核心服务器免受病毒、黑客和恶意软件的攻击。

技术栈:
    - Python 3.13.5
    - Pygame 2.6.0
    - PyCharm 2024.1.6

操作说明:
    - 鼠标左键: 选择并放置防御塔
    - 鼠标右键: 取消选择
    - 数字键 1-5: 快速选择防御塔类型
    - 空格键: 暂停/继续游戏
    - ESC键: 返回菜单

作者: 课程设计项目
日期: 2026-06-14
"""

import sys
import os

# 确保当前目录在路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from game_engine import main

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n游戏已退出")
        sys.exit(0)
    except Exception as e:
        print(f"游戏发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
