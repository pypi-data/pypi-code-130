import asyncio
import struct


async def handle_echo(reader, writer):
    data = struct.pack(">H", 5)
    writer.write(data)
    print("Sending")
    await writer.drain()


async def main():
    server = await asyncio.start_server(handle_echo, "0.0.0.0", 8888)

    addr = server.sockets[0].getsockname()
    print(f"Serving on {addr}")

    async with server:
        await server.serve_forever()


asyncio.run(main())
