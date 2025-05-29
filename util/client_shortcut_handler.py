from pynput import keyboard as pynput_keyboard
from util.client_cosmic import Cosmic, console
from config import ClientConfig as Config
import sys
import platform

# 检查macOS权限
if platform.system() == 'Darwin':
    console.print("[yellow]注意：在macOS上，程序需要系统权限才能监听全局快捷键")
    console.print("[yellow]请在系统偏好设置 -> 安全性与隐私 -> 辅助功能 中添加Python或终端应用程序的访问权限")

import time
import asyncio
from threading import Event
from concurrent.futures import ThreadPoolExecutor
from util.client_send_audio import send_audio
from util.my_status import Status

task = asyncio.Future()
status = Status('开始录音', spinner='point')
pool = ThreadPoolExecutor()
pressed = False
released = True
event = Event()

def shortcut_correct(key: pynput_keyboard.Key):
    # 获取配置中的快捷键
    shortcut = Config.shortcut.lower()
    
    # 处理特殊键，添加macOS的特殊处理
    special_keys = {
        'ctrl': pynput_keyboard.Key.ctrl,
        'ctrl_l': pynput_keyboard.Key.ctrl_l,
        'ctrl_r': pynput_keyboard.Key.ctrl_r,
        'alt': pynput_keyboard.Key.alt,
        'alt_l': pynput_keyboard.Key.alt_l,
        'alt_r': pynput_keyboard.Key.alt_r,
        'shift': pynput_keyboard.Key.shift,
        'shift_l': pynput_keyboard.Key.shift_l,
        'shift_r': pynput_keyboard.Key.shift_r,
        'cmd': pynput_keyboard.Key.cmd,
        'cmd_l': pynput_keyboard.Key.cmd_l,
        'cmd_r': pynput_keyboard.Key.cmd_r
    }
    
    if shortcut in special_keys:
        return key == special_keys[shortcut]
    
    # 对于普通字符键，直接比较字符
    try:
        return key.char.lower() == shortcut
    except AttributeError:
        return False
    
    return False


def launch_task():
    global task

    # 记录开始时间
    t1 = time.time()

    # 将开始标志放入队列
    asyncio.run_coroutine_threadsafe(
        Cosmic.queue_in.put({'type': 'begin', 'time': t1, 'data': None}),
        Cosmic.loop
    )

    # 通知录音线程可以向队列放数据了
    Cosmic.on = t1

    # 打印动画：正在录音
    status.start()

    # 启动识别任务
    task = asyncio.run_coroutine_threadsafe(
        send_audio(),
        Cosmic.loop
    )


def cancel_task():
    # 通知停止录音，关掉滚动条
    Cosmic.on = False
    status.stop()

    # 取消协程任务
    task.cancel()


def finish_task():
    global task

    # 通知停止录音，关掉滚动条
    Cosmic.on = False
    status.stop()

    # 通知结束任务
    asyncio.run_coroutine_threadsafe(
        Cosmic.queue_in.put(
            {'type': 'finish',
             'time': time.time(),
             'data': None
             },
        ),
        Cosmic.loop
    )


# =================单击模式======================


def count_down(e: Event):
    """按下后，开始倒数"""
    time.sleep(Config.threshold)
    e.set()


def manage_task(e: Event):
    """
    通过检测 e 是否在 threshold 时间内被触发，判断是单击，还是长按
    进行下一步的动作
    """

    # 记录是否有任务
    on = Cosmic.on

    # 先运行任务
    if not on:
        launch_task()

    # 及时松开按键了，是单击
    if e.wait(timeout=Config.threshold * 0.8):
        # 如果有任务在运行，就结束任务
        if Cosmic.on and on:
            finish_task()

    # 没有及时松开按键，是长按
    else:
        # 就取消本栈启动的任务
        if not on:
            cancel_task()

        # 长按，发送按键
        pynput_keyboard.Controller().press(Config.shortcut)
        pynput_keyboard.Controller().release(Config.shortcut)


def click_mode(key: pynput_keyboard.Key):
    """单击模式"""
    global pressed, released, event

    if shortcut_correct(key):
        # 重置事件
        event.clear()
        # 开始倒计时
        pool.submit(count_down, event)
        # 之后再判断是单击还是长按
        pool.submit(manage_task, event)

    elif key == pynput_keyboard.Key.esc:
        pressed, released = False, True
        event.set()


# ======================长按模式==================================


def hold_mode(key: pynput_keyboard.Key, is_press=True):
    """像对讲机一样，按下录音，松开停止
    
    Args:
        key: 按键对象
        is_press: 是否是按下事件，如果是False则为松开事件
    """
    # 判断是否是目标快捷键
    if not shortcut_correct(key):
        return
    
    # 根据按下或松开执行不同操作
    if is_press:
        launch_task()
    else:
        finish_task()


def hold_handler(key: pynput_keyboard.Key, is_press=True):
    # 验证按键名正确
    if not shortcut_correct(key):
        # 不显示未匹配按键的调试信息
        return
    
    # 只对匹配的按键显示调试信息
    # print(f"Debug: hold_handler received key: {key}, is_press: {is_press}")
    # print(f"Debug: Current shortcut: {Config.shortcut}")

    # 长按模式
    # print(f"Debug: Key matched, {'starting' if is_press else 'stopping'} hold mode for: {key}")
    hold_mode(key, is_press)


def click_handler(key: pynput_keyboard.Key):
    # 验证按键名正确
    if not shortcut_correct(key):
        # 不显示未匹配按键的调试信息
        return
    
    # 只对匹配的按键显示调试信息
    # print(f"Debug: Key pressed: {key}")
    # print(f"Debug: Shortcut: {Config.shortcut}")

    # 单击模式
    # print("Debug: Key matched, starting click mode")
    click_mode(key)


def bond_shortcut():
    # 检查是否是macOS
    if platform.system() == 'Darwin':
        console.print("[yellow]注意：在macOS上，程序需要系统权限才能监听全局快捷键")
        console.print("[yellow]请在系统偏好设置 -> 安全性与隐私 -> 隐私 -> 辅助功能 中添加Python或终端应用程序的访问权限")
    
    # 设置键盘监听器
    
    if Config.mode == 'hold':
        # 长按模式需要区分按下和松开事件
        def on_press(key):
            return hold_handler(key, is_press=True)
            
        def on_release(key):
            return hold_handler(key, is_press=False)
            
        listener = pynput_keyboard.Listener(on_press=on_press, on_release=on_release)
    else:
        # 单击模式只需要按下事件
        listener = pynput_keyboard.Listener(on_press=click_handler)
    
    print("Debug: Starting keyboard listener")
    listener.start()