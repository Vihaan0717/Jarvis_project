import asyncio
import websockets
import json

async def simulate_ui():
    uri = "ws://127.0.0.1:8765"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected! Waiting for INIT_DATA...")
            
            # 1. Check Init Data
            init_msg = await websocket.recv()
            print(f"RECEIVED INIT_DATA: {json.loads(init_msg).keys()}")
            
            # 2. Test Project Command
            print("\nTesting 'create_project' command...")
            cmd = {
                "type": "PROJECT_COMMAND",
                "action": "create_project",
                "parameters": {"name": "TestUIProject"}
            }
            await websocket.send(json.dumps(cmd))
            res = await websocket.recv()
            print(f"RESULT: {res}")
            
            # 3. Test Code Gen
            print("\nTesting 'GET_CODE_GEN' command...")
            gen = {
                "type": "GET_CODE_GEN",
                "prompt": "Write a hello world in python"
            }
            await websocket.send(json.dumps(gen))
            # Wait for code result
            code_res = await websocket.recv()
            print(f"AI CODE RECEIVED: {code_res[:100]}...")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(simulate_ui())
