"""
Base Agent class for all customer support agents.

This module provides the foundational BaseAgent class that all specialized
agents inherit from, following Google ADK patterns.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

import google.generativeai as genai
from loguru import logger

from utils.config import Config
from utils.logger import LoggerMixin


@dataclass
class AgentResponse:
    """
    Response object for agent interactions following ADK patterns.

    This dataclass provides a standardized response format for all agents,
    ensuring consistency across the multi-agent system.
    """

    response: str
    confidence: float
    agent_type: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseAgent(ABC, LoggerMixin):
    """
    Base Agent class following Google ADK patterns.

    This abstract base class provides the foundation for all specialized
    agents in the customer support system, implementing common functionality
    and following Google Agent Development Kit (ADK) architecture patterns.

    ADK Architecture Decision: Base Agent Pattern
    - Provides common interface for all agents
    - Implements shared functionality (AI model, logging, etc.)
    - Defines abstract methods for specialized behavior
    - Follows Google ADK patterns for agent development
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
        self.conversation_history = []

        # Initialize AI model
        self._initialize_ai_model()

        self.log_info(f"Base Agent '{agent_type}' initialized")

    def _initialize_ai_model(self):
        """Initialize the AI model for this agent."""
        try:
            genai.configure(api_key=self.config.google_api_key)
            self.model = genai.GenerativeModel(
                model_name=self.config.agent_model,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 1024,
                },
            )
            self.log_info(f"AI model '{self.config.agent_model}' initialized")
        except Exception as e:
            self.log_error(f"Failed to initialize AI model: {e}")
            raise

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.

        Returns:
            str: System prompt defining the agent's role and capabilities
        """
        pass

    @abstractmethod
    def can_handle_query(self, query: str) -> float:
        """
        Determine if this agent can handle the given query.

        Args:
            query (str): The customer query to evaluate

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        pass

    @abstractmethod
    async def process_query(self, query: str, user_id: str = None) -> AgentResponse:
        """
        Process a customer query.

        Args:
            query (str): The customer query to process
            user_id (str): Optional user identifier for session tracking

        Returns:
            AgentResponse: The agent's response with metadata
        """
        pass

    def _update_conversation_history(
        self, query: str, response: str, user_id: str = None
    ):
        """
        Update conversation history for context.

        Args:
            query (str): Customer query
            response (str): Agent response
            user_id (str): User identifier
        """
        self.conversation_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "query": query,
                "response": response,
                "agent_type": self.agent_type,
            }
        )

        # Keep only last 10 conversations for memory management
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]

    async def _get_ai_response(self, prompt: str) -> str:
        """
        Get response from AI model.

        Args:
            prompt (str): Prompt to send to AI model

        Returns:
            str: AI model response
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            self.log_error(f"Error generating AI response: {e}")
            raise

    def get_capabilities(self) -> list:
        """
        Get list of agent capabilities.

        Returns:
            list: List of capability strings
        """
        return ["query_processing", "ai_response", "conversation_management"]

    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get agent information.

        Returns:
            Dict[str, Any]: Agent information
        """
        return {
            "agent_type": self.agent_type,
            "capabilities": self.get_capabilities(),
            "conversation_history_length": len(self.conversation_history),
            "ai_model": self.config.agent_model,
        }
