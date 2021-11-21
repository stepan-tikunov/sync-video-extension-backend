import asyncio, signal, websockets, json

clients = {}

async def update_room_size(uri):
    room_size = {
        "type": "update_room_size",
        "roomSize": len(clients[uri])
    }

    message = json.dumps(room_size, ensure_ascii=False)

    await broadcast(uri, message)

async def connect(client, uri):
    if uri in clients:
        clients[uri].append(client)
    else:
        clients[uri] = [client]

    await update_room_size(uri)
        
async def disconnect(client, uri):
    clients[uri].remove(client)

    await update_room_size(uri)

async def broadcast(uri, message):
    try:
        for client in clients[uri]:
            await client.send(message)
    except:
        await disconnect(client, uri)

async def handler(client, uri):
    await connect(client, uri)
    try:
        async for message in client:
            try:
                data = json.loads(message)
                bad_message = any("type" not in data,
                                  "videoId" not in data,
                                  "time": not in data,
                                  data["type"] not in ("pause", "play"))
                try:
                    int(data["videoId"])
                    videoIdIsNotInt = False
                except:
                    videoIdIsNotInt = True

                try:
                    float(data["time"])
                    timeIsNotFloat = False
                except:
                    timeIsNotFloat = False

                bad_message = any(bad_message, videoIdIsNotInt, timeIsNotFloat)
                if bad_message:
                    pass
                else:
                    data = {
                        "type": data["type"],
                        "videoId": data["videoId"],
                        "time": data["time"]
                    }
                    message = json.dumps(data, ensure_ascii=False)
                    await broadcast(uri, message)
            except:
                pass
    except:
        pass
    await disconnect(client, uri)

async def main(stop):
    async with websockets.serve(handler, "0.0.0.0", 8080):
        await stop

loop = asyncio.get_event_loop()

stop = loop.create_future()
loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

loop.run_until_complete(main(stop))
