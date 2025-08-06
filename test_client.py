#!/usr/bin/env python3
"""
Test client for the AI Customer Support WebSocket server.

This script provides a simple command-line interface to test the WebSocket
server and interact with the AI agents.
"""

import asyncio
import json
import websockets
from datetime import datetime


async def test_websocket_client():
    """
    Test client for the WebSocket server.

    This function connects to the WebSocket server and provides an interactive
    interface for testing the AI customer support agents.
    """
    uri = "ws://localhost:8765"

    try:
        print("Connecting to AI Customer Support WebSocket server...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to server!")

            # Listen for messages from server
            async def listen_for_messages():
                try:
                    async for message in websocket:
                        data = json.loads(message)
                        print(
                            f"\n🤖 Server: {data.get('message', data.get('content', 'No content'))}"
                        )
                        if data.get("agent_type"):
                            print(f"   Agent: {data['agent_type']}")
                        if data.get("confidence"):
                            print(f"   Confidence: {data['confidence']:.2f}")
                        print("> ", end="", flush=True)
                except Exception as e:
                    print(f"Error receiving message: {e}")

            # Start listening for messages
            listener_task = asyncio.create_task(listen_for_messages())

            # Interactive input loop
            print("\n💬 Start chatting with the AI agents! (Type 'quit' to exit)")
            print("> ", end="", flush=True)

            while True:
                try:
                    # Get user input
                    user_input = await asyncio.get_event_loop().run_in_executor(
                        None, input
                    )

                    if user_input.lower() in ["quit", "exit", "bye"]:
                        print("👋 Goodbye!")
                        break

                    if not user_input.strip():
                        print("> ", end="", flush=True)
                        continue

                    # Send message to server
                    message = {
                        "type": "message",
                        "content": user_input,
                        "timestamp": datetime.now().isoformat(),
                    }

                    await websocket.send(json.dumps(message))

                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"Error sending message: {e}")
                    print("> ", end="", flush=True)

            # Cancel the listener task
            listener_task.cancel()

            except websockets.exceptions.ConnectionClosed:
        print(
            "❌ Could not connect to server. Make sure the server is running on localhost:8765"
        )
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_status_requests():
    """
    Test status requests to the WebSocket server.

    This function demonstrates how to request system and agent status
    information from the server.
    """
    uri = "ws://localhost:8765"

    try:
        async with websockets.connect(uri) as websocket:
            print("Testing status requests...")

            # Test system status
            system_status_request = {"type": "status", "status_type": "system"}

            await websocket.send(json.dumps(system_status_request))
            response = await websocket.recv()
            data = json.loads(response)

            print(f"System Status: {json.dumps(data, indent=2)}")

            # Test agent status
            agent_status_request = {"type": "status", "status_type": "agents"}

            await websocket.send(json.dumps(agent_status_request))
            response = await websocket.recv()
            data = json.loads(response)

            print(f"Agent Status: {json.dumps(data, indent=2)}")

    except Exception as e:
        print(f"Error testing status requests: {e}")


def main():
    """Main function to run the test client."""
    print("🤖 AI Customer Support Test Client")
    print("=" * 40)

    # Ask user what they want to test
    print("Choose an option:")
    print("1. Interactive chat with AI agents")
    print("2. Test status requests")
    print("3. Both")

    choice = input("Enter your choice (1-3): ").strip()

    if choice == "1":
        asyncio.run(test_websocket_client())
    elif choice == "2":
        asyncio.run(test_status_requests())
    elif choice == "3":
        asyncio.run(test_websocket_client())
        print("\n" + "=" * 40)
        asyncio.run(test_status_requests())
    else:
        print("Invalid choice. Running interactive chat...")
        asyncio.run(test_websocket_client())


if __name__ == "__main__":
    main()
