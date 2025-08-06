"""
WebSocket Server for real-time customer support communication.

This module implements a WebSocket server that enables real-time communication
between customers and the AI support agents, handling message routing and
session management.
"""

import asyncio
import json
import uuid
from typing import Dict, Set, Optional, Any
from datetime import datetime

import websockets
from websockets.server import WebSocketServerProtocol
from loguru import logger

from utils.config import Config
from utils.logger import LoggerMixin
from agents.agent_manager import AgentManager


class WebSocketServer(LoggerMixin):
    """
    WebSocket Server for real-time customer support communication.

    This class implements a WebSocket server that:
    1. Handles real-time communication with customers
    2. Routes messages to appropriate AI agents
    3. Manages user sessions and connections
    4. Provides status and monitoring capabilities
    5. Handles connection lifecycle events

    Architecture Decision: WebSocket for Real-time Communication
    - Enables instant message exchange
    - Supports multiple concurrent connections
    - Maintains persistent connections for better UX
    - Allows for real-time status updates
    - Scales well for customer support scenarios
    """

    def __init__(self, config: Config, agent_manager: AgentManager):
        """
        Initialize the WebSocket server.

        Args:
            config (Config): Application configuration
            agent_manager (AgentManager): Agent manager instance
        """
        super().__init__()
        self.config = config
        self.agent_manager = agent_manager
        self.clients: Dict[str, WebSocketServerProtocol] = {}
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
        self.server = None

        self.log_info("WebSocket Server initialized")

    async def start(self):
        """
        Start the WebSocket server.

        This method starts the WebSocket server and begins listening for
        incoming connections on the configured host and port.
        """
        try:
            # Start the WebSocket server
            self.server = await websockets.serve(
                self._handle_client,
                self.config.websocket_host,
                self.config.websocket_port,
            )

            self.log_info(
                f"WebSocket server started on ws://{self.config.websocket_host}:{self.config.websocket_port}"
            )

            # Keep the server running
            await self.server.wait_closed()

        except Exception as e:
            self.log_error(f"Failed to start WebSocket server: {e}")
            raise

    async def _handle_client(self, websocket: WebSocketServerProtocol):
        """
        Handle a new WebSocket client connection.

        This method manages the lifecycle of a client connection, including
        connection setup, message processing, and cleanup.

        Args:
            websocket (WebSocketServerProtocol): The WebSocket connection
        """
        client_id = str(uuid.uuid4())
        user_id = None

        try:
            # Store client connection
            self.clients[client_id] = websocket
            self.log_info(f"New client connected: {client_id}")

            # Send welcome message
            welcome_message = {
                "type": "connection",
                "status": "connected",
                "client_id": client_id,
                "timestamp": datetime.now().isoformat(),
                "message": "Welcome to our AI Customer Support! How can I help you today?",
            }

            await websocket.send(json.dumps(welcome_message))

            # Handle incoming messages
            async for message in websocket:
                try:
                    # Parse the message
                    data = json.loads(message)
                    response = await self._process_message(data, client_id)

                    # Send response back to client
                    await websocket.send(json.dumps(response))

                except json.JSONDecodeError:
                    # Handle non-JSON messages as plain text
                    text_message = {
                        "type": "message",
                        "content": message,
                        "timestamp": datetime.now().isoformat(),
                    }
                    response = await self._process_message(text_message, client_id)
                    await websocket.send(json.dumps(response))

                except Exception as e:
                    self.log_error(f"Error processing message: {e}")
                    error_response = {
                        "type": "error",
                        "message": "An error occurred while processing your message. Please try again.",
                        "timestamp": datetime.now().isoformat(),
                    }
                    await websocket.send(json.dumps(error_response))

        except websockets.exceptions.ConnectionClosed:
            self.log_info(f"Client disconnected: {client_id}")

        except Exception as e:
            self.log_error(f"Error handling client {client_id}: {e}")

        finally:
            # Clean up client connection
            await self._cleanup_client(client_id, user_id)

    async def _process_message(
        self, data: Dict[str, Any], client_id: str
    ) -> Dict[str, Any]:
        """
        Process an incoming message from a client.

        This method routes the message to the appropriate agent and returns
        the response with metadata.

        Args:
            data (Dict[str, Any]): The incoming message data
            client_id (str): The client identifier

        Returns:
            Dict[str, Any]: The response to send back to the client
        """
        try:
            message_type = data.get("type", "message")

            if message_type == "message":
                return await self._handle_chat_message(data, client_id)
            elif message_type == "status":
                return await self._handle_status_request(data, client_id)
            elif message_type == "session":
                return await self._handle_session_request(data, client_id)
            else:
                return {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}",
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            self.log_error(f"Error processing message: {e}")
            return {
                "type": "error",
                "message": "An error occurred while processing your request.",
                "timestamp": datetime.now().isoformat(),
            }

    async def _handle_chat_message(
        self, data: Dict[str, Any], client_id: str
    ) -> Dict[str, Any]:
        """
        Handle a chat message from a client.

        Args:
            data (Dict[str, Any]): The message data
            client_id (str): The client identifier

        Returns:
            Dict[str, Any]: The agent's response
        """
        content = data.get("content", "")
        user_id = data.get("user_id", client_id)

        if not content.strip():
            return {
                "type": "error",
                "message": "Message cannot be empty.",
                "timestamp": datetime.now().isoformat(),
            }

        # Process the message with the agent manager
        agent_response = await self.agent_manager.process_query(content, user_id)

        # Update user session
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "client_id": client_id,
                "created_at": datetime.now(),
                "message_count": 0,
            }

        self.user_sessions[user_id]["message_count"] += 1
        self.user_sessions[user_id]["last_activity"] = datetime.now()

        # Format the response
        response = {
            "type": "message",
            "content": agent_response.response,
            "agent_type": agent_response.agent_type,
            "confidence": agent_response.confidence,
            "timestamp": datetime.now().isoformat(),
            "metadata": agent_response.metadata,
        }

        self.log_info(
            f"Processed message for user {user_id} with {agent_response.agent_type} agent"
        )
        return response

    async def _handle_status_request(
        self, data: Dict[str, Any], client_id: str
    ) -> Dict[str, Any]:
        """
        Handle a status request from a client.

        Args:
            data (Dict[str, Any]): The status request data
            client_id (str): The client identifier

        Returns:
            Dict[str, Any]: Status information
        """
        status_type = data.get("status_type", "system")

        if status_type == "system":
            stats = self.agent_manager.get_system_stats()
            return {
                "type": "status",
                "status_type": "system",
                "data": stats,
                "timestamp": datetime.now().isoformat(),
            }
        elif status_type == "agents":
            agent_status = self.agent_manager.get_agent_status()
            return {
                "type": "status",
                "status_type": "agents",
                "data": agent_status,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {
                "type": "error",
                "message": f"Unknown status type: {status_type}",
                "timestamp": datetime.now().isoformat(),
            }

    async def _handle_session_request(
        self, data: Dict[str, Any], client_id: str
    ) -> Dict[str, Any]:
        """
        Handle a session request from a client.

        Args:
            data (Dict[str, Any]): The session request data
            client_id (str): The client identifier

        Returns:
            Dict[str, Any]: Session information
        """
        action = data.get("action", "get")
        user_id = data.get("user_id", client_id)

        if action == "get":
            session_info = self.agent_manager.get_session_info(user_id)
            return {
                "type": "session",
                "action": "get",
                "data": session_info,
                "timestamp": datetime.now().isoformat(),
            }
        elif action == "clear":
            self.agent_manager.clear_user_session(user_id)
            return {
                "type": "session",
                "action": "clear",
                "message": "Session cleared successfully",
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {
                "type": "error",
                "message": f"Unknown session action: {action}",
                "timestamp": datetime.now().isoformat(),
            }

    async def _cleanup_client(self, client_id: str, user_id: str):
        """
        Clean up when a client disconnects.

        Args:
            client_id (str): The client identifier
            user_id (str): The user identifier
        """
        # Remove client from active connections
        if client_id in self.clients:
            del self.clients[client_id]

        # Update user session
        if user_id in self.user_sessions:
            self.user_sessions[user_id]["disconnected_at"] = datetime.now()

        self.log_info(f"Cleaned up client: {client_id}")

    def get_server_stats(self) -> Dict[str, Any]:
        """
        Get server statistics.

        Returns:
            Dict[str, Any]: Server statistics
        """
        return {
            "active_connections": len(self.clients),
            "active_sessions": len(self.user_sessions),
            "server_status": "running" if self.server else "stopped",
            "host": self.config.websocket_host,
            "port": self.config.websocket_port,
        }

    async def broadcast_message(self, message: Dict[str, Any]):
        """
        Broadcast a message to all connected clients.

        Args:
            message (Dict[str, Any]): The message to broadcast
        """
        if not self.clients:
            return

        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()

        # Convert to JSON
        message_json = json.dumps(message)

        # Send to all clients
        disconnected_clients = []
        for client_id, websocket in self.clients.items():
            try:
                await websocket.send(message_json)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(client_id)
            except Exception as e:
                self.log_error(f"Error broadcasting to client {client_id}: {e}")
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            if client_id in self.clients:
                del self.clients[client_id]

        self.log_info(f"Broadcasted message to {len(self.clients)} clients")

    async def stop(self):
        """
        Stop the WebSocket server.

        This method gracefully shuts down the server and closes all
        client connections.
        """
        try:
            # Close all client connections
            for client_id, websocket in self.clients.items():
                try:
                    await websocket.close()
                except Exception as e:
                    self.log_error(f"Error closing client {client_id}: {e}")

            # Clear client list
            self.clients.clear()

            # Stop the server
            if self.server:
                self.server.close()
                await self.server.wait_closed()

            self.log_info("WebSocket server stopped")

        except Exception as e:
            self.log_error(f"Error stopping WebSocket server: {e}")
            raise
