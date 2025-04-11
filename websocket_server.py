import asyncio
import websockets
import json
import sys
from datetime import datetime

class WebSocketManager:
    def __init__(self):
        self.clients = set()

    async def handle_client(self, websocket):
        """处理单个WebSocket客户端连接"""
        self.clients.add(websocket)
        client_ip = websocket.remote_address[0]
        print(f"New client connected: {client_ip}")
        
        try:
            # 发送欢迎消息
            welcome_msg = {
                "type": "system",
                "content": "WebSocket连接已建立",
                "timestamp": int(datetime.now().timestamp() * 1000)
            }
            await websocket.send(json.dumps(welcome_msg))
            
            # 监听客户端消息
            async for message in websocket:
                await self.process_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            print(f"Client disconnected: {client_ip}")
        finally:
            self.clients.remove(websocket)
    
    async def process_message(self, websocket, message):
        """处理来自客户端的消息"""
        try:
            data = json.loads(message)
            print(f"Received message: {data}")
            
            # 简单回显消息
            response = {
                "type": "echo",
                "content": f"Echo: {data['content']}",
                "timestamp": int(datetime.now().timestamp() * 1000)
            }
            await websocket.send(json.dumps(response))
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Invalid JSON format",
                "timestamp": int(datetime.now().timestamp() * 1000)
            }))

async def start_server():
    manager = WebSocketManager()
    
    # Windows-specific event loop policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Create server with Windows-compatible configuration
    async with websockets.serve(
        manager.handle_client,
        "0.0.0.0",
        8765,
        reuse_address=True,  # Windows-compatible alternative to reuse_port
        ping_interval=20,
        ping_timeout=20,
        max_size=2**25,
        compression=None,
        origins=None #["http://localhost", "http://127.0.0.1"]
    ) as server:
        print(f"WebSocket server started on ws://{server.sockets[0].getsockname()[0]}:{server.sockets[0].getsockname()[1]}")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(start_server())
    
    #{server.sockets[0].getsockname()[0]}:{server.sockets[0].getsockname()[1]}