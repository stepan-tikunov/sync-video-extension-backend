import asyncio, signal, websockets

clients = {}

async def connect(client, uri):
    if uri in clients:
        clients[uri].append(client)
    else:
        clients[uri] = [client]

async def disconnect(client, uri):
    clients[uri].remove(client)

async def broadcast(uri, message):
    for client in clients[uri]:
        await client.send(message)

async def handler(client, uri):
    await connect(client, uri)
    async for message in client:
        print(uri, message)
        await broadcast(uri, message)
    await disconnect(client, uri)

async def main(stop):
    async with websockets.serve(handler, "0.0.0.0", 8080):
        await stop

loop = asyncio.get_event_loop()

stop = loop.create_future()
loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
        
loop.run_until_complete(main(stop))
