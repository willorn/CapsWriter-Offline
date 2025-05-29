#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
键盘监听测试脚本
用于测试在macOS上是否能正常监听键盘事件
"""

import platform
from pynput import keyboard
import time

print(f"当前操作系统: {platform.system()}")
print(f"Python版本: {platform.python_version()}")
print("pynput版本:", keyboard.__version__ if hasattr(keyboard, "__version__") else "未知")
print("\n" + "="*50)
print("键盘监听测试开始")
print("请按任意键，程序将显示按键信息")
print("按ESC键退出测试")
print("="*50 + "\n")

# 记录按键状态
key_count = 0
start_time = time.time()

def on_press(key):
    """按键按下时的回调函数"""
    global key_count
    key_count += 1
    
    try:
        # 尝试获取字符
        print(f"按键按下: '{key.char}' (字符键)")
    except AttributeError:
        # 特殊键
        print(f"按键按下: {key} (特殊键)")
    
    # 检查是否按下ESC键退出
    if key == keyboard.Key.esc:
        print("\n" + "="*50)
        print(f"测试结束，共检测到 {key_count} 个按键事件")
        print(f"测试持续时间: {time.time() - start_time:.2f} 秒")
        print("="*50)
        # 停止监听
        return False

def on_release(key):
    """按键释放时的回调函数"""
    try:
        # 尝试获取字符
        print(f"按键释放: '{key.char}' (字符键)")
    except AttributeError:
        # 特殊键
        print(f"按键释放: {key} (特殊键)")

# 创建监听器
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)

# 启动监听
listener.start()

# 等待监听器结束
try:
    listener.join()
except KeyboardInterrupt:
    print("\n程序被用户中断")
    print(f"测试结束，共检测到 {key_count} 个按键事件")
    print(f"测试持续时间: {time.time() - start_time:.2f} 秒")
