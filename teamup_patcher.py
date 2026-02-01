import asyncio
from time import time, sleep

from wizwalker import XYZ, ClientHandler, Client, Keycode
from wizwalker.memory import MemoryReader, Window
from typing import Union, List


async def patch(client:Client) -> List[tuple[int, bytes]]:
    async def readbytes_writebytes(pattern:bytes, write_bytes:int) -> tuple[int, bytes]:
        add = await reader.pattern_scan(pattern, return_multiple=False, module="WizardGraphicalClient.exe")
        print(hex(add))
        old_bytes = await reader.read_bytes(add, len(write_bytes))
        await reader.write_bytes(add, write_bytes)
        return (add, old_bytes)
    
    address_oldbytes = [] 
    reader = MemoryReader(client._pymem)

    async def teamup_kiosk_level_locked_patch():
        write_bytes = b"\xE9\x90\x05\x00\x00\x90"
        pattern = rb"\x0F\x84\x8F\x05\x00\x00\x0F\x57\xC0"
        address_oldbytes.append(await readbytes_writebytes(pattern, write_bytes))

    await teamup_kiosk_level_locked_patch()

    return address_oldbytes

async def reset_patch(client: Client, address_bytes: List[tuple[int, bytes]]):
    reader = MemoryReader(client._pymem)
    for address, oldbytes in address_bytes:
        await reader.write_bytes(address, oldbytes)

async def main():
    handler = ClientHandler()
    client = handler.get_new_clients()[0]
    address_bytes = []
    try:
        print("Preparing")
        address_bytes = await patch(client)
        print("Done")
        while True:
            await asyncio.sleep(0.1)
    finally:
        if address_bytes:
            await reset_patch(client, address_bytes)
        print("Closing")
        await handler.close()


if __name__ == "__main__":
    asyncio.run(main())
