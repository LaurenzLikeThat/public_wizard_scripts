import asyncio

from wizwalker import HotkeyListener, ClientHandler, Client, Keycode, ModifierKeys
from wizwalker.memory import WindowFlags
from wizwalker.errors import PatternFailed
from loguru import logger

# Written by LaurenzNotHere

MINIMAP_TOGGLE_HOTKEY = "F2"
PROGRAM_KILL_HOTKEY = "F9"

async def main():
    handler = ClientHandler()
    clients = handler.get_new_clients()
    listener: HotkeyListener = None
    listener_is_enabled = False

    async def minimap_toggle():
        async def toggle_all_clients(client: Client):
            windows = await client.root_window.get_windows_with_type("BattlegroundMiniMapWindow")
            if windows:
                minimap_window = windows[0]

                logger.debug(f"{MINIMAP_TOGGLE_HOTKEY} key pressed, toggling minimap.")

                curr_flags = await minimap_window.flags()
                await minimap_window.write_flags(curr_flags ^ WindowFlags(WindowFlags.visible) ^ WindowFlags(WindowFlags.disabled))
            else:
                logger.debug("No Windows Found.")

        await asyncio.gather(*[toggle_all_clients(client) for client in clients])

    async def kill_tool():
        logger.debug(f"{PROGRAM_KILL_HOTKEY} key pressed, killing program.")
        raise KeyboardInterrupt

    try:
        logger.debug("Preparing")
        await asyncio.gather(*[client.hook_handler.activate_root_window_hook() for client in clients])
        logger.debug("Successfully Activated Hooks!")

        logger.debug("Enabling Listener and adding Hotkeys.")
        listener = HotkeyListener()
        listener.start()

        await listener.add_hotkey(Keycode[MINIMAP_TOGGLE_HOTKEY], minimap_toggle, modifiers=ModifierKeys.NOREPEAT)
        await listener.add_hotkey(Keycode[PROGRAM_KILL_HOTKEY], kill_tool, modifiers=ModifierKeys.NOREPEAT)

        logger.debug("Listener Enabled!")
        listener_is_enabled = True

        while True:
            await asyncio.sleep(0.1)

    except PatternFailed as e:
        logger.critical(f"{e}")

    finally:
        if listener_is_enabled:
            await listener.clear()
        logger.debug("Closing")
        await handler.close()


if __name__ == "__main__":
    asyncio.run(main())
