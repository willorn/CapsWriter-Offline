
import websockets 
from util.client_cosmic import Cosmic, console
from config import ClientConfig as Config


class Handler:
    def __enter__(self):...

    def __exit__(self, exc_type, e, exc_tb):
        if e == None:
            return True
        if isinstance(e, ConnectionRefusedError):
            return True
        elif isinstance(e, TimeoutError):
            return True
        elif isinstance(e, Exception):
            return True
        else:
            print(e)


async def check_websocket() -> bool:
    if Cosmic.websocket and Cosmic.websocket.state == websockets.protocol.State.OPEN:
        return True
    for _ in range(3):
        with Handler():
            Cosmic.websocket = await websockets.connect(f"ws://{Config.addr}:{Config.port}", max_size=None)
            return True
    else:
        console.print(f"[red]无法连接到服务器。请检查服务器是否运行以及配置是否正确。")
        return False

    # for _ in range(3):
    #     try:
    #         Cosmic.websocket = await websockets.connect(f"ws://{Config.addr}:{Config.port}", max_size=None)
    #         return True
    #     except ConnectionRefusedError as e:
    #         continue
    #     except TimeoutError:
    #         continue
    #     except Exception as e:
    #         print(e)
    #
    # else:
    #     return False
