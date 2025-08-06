"""
Agent Manager for orchestrating all customer support agents.

This module manages the multi-agent architecture, handling routing decisions,
agent coordination, and ensuring optimal customer support delivery.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from agents.base_agent import BaseAgent, AgentResponse
from agents.root_agent import RootAgent
from agents.general_support_agent import GeneralSupportAgent
from agents.technical_support_agent import TechnicalSupportAgent
from agents.billing_support_agent import BillingSupportAgent
from agents.escalation_agent import EscalationAgent
from utils.config import Config
from utils.logger import LoggerMixin


class AgentManager(LoggerMixin):
    """
    Agent Manager for orchestrating all customer support agents.

    This class manages the multi-agent architecture and is responsible for:
    1. Initializing and managing all specialized agents
    2. Routing customer queries to the most appropriate agent
    3. Coordinating agent handoffs and escalations
    4. Maintaining conversation context across agents
    5. Ensuring optimal customer support delivery

    Architecture Decision: Multi-Agent Orchestration
    - Centralized routing and coordination
    - Intelligent query distribution based on agent expertise
    - Seamless handoffs between specialized agents
    - Fallback mechanisms for edge cases
    - Scalable design for adding new agent types
    """

    def __init__(self, config: Config):
        """
        Initialize the agent manager.

        Args:
            config (Config): Application configuration
        """
        super().__init__()
        self.config = config
        self.agents: Dict[str, BaseAgent] = {}
        self.root_agent: RootAgent = None
        self.conversation_sessions: Dict[str, Dict[str, Any]] = {}

        self.log_info("Initializing Agent Manager with ADK Root Agent")

    async def initialize(self):
        """
        Initialize all agents in the system following ADK patterns.

        This method creates and initializes the root agent and all specialized agents,
        setting up the complete multi-agent support system with ADK architecture.
        """
        try:
            # Initialize the root agent first
            self.root_agent = RootAgent(self.config)

            # Initialize all specialized agents
            self.agents = {
                "general": GeneralSupportAgent(self.config),
                "technical": TechnicalSupportAgent(self.config),
                "billing": BillingSupportAgent(self.config),
                "escalation": EscalationAgent(self.config),
            }

            # Register all agents with the root agent following ADK patterns
            for agent_type, agent in self.agents.items():
                self.root_agent.register_sub_agent(agent_type, agent)

            self.log_info(
                f"Initialized root agent with {len(self.agents)} sub-agents: {list(self.agents.keys())}"
            )

        except Exception as e:
            self.log_error(f"Failed to initialize agents: {e}")
            raise

    async def process_query(self, query: str, user_id: str = None) -> AgentResponse:
        """
        Process a customer query using the root agent following ADK patterns.

        This method delegates to the root agent, which handles intelligent routing
        and delegation to appropriate specialized agents.

        Args:
            query (str): The customer query to process
            user_id (str): Optional user identifier for session tracking

        Returns:
            AgentResponse: The agent's response with metadata
        """
        try:
            # Use the root agent to process the query following ADK patterns
            response = await self.root_agent.process_query(query, user_id)

            # Get conversation state from root agent
            conversation_state = self.root_agent.get_conversation_state(user_id)

            # Update session with routing information
            session = self._get_user_session(user_id)
            session["last_agent"] = response.agent_type
            session["last_query"] = query
            session["last_response"] = response.response
            session["last_timestamp"] = datetime.now()
            session["query_count"] += 1
            session["adk_conversation_state"] = conversation_state

            return response

        except Exception as e:
            self.log_error(f"Error processing query with root agent: {e}")
            # Fallback to general agent
            fallback_response = await self.agents["general"].process_query(
                f"Error occurred: {query}", user_id
            )
            return fallback_response

    async def _select_best_agent(
        self, query: str, session: Dict[str, Any]
    ) -> Tuple[BaseAgent, float]:
        """
        Select the best agent for handling the query.

        This method evaluates all agents and selects the one with the highest
        confidence score for handling the specific query.

        Args:
            query (str): The customer query
            session (Dict[str, Any]): User session information

        Returns:
            Tuple[BaseAgent, float]: Selected agent and confidence score
        """
        agent_scores = {}

        # Get confidence scores from all agents
        for agent_type, agent in self.agents.items():
            confidence = agent.can_handle_query(query)
            agent_scores[agent_type] = confidence

        # Find the agent with highest confidence
        best_agent_type = max(agent_scores, key=agent_scores.get)
        best_confidence = agent_scores[best_agent_type]

        # Apply session-based adjustments
        if session.get("last_agent") and session["last_agent"] != best_agent_type:
            # If switching agents, slightly boost the previous agent's score
            previous_agent_score = agent_scores.get(session["last_agent"], 0)
            if previous_agent_score > best_confidence * 0.8:  # Within 20% of best
                best_agent_type = session["last_agent"]
                best_confidence = previous_agent_score

        return self.agents[best_agent_type], best_confidence

    def _get_user_session(self, user_id: str) -> Dict[str, Any]:
        """
        Get or create a user session for tracking conversation state.

        Args:
            user_id (str): User identifier

        Returns:
            Dict[str, Any]: User session information
        """
        if user_id not in self.conversation_sessions:
            self.conversation_sessions[user_id] = {
                "created_at": datetime.now(),
                "last_agent": None,
                "last_query": None,
                "last_response": None,
                "last_timestamp": None,
                "query_count": 0,
                "agent_history": [],
            }

        return self.conversation_sessions[user_id]

    def _should_escalate(
        self, query: str, response: AgentResponse, session: Dict[str, Any]
    ) -> bool:
        """
        Determine if the query should be escalated to a different agent.

        Args:
            query (str): The customer query
            response (AgentResponse): The current agent's response
            session (Dict[str, Any]): User session information

        Returns:
            bool: True if escalation is needed
        """
        # Check if current agent has low confidence
        if response.confidence < 0.3:
            return True

        # Check for escalation keywords in the query
        escalation_keywords = ["escalate", "supervisor", "human", "manager", "urgent"]
        if any(keyword in query.lower() for keyword in escalation_keywords):
            return True

        # Check if user has been with same agent for too long
        if session["query_count"] > 5 and session["last_agent"] == response.agent_type:
            return True

        return False

    async def _handle_escalation(
        self, query: str, user_id: str, session: Dict[str, Any]
    ) -> AgentResponse:
        """
        Handle escalation to a more appropriate agent.

        Args:
            query (str): The customer query
            user_id (str): User identifier
            session (Dict[str, Any]): User session information

        Returns:
            AgentResponse: Escalation agent's response
        """
        # Use escalation agent for complex cases
        escalation_agent = self.agents["escalation"]

        # Add context about the escalation
        escalation_context = f"Previous agent: {session.get('last_agent', 'None')}\nQuery count: {session['query_count']}\nOriginal query: {query}"

        # Process with escalation agent
        response = await escalation_agent.process_query(query, user_id)

        # Update session
        session["last_agent"] = "escalation"
        session["agent_history"].append("escalation")

        self.log_info(f"Escalated query to escalation agent for user {user_id}")

        return response

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get status information for all agents.

        Returns:
            Dict[str, Any]: Status information for all agents
        """
        status = {}

        for agent_type, agent in self.agents.items():
            status[agent_type] = {
                "active": True,
                "conversation_count": len(agent.conversation_history),
                "last_activity": (
                    agent.conversation_history[-1]["timestamp"]
                    if agent.conversation_history
                    else None
                ),
            }

        return status

    def get_session_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get information about a user's session.

        Args:
            user_id (str): User identifier

        Returns:
            Dict[str, Any]: Session information
        """
        if user_id not in self.conversation_sessions:
            return {"error": "Session not found"}

        session = self.conversation_sessions[user_id]
        return {
            "user_id": user_id,
            "created_at": session["created_at"].isoformat(),
            "query_count": session["query_count"],
            "last_agent": session["last_agent"],
            "last_activity": (
                session["last_timestamp"].isoformat()
                if session["last_timestamp"]
                else None
            ),
            "agent_history": session["agent_history"],
        }

    def clear_user_session(self, user_id: str):
        """
        Clear a user's session and conversation history.

        Args:
            user_id (str): User identifier
        """
        if user_id in self.conversation_sessions:
            del self.conversation_sessions[user_id]
            self.log_info(f"Cleared session for user {user_id}")

        # Clear conversation history for all agents for this user
        for agent in self.agents.values():
            # Filter out messages for this user
            agent.conversation_history = [
                msg
                for msg in agent.conversation_history
                if msg.get("user_id") != user_id
            ]

    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system-wide statistics including ADK metadata.

        Returns:
            Dict[str, Any]: System statistics with ADK information
        """
        total_conversations = sum(
            len(agent.conversation_history) for agent in self.agents.values()
        )
        active_sessions = len(self.conversation_sessions)

        # Get ADK metadata from root agent
        adk_metadata = self.root_agent.get_adk_metadata() if self.root_agent else {}
        agent_hierarchy = (
            self.root_agent.get_agent_hierarchy() if self.root_agent else {}
        )

        return {
            "total_conversations": total_conversations,
            "active_sessions": active_sessions,
            "agents_count": len(self.agents),
            "agent_types": list(self.agents.keys()),
            "adk_metadata": adk_metadata,
            "agent_hierarchy": agent_hierarchy,
            "architecture": "ADK Root Agent Pattern",
        }

    def get_adk_info(self) -> Dict[str, Any]:
        """
        Get ADK-specific information about the system.

        Returns:
            Dict[str, Any]: ADK information
        """
        if not self.root_agent:
            return {"error": "Root agent not initialized"}

        return {
            "root_agent": self.root_agent.get_adk_metadata(),
            "agent_hierarchy": self.root_agent.get_agent_hierarchy(),
            "conversation_states": len(self.root_agent.conversation_state),
            "sub_agents": list(self.root_agent.sub_agents.keys()),
        }
