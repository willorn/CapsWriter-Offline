from config import ClientConfig as Config
from pynput import keyboard as pynput_keyboard
import pyclip
import platform
import asyncio


async def type_result(text):

    # 模拟粘贴
    if Config.paste:

        # 保存剪切板
        try:
            temp = pyclip.paste().decode('utf-8')
        except:
            temp = ''

        # 复制结果
        pyclip.copy(text)

        # 粘贴结果
        if platform.system() == 'Darwin':
            controller = pynput_keyboard.Controller()
            controller.press(pynput_keyboard.Key.cmd)
            controller.press('v')
            controller.release(pynput_keyboard.Key.cmd)
            controller.release('v')
        else:
            controller = pynput_keyboard.Controller()
            controller.press(pynput_keyboard.Key.ctrl)
            controller.press('v')
            controller.release(pynput_keyboard.Key.ctrl)
            controller.release('v')

        # 还原剪贴板
        if Config.restore_clip:
            await asyncio.sleep(0.1)
            pyclip.copy(temp)

    # 模拟打印
    else:
        controller = pynput_keyboard.Controller()
        controller.type(text)
