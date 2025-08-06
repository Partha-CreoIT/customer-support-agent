"""
Base agent class for the customer support system.

This module defines the abstract base class that all specialized agents
inherit from, providing common functionality and interface definitions.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

import google.generativeai as genai
from loguru import logger

from utils.logger import LoggerMixin
from utils.config import Config


@dataclass
class AgentResponse:
    """
    Data class representing an agent's response to a customer query.

    This class encapsulates all the information about an agent's response,
    including the response text, confidence level, and metadata.
    """

    response: str
    confidence: float
    agent_type: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = {}


class BaseAgent(ABC, LoggerMixin):
    """
    Abstract base class for all customer support agents.

    This class provides the common interface and functionality that all
    specialized agents must implement. It handles Google AI integration,
    conversation management, and response formatting.

    Architecture Decision: Abstract Base Class Pattern
    - Provides consistent interface across all agents
    - Enables easy addition of new agent types
    - Centralizes common functionality (AI integration, logging, etc.)
    - Supports the multi-agent architecture effectively
    """

    def __init__(self, config: Config, agent_type: str):
        """
        Initialize the base agent.

        Args:
            config (Config): Application configuration
            agent_type (str): Type identifier for this agent
        """
        super().__init__()
        self.config = config
        self.agent_type = agent_type
        self.model = None
        self.conversation_history: List[Dict[str, str]] = []

        # Initialize Google AI
        self._initialize_google_ai()

        self.log_info(f"Initialized {agent_type} agent")

    def _initialize_google_ai(self):
        """
        Initialize Google Generative AI with the configured model.

        This method sets up the Google AI client with the specified model
        and configuration parameters.
        """
        try:
            # Configure Google AI
            genai.configure(api_key=self.config.google_api_key)

            # Initialize the model
            self.model = genai.GenerativeModel(
                model_name=self.config.agent_model,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                ),
            )

            self.log_info(
                f"Google AI initialized with model: {self.config.agent_model}"
            )

        except Exception as e:
            self.log_error(f"Failed to initialize Google AI: {e}")
            raise

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.

        This method must be implemented by each specialized agent to provide
        their specific system prompt that defines their role and capabilities.

        Returns:
            str: The system prompt for this agent
        """
        pass

    @abstractmethod
    def can_handle_query(self, query: str) -> float:
        """
        Determine if this agent can handle the given query.

        This method should return a confidence score (0.0 to 1.0) indicating
        how well this agent can handle the specific query.

        Args:
            query (str): The customer query to evaluate

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        pass

    async def process_query(self, query: str, user_id: str = None) -> AgentResponse:
        """
        Process a customer query and generate a response.

        This method handles the complete query processing pipeline:
        1. Validates the query
        2. Adds context from conversation history
        3. Generates response using Google AI
        4. Formats and returns the response

        Args:
            query (str): The customer query to process
            user_id (str): Optional user identifier for conversation tracking

        Returns:
            AgentResponse: The agent's response with metadata
        """
        try:
            # Validate query
            if not query or not query.strip():
                raise ValueError("Query cannot be empty")

            # Add to conversation history
            self.conversation_history.append(
                {
                    "role": "user",
                    "content": query,
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id,
                }
            )

            # Prepare conversation context
            conversation_context = self._prepare_conversation_context()

            # Generate response using Google AI
            response_text = await self._generate_response(query, conversation_context)

            # Add response to history
            self.conversation_history.append(
                {
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": datetime.now().isoformat(),
                    "agent_type": self.agent_type,
                }
            )

            # Create response object
            response = AgentResponse(
                response=response_text,
                confidence=self.can_handle_query(query),
                agent_type=self.agent_type,
                timestamp=datetime.now(),
                metadata={
                    "user_id": user_id,
                    "conversation_length": len(self.conversation_history),
                },
            )

            self.log_info(
                f"Processed query for user {user_id}, response length: {len(response_text)}"
            )
            return response

        except Exception as e:
            self.log_error(f"Error processing query: {e}")
            return AgentResponse(
                response="I apologize, but I encountered an error processing your request. Please try again.",
                confidence=0.0,
                agent_type=self.agent_type,
                timestamp=datetime.now(),
                metadata={"error": str(e)},
            )

    def _prepare_conversation_context(self) -> str:
        """
        Prepare conversation context from history.

        This method formats the conversation history into a context string
        that can be used by the AI model to maintain conversation continuity.

        Returns:
            str: Formatted conversation context
        """
        if not self.conversation_history:
            return ""

        # Take last 10 messages for context (to avoid token limits)
        recent_messages = self.conversation_history[-10:]

        context_parts = []
        for msg in recent_messages:
            role = msg["role"]
            content = msg["content"]
            context_parts.append(f"{role.title()}: {content}")

        return "\n".join(context_parts)

    async def _generate_response(self, query: str, context: str) -> str:
        """
        Generate response using Google AI.

        This method uses the Google Generative AI model to generate a response
        based on the query and conversation context.

        Args:
            query (str): The current query
            context (str): Conversation context

        Returns:
            str: Generated response text
        """
        try:
            # Prepare the full prompt
            system_prompt = self.get_system_prompt()

            if context:
                full_prompt = f"{system_prompt}\n\nConversation Context:\n{context}\n\nCurrent Query: {query}"
            else:
                full_prompt = f"{system_prompt}\n\nQuery: {query}"

            # Generate response
            response = await asyncio.to_thread(self.model.generate_content, full_prompt)

            return response.text

        except Exception as e:
            self.log_error(f"Error generating response with Google AI: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."

    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current conversation.

        Returns:
            Dict[str, Any]: Summary of conversation statistics
        """
        return {
            "agent_type": self.agent_type,
            "total_messages": len(self.conversation_history),
            "user_messages": len(
                [m for m in self.conversation_history if m["role"] == "user"]
            ),
            "assistant_messages": len(
                [m for m in self.conversation_history if m["role"] == "assistant"]
            ),
            "last_activity": (
                self.conversation_history[-1]["timestamp"]
                if self.conversation_history
                else None
            ),
        }

    def clear_conversation_history(self):
        """Clear the conversation history for this agent."""
        self.conversation_history.clear()
        self.log_info("Conversation history cleared")
