#!/usr/bin/env python3
"""
Demo script for the AI Customer Support Agent System.

This script demonstrates the capabilities of different agents by running
predefined test scenarios and showing how the system routes queries.
"""

import asyncio
import json
import websockets
from datetime import datetime


class CustomerSupportDemo:
    """
    Demo class for showcasing the AI Customer Support Agent System.

    This class provides predefined test scenarios to demonstrate
    the capabilities of different agents and the routing system.
    """

    def __init__(self, websocket_url: str = "ws://localhost:8765"):
        """
        Initialize the demo.

        Args:
            websocket_url (str): WebSocket server URL
        """
        self.websocket_url = websocket_url
        self.test_scenarios = [
            {
                "name": "General Inquiry",
                "query": "What are your business hours?",
                "expected_agent": "general_support",
                "description": "Tests general support agent for basic company information",
            },
            {
                "name": "Technical Issue",
                "query": "My software keeps crashing with error code 0x80070057. Can you help me fix this?",
                "expected_agent": "technical_support",
                "description": "Tests technical support agent for software troubleshooting",
            },
            {
                "name": "Billing Question",
                "query": "I was charged twice for my subscription this month. I need a refund.",
                "expected_agent": "billing_support",
                "description": "Tests billing support agent for payment and refund issues",
            },
            {
                "name": "Escalation Request",
                "query": "I've been trying to resolve this issue for 3 days and I'm still not satisfied. I need to speak to a human supervisor immediately.",
                "expected_agent": "escalation",
                "description": "Tests escalation agent for complex cases requiring human intervention",
            },
            {
                "name": "Mixed Technical Issue",
                "query": "My payment failed when trying to upgrade my subscription, and now the software won't work properly.",
                "expected_agent": "technical_support",  # Technical issues often take priority
                "description": "Tests agent routing when query contains multiple domain keywords",
            },
        ]

    async def run_demo(self):
        """
        Run the complete demo showcasing all agents.
        """
        print("🤖 AI Customer Support Agent System Demo")
        print("=" * 50)

        try:
            async with websockets.connect(self.websocket_url) as websocket:
                print("✅ Connected to WebSocket server")
                print()

                # Run each test scenario
                for i, scenario in enumerate(self.test_scenarios, 1):
                    await self._run_scenario(websocket, scenario, i)
                    print("-" * 50)

                # Show system statistics
                await self._show_system_stats(websocket)

        except websockets.exceptions.ConnectionRefused:
            print("❌ Could not connect to server. Make sure the server is running:")
            print("   python main.py")
        except Exception as e:
            print(f"❌ Error during demo: {e}")

    async def _run_scenario(self, websocket, scenario: dict, scenario_num: int):
        """
        Run a single test scenario.

        Args:
            websocket: WebSocket connection
            scenario (dict): Test scenario data
            scenario_num (int): Scenario number
        """
        print(f"📋 Scenario {scenario_num}: {scenario['name']}")
        print(f"📝 Description: {scenario['description']}")
        print(f"💬 Query: \"{scenario['query']}\"")
        print(f"🎯 Expected Agent: {scenario['expected_agent']}")
        print()

        # Send the query
        message = {
            "type": "message",
            "content": scenario["query"],
            "timestamp": datetime.now().isoformat(),
        }

        await websocket.send(json.dumps(message))

        # Get response
        response = await websocket.recv()
        data = json.loads(response)

        # Display results
        print("🤖 Response:")
        print(f"   Agent: {data.get('agent_type', 'Unknown')}")
        print(f"   Confidence: {data.get('confidence', 0):.2f}")
        print(f"   Response: {data.get('content', 'No response')}")

        # Check if routing was correct
        actual_agent = data.get("agent_type", "unknown")
        expected_agent = scenario["expected_agent"]

        if actual_agent == expected_agent:
            print("✅ Routing: CORRECT")
        else:
            print(
                f"⚠️  Routing: INCORRECT (Expected: {expected_agent}, Got: {actual_agent})"
            )

        print()

    async def _show_system_stats(self, websocket):
        """
        Show system statistics.

        Args:
            websocket: WebSocket connection
        """
        print("📊 System Statistics")
        print("=" * 30)

        # Get system status
        system_request = {"type": "status", "status_type": "system"}

        await websocket.send(json.dumps(system_request))
        response = await websocket.recv()
        system_data = json.loads(response)

        if system_data.get("type") == "status":
            stats = system_data.get("data", {})
            print(f"Total Conversations: {stats.get('total_conversations', 0)}")
            print(f"Active Sessions: {stats.get('active_sessions', 0)}")
            print(f"Agents Count: {stats.get('agents_count', 0)}")
            print(f"Agent Types: {', '.join(stats.get('agent_types', []))}")

        # Get agent status
        agent_request = {"type": "status", "status_type": "agents"}

        await websocket.send(json.dumps(agent_request))
        response = await websocket.recv()
        agent_data = json.loads(response)

        if agent_data.get("type") == "status":
            agents = agent_data.get("data", {})
            print("\nAgent Activity:")
            for agent_type, agent_info in agents.items():
                status = "🟢 Active" if agent_info.get("active") else "🔴 Inactive"
                conversations = agent_info.get("conversation_count", 0)
                print(f"   {agent_type}: {status} ({conversations} conversations)")

        print()


async def interactive_demo():
    """
    Interactive demo allowing user to test custom queries.
    """
    print("🎮 Interactive Demo Mode")
    print("=" * 30)
    print("Type your own queries to test the AI agents!")
    print("Type 'quit' to exit")
    print()

    try:
        async with websockets.connect("ws://localhost:8765") as websocket:
            print("✅ Connected to server")
            print("💬 Start chatting:")
            print()

            while True:
                # Get user input
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, "You: "
                )

                if user_input.lower() in ["quit", "exit", "bye"]:
                    print("👋 Goodbye!")
                    break

                if not user_input.strip():
                    continue

                # Send message
                message = {
                    "type": "message",
                    "content": user_input,
                    "timestamp": datetime.now().isoformat(),
                }

                await websocket.send(json.dumps(message))

                # Get response
                response = await websocket.recv()
                data = json.loads(response)

                # Display response
                print(
                    f"🤖 {data.get('agent_type', 'Agent')}: {data.get('content', 'No response')}"
                )
                if data.get("confidence"):
                    print(f"   Confidence: {data['confidence']:.2f}")
                print()

    except websockets.exceptions.ConnectionRefused:
        print("❌ Could not connect to server. Make sure the server is running:")
        print("   python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """
    Main function to run the demo.
    """
    print("🎯 AI Customer Support Agent Demo")
    print("=" * 40)
    print("Choose demo mode:")
    print("1. Automated test scenarios")
    print("2. Interactive mode")
    print("3. Both")

    choice = input("Enter your choice (1-3): ").strip()

    demo = CustomerSupportDemo()

    if choice == "1":
        asyncio.run(demo.run_demo())
    elif choice == "2":
        asyncio.run(interactive_demo())
    elif choice == "3":
        asyncio.run(demo.run_demo())
        print("\n" + "=" * 50)
        asyncio.run(interactive_demo())
    else:
        print("Invalid choice. Running automated demo...")
        asyncio.run(demo.run_demo())


if __name__ == "__main__":
    main()
