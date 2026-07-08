import asyncio

from wizwalker import ClientHandler, Client
from wizwalker.memory import MemoryReader, Window
from wizwalker.errors import PatternFailed
from loguru import logger
from typing import List

CACHED_ADDRESSES = {}

# Written by LaurenzNotHere

async def patch(client:Client) -> List[tuple[int, bytes]]:
    async def readbytes_writebytes(pattern:bytes, write_bytes:bytes, patch_name:str, offset: int = 0) -> tuple[int, bytes]:
        add = 0
        if patch_name not in CACHED_ADDRESSES:
            add = await reader.pattern_scan(pattern, return_multiple=False, module="WizardGraphicalClient.exe") + offset
            print(f"{patch_name} found at {hex(add)}")
            CACHED_ADDRESSES[patch_name] = add
        else:
            add = CACHED_ADDRESSES[patch_name]

        old_bytes = await reader.read_bytes(add, len(write_bytes))
        await reader.write_bytes(add, write_bytes)
        return (add, old_bytes)
    
    address_oldbytes = []
    reader = MemoryReader(client._pymem)

    async def inactive_adventure_party_remove_patch():
        write_bytes = b"\x48\x31\xC0\xC3\x90"
        pattern = rb"\x48\x89\x5C\x24.\x55\x56\x57\x41\x54\x41\x55\x41\x56\x41\x57\x48\x8D\xAC\x24...." \
                  rb"\x48\x81\xEC....\x48\x8B\x05....\x48\x33\xC4\x48\x89\x85....\x48\x8B\xDA\x4C\x8B\xE9" \
                  rb"\x45\x33\xFF\x41\x8B\xFF"
        address_oldbytes.append(await readbytes_writebytes(pattern, write_bytes, "inactive_adventure_party_remove_patch"))

    patches = [
        inactive_adventure_party_remove_patch(),
    ]

    await asyncio.gather(*patches)

    return address_oldbytes

async def reset_patch(client: Client, address_bytes: List[tuple[int, bytes]]):
    reader = MemoryReader(client._pymem)
    for address, oldbytes in address_bytes:
        await reader.write_bytes(address, oldbytes)

async def main():
    handler = ClientHandler()
    client = handler.get_new_clients()[0]
    address_bytes = []
    enabled = False

    print("Type \"e\" to enable, \"d\" to disable, or \"exit\" to exit.")

    try:
        while True:
            inp = input("> ")
            inp = inp.lower()
            if inp == "e" or inp == "enable":
                if enabled:
                    print("The patch is already enabled.")
                else:
                    print("Preparing")
                    try:
                        address_bytes = await patch(client)
                        print("Patch Enabled.")
                        enabled = True
                    except PatternFailed as e:
                        logger.critical(f"{e}")
            elif inp == "d" or inp == "disable":
                if not enabled:
                    print("The patch is already disabled.")
                else:
                    if address_bytes:
                        await reset_patch(client, address_bytes)
                        enabled = False
                        address_bytes = []
                        print("Patch Disabled.")
                    else:
                        break
            elif inp == "exit" or inp == "quit":
                break
    finally:
        if address_bytes:
            await reset_patch(client, address_bytes)
        print("Closing")
        await handler.close()


if __name__ == "__main__":
    asyncio.run(main())
