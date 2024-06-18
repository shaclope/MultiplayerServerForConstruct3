import asyncio
import websockets
import json

connected_clients = {}
positions = {}

async def handler(websocket, path):
    client_id = id(websocket)
    connected_clients[client_id] = websocket
    positions[client_id] = {"x": 0, "y": 0}
    print(f"Client {client_id} connected")
    
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "update_position":
                positions[client_id] = data["position"]
                await broadcast_positions()
    except websockets.ConnectionClosed:
        print(f"Client {client_id} disconnected")
    finally:
        del connected_clients[client_id]
        del positions[client_id]
        await broadcast_positions()

async def broadcast_positions():
    if connected_clients:
        message = json.dumps({"type": "positions", "positions": positions})
        await asyncio.gather(*[client.send(message) for client in connected_clients.values()])

async def main():
    print("Server starting...")
    async with websockets.serve(handler, "0.0.0.0", 5000):
        print("Server started")
        await asyncio.Future()

if __name__ == "__main__":
    print("Running main...")
    asyncio.run(main())
