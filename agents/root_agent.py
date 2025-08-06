"""
Root Agent for the customer support system following Google ADK patterns.

This agent serves as the main entry point for all customer interactions,
following the Google Agent Development Kit (ADK) architecture.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from agents.base_agent import BaseAgent, AgentResponse
from utils.config import Config
from utils.logger import LoggerMixin


class RootAgent(BaseAgent, LoggerMixin):
    """
    Root Agent following Google ADK patterns for customer support.

    This agent serves as the main orchestrator and entry point for all
    customer interactions, following the Google Agent Development Kit
    architecture patterns.

    ADK Architecture Decision: Root Agent Pattern
    - Serves as the main entry point for all interactions
    - Orchestrates other specialized agents
    - Handles initial routing and delegation
    - Maintains conversation context and state
    - Follows Google ADK patterns for agent development
    """

    def __init__(self, config: Config):
        """Initialize the root agent."""
        super().__init__(config, "root_agent")
        self.sub_agents = {}
        self.conversation_state = {}

        self.log_info("Root Agent initialized following ADK patterns")

    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the root agent following ADK patterns.

        Returns:
            str: System prompt defining the agent's role and capabilities
        """
        return """You are a Root Agent for a customer support system following Google ADK patterns. Your role is to:

1. **Initial Assessment**: 
   - Analyze incoming customer queries
   - Determine the appropriate specialized agent to handle the request
   - Route queries to the most suitable agent

2. **Orchestration**:
   - Coordinate between different specialized agents
   - Manage conversation flow and context
   - Handle agent handoffs seamlessly

3. **Customer Experience**:
   - Provide a unified, professional customer experience
   - Ensure smooth transitions between agents
   - Maintain conversation continuity

4. **ADK Compliance**:
   - Follow Google Agent Development Kit patterns
   - Implement proper agent delegation
   - Maintain conversation state and context

5. **Routing Logic**:
   - General Support: Basic inquiries, company information
   - Technical Support: Software/hardware issues, troubleshooting
   - Billing Support: Payment, billing, subscription issues
   - Escalation: Complex cases, human handoffs

Key Guidelines:
- Always assess the query before routing
- Provide clear transitions when delegating
- Maintain professional, helpful tone
- Follow ADK best practices for agent coordination

Remember: You are the main entry point - make every customer interaction count!"""

    def can_handle_query(self, query: str) -> float:
        """
        Determine if this agent can handle the given query.

        The root agent can handle all queries initially, but will delegate
        to specialized agents based on query content.

        Args:
            query (str): The customer query to evaluate

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        # Root agent can handle all queries initially
        return 1.0

    async def delegate_to_agent(
        self, query: str, agent_type: str, user_id: str = None
    ) -> AgentResponse:
        """
        Delegate a query to a specialized agent following ADK patterns.

        Args:
            query (str): The customer query
            agent_type (str): The type of agent to delegate to
            user_id (str): User identifier

        Returns:
            AgentResponse: The delegated agent's response
        """
        try:
            if agent_type in self.sub_agents:
                agent = self.sub_agents[agent_type]
                response = await agent.process_query(query, user_id)

                # Add delegation metadata
                response.metadata["delegated_by"] = "root_agent"
                response.metadata["delegation_timestamp"] = datetime.now().isoformat()

                self.log_info(f"Delegated query to {agent_type} agent")
                return response
            else:
                # Fallback to general support
                return await self.sub_agents["general"].process_query(query, user_id)

        except Exception as e:
            self.log_error(f"Error delegating to {agent_type} agent: {e}")
            # Fallback response
            return AgentResponse(
                response="I apologize, but I'm having trouble connecting you to the right specialist. Let me help you with your inquiry.",
                confidence=0.5,
                agent_type="root_agent",
                timestamp=datetime.now(),
                metadata={"error": str(e), "fallback": True},
            )

    def register_sub_agent(self, agent_type: str, agent: BaseAgent):
        """
        Register a sub-agent with the root agent following ADK patterns.

        Args:
            agent_type (str): The type of agent
            agent (BaseAgent): The agent instance
        """
        self.sub_agents[agent_type] = agent
        self.log_info(f"Registered sub-agent: {agent_type}")

    def get_agent_hierarchy(self) -> Dict[str, Any]:
        """
        Get the agent hierarchy following ADK patterns.

        Returns:
            Dict[str, Any]: Agent hierarchy information
        """
        return {
            "root_agent": {
                "type": "orchestrator",
                "sub_agents": list(self.sub_agents.keys()),
                "capabilities": ["routing", "delegation", "coordination"],
            },
            "sub_agents": {
                agent_type: {
                    "type": agent.agent_type,
                    "capabilities": (
                        agent.get_capabilities()
                        if hasattr(agent, "get_capabilities")
                        else []
                    ),
                }
                for agent_type, agent in self.sub_agents.items()
            },
        }

    def get_conversation_state(self, user_id: str) -> Dict[str, Any]:
        """
        Get conversation state for a user following ADK patterns.

        Args:
            user_id (str): User identifier

        Returns:
            Dict[str, Any]: Conversation state
        """
        return self.conversation_state.get(
            user_id,
            {
                "current_agent": "root_agent",
                "agent_history": [],
                "conversation_start": datetime.now().isoformat(),
                "message_count": 0,
            },
        )

    def update_conversation_state(self, user_id: str, agent_type: str, query: str):
        """
        Update conversation state following ADK patterns.

        Args:
            user_id (str): User identifier
            agent_type (str): The agent type that handled the query
            query (str): The customer query
        """
        if user_id not in self.conversation_state:
            self.conversation_state[user_id] = {
                "current_agent": "root_agent",
                "agent_history": [],
                "conversation_start": datetime.now().isoformat(),
                "message_count": 0,
            }

        state = self.conversation_state[user_id]
        state["current_agent"] = agent_type
        state["agent_history"].append(
            {
                "agent": agent_type,
                "timestamp": datetime.now().isoformat(),
                "query": query,
            }
        )
        state["message_count"] += 1

    async def process_query(self, query: str, user_id: str = None) -> AgentResponse:
        """
        Process a customer query following ADK patterns.

        This method implements the root agent's main logic for handling
        customer queries and delegating to appropriate sub-agents.

        Args:
            query (str): The customer query to process
            user_id (str): Optional user identifier for session tracking

        Returns:
            AgentResponse: The agent's response with metadata
        """
        try:
            # Update conversation state
            self.update_conversation_state(user_id, "root_agent", query)

            # Determine the best agent to handle this query
            best_agent_type = self._determine_best_agent(query)

            # Delegate to the appropriate agent
            response = await self.delegate_to_agent(query, best_agent_type, user_id)

            # Update conversation state with the delegated agent
            self.update_conversation_state(user_id, best_agent_type, query)

            return response

        except Exception as e:
            self.log_error(f"Error in root agent processing: {e}")
            return AgentResponse(
                response="I apologize, but I encountered an error processing your request. Please try again.",
                confidence=0.0,
                agent_type="root_agent",
                timestamp=datetime.now(),
                metadata={"error": str(e)},
            )

    def _determine_best_agent(self, query: str) -> str:
        """
        Determine the best agent to handle the query following ADK patterns.

        Args:
            query (str): The customer query

        Returns:
            str: The best agent type to handle the query
        """
        query_lower = query.lower()

        # Define routing keywords for each agent type
        routing_keywords = {
            "technical": [
                "error",
                "bug",
                "crash",
                "not working",
                "broken",
                "issue",
                "problem",
                "technical",
                "software",
                "hardware",
                "installation",
                "update",
                "upgrade",
            ],
            "billing": [
                "payment",
                "billing",
                "invoice",
                "charge",
                "cost",
                "price",
                "fee",
                "subscription",
                "refund",
                "credit",
                "discount",
                "promotion",
            ],
            "escalation": [
                "manager",
                "supervisor",
                "human",
                "speak to someone",
                "real person",
                "complex",
                "urgent",
                "emergency",
                "complaint",
                "dissatisfied",
            ],
        }

        # Calculate scores for each agent type
        agent_scores = {}
        for agent_type, keywords in routing_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            agent_scores[agent_type] = score

        # Find the agent with highest score
        best_agent = (
            max(agent_scores, key=agent_scores.get) if agent_scores else "general"
        )

        # If no specific keywords found, use general support
        if agent_scores[best_agent] == 0:
            best_agent = "general"

        return best_agent

    def get_adk_metadata(self) -> Dict[str, Any]:
        """
        Get ADK-specific metadata for this agent.

        Returns:
            Dict[str, Any]: ADK metadata
        """
        return {
            "agent_type": "root_agent",
            "adk_version": "1.0",
            "capabilities": ["routing", "delegation", "orchestration"],
            "sub_agents_count": len(self.sub_agents),
            "conversation_states_count": len(self.conversation_state),
        }
