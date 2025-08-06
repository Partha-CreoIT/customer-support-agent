#!/usr/bin/env python3
"""
Main entry point for the Google-style AI Customer Support Agent System.

This module initializes and runs the WebSocket server that connects AI agents
for real-time customer support interactions.

Architecture Decision: Multi-Agent System
- General Support Agent: Handles general queries and routing
- Technical Support Agent: Specialized in technical issues
- Billing Support Agent: Handles payment and billing queries
- Escalation Agent: Manages complex cases and human handoffs

This multi-agent approach allows for:
1. Specialized expertise in different domains
2. Better scalability and maintainability
3. Improved response quality through domain-specific knowledge
4. Easier testing and debugging of individual components
"""

import asyncio
import logging
import os
import sys
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


async def main():
    """
    Main function that initializes and runs the customer support agent system.

    This function:
    1. Loads environment configuration
    2. Sets up logging
    3. Initializes the agent manager
    4. Starts the WebSocket server
    5. Handles graceful shutdown
    """
    try:
        # Load environment variables
        load_dotenv("config.env")

        # Setup logging
        setup_logging()
        logger.info("Starting Google-style AI Customer Support Agent System")

        # Initialize configuration
        config = Config()
        logger.info(
            f"Configuration loaded: WebSocket server on {config.websocket_host}:{config.websocket_port}"
        )

        # Initialize agent manager
        agent_manager = AgentManager(config)
        await agent_manager.initialize()
        logger.info("Agent manager initialized successfully")

        # Create and start WebSocket server
        server = WebSocketServer(config, agent_manager)
        logger.info("WebSocket server created, starting...")

        # Start the server
        await server.start()

    except KeyboardInterrupt:
        logger.info("Received shutdown signal, stopping server...")
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)
    finally:
        logger.info("Customer support agent system shutdown complete")


if __name__ == "__main__":
    # Run the main async function
    asyncio.run(main())
