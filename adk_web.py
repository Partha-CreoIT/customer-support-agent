#!/usr/bin/env python3
"""
ADK Web Command for the Customer Support Agent System.

This script provides ADK-compliant web interface for the customer support
agent system, following Google Agent Development Kit patterns.

Usage: python adk_web.py [options]
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from loguru import logger

from websocket_server.server import WebSocketServer
from agents.agent_manager import AgentManager
from utils.config import Config
from utils.logger import setup_logging


class ADKWebCommand:
    """
    ADK Web Command for running the customer support agent system.

    This class provides ADK-compliant web interface following Google
    Agent Development Kit patterns and best practices.
    """

    def __init__(self):
        """Initialize the ADK web command."""
        self.config = None
        self.agent_manager = None
        self.websocket_server = None

    async def setup(self):
        """Setup the ADK web system."""
        try:
            # Load environment variables
            load_dotenv("config.env")

            # Setup logging
            setup_logging()
            logger.info("Starting ADK Web Command for Customer Support Agent System")

            # Initialize configuration
            self.config = Config()
            logger.info(
                f"ADK Configuration loaded: WebSocket server on {self.config.websocket_host}:{self.config.websocket_port}"
            )

            # Initialize agent manager with ADK patterns
            self.agent_manager = AgentManager(self.config)
            await self.agent_manager.initialize()
            logger.info("ADK Agent Manager initialized successfully")

            # Create WebSocket server
            self.websocket_server = WebSocketServer(self.config, self.agent_manager)
            logger.info("ADK WebSocket server created")

        except Exception as e:
            logger.error(f"Failed to setup ADK web system: {e}")
            raise

    async def start(self):
        """Start the ADK web system."""
        try:
            logger.info("Starting ADK Web System...")
            await self.websocket_server.start()
        except KeyboardInterrupt:
            logger.info("Received shutdown signal, stopping ADK web system...")
        except Exception as e:
            logger.error(f"Error in ADK web system: {e}")
            raise
        finally:
            try:
                await self.cleanup()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")

    async def cleanup(self):
        """Cleanup ADK web system resources."""
        try:
            if self.websocket_server:
                logger.info("Stopping WebSocket server...")
                await self.websocket_server.stop()
                logger.info("WebSocket server stopped successfully")
            logger.info("ADK Web System cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            # Don't raise the exception to avoid masking the original error

    def get_adk_info(self):
        """Get ADK-specific information."""
        if not self.agent_manager:
            return {"error": "Agent manager not initialized"}

        return self.agent_manager.get_adk_info()

    def get_system_status(self):
        """Get system status with ADK metadata."""
        if not self.agent_manager:
            return {"error": "Agent manager not initialized"}

        return self.agent_manager.get_system_stats()


async def main():
    """Main function for ADK web command."""
    parser = argparse.ArgumentParser(
        description="ADK Web Command for Customer Support Agent System"
    )
    parser.add_argument("--info", action="store_true", help="Show ADK information")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--start", action="store_true", help="Start the ADK web system")

    args = parser.parse_args()

    adk_web = ADKWebCommand()

    try:
        await adk_web.setup()

        if args.info:
            info = adk_web.get_adk_info()
            print("🤖 ADK Information:")
            print(
                f"   Root Agent: {info.get('root_agent', {}).get('agent_type', 'Unknown')}"
            )
            print(f"   Sub Agents: {', '.join(info.get('sub_agents', []))}")
            print(f"   Conversation States: {info.get('conversation_states', 0)}")
            print(f"   Architecture: ADK Root Agent Pattern")
            return

        if args.status:
            status = adk_web.get_system_status()
            print("📊 ADK System Status:")
            print(f"   Total Conversations: {status.get('total_conversations', 0)}")
            print(f"   Active Sessions: {status.get('active_sessions', 0)}")
            print(f"   Agents Count: {status.get('agents_count', 0)}")
            print(f"   Architecture: {status.get('architecture', 'Unknown')}")
            return

        if args.start or not any([args.info, args.status]):
            print("🚀 Starting ADK Web System...")
            print("   WebSocket URL: ws://localhost:8765")
            print("   Architecture: ADK Root Agent Pattern")
            print("   Press Ctrl+C to stop")
            print()
            try:
                await adk_web.start()
            except KeyboardInterrupt:
                print("\n👋 Shutting down gracefully...")
                sys.exit(0)
            except Exception as e:
                logger.error(f"ADK Web Command failed: {e}")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"ADK Web Command failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
