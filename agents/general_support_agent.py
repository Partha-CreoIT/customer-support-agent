"""
General Support Agent for handling general customer queries and routing.

This agent serves as the primary point of contact for customers and is responsible
for understanding their needs and routing them to the appropriate specialized agent
when necessary.
"""

import re
from typing import List, Dict, Any
from agents.base_agent import BaseAgent
from utils.config import Config


class GeneralSupportAgent(BaseAgent):
    """
    General Support Agent for handling general customer queries and routing.

    This agent is designed to:
    1. Handle general inquiries about products, services, and company information
    2. Route customers to specialized agents when needed
    3. Provide basic troubleshooting and guidance
    4. Maintain a friendly and professional tone

    Architecture Decision: General Support Agent as Primary Router
    - Acts as the first point of contact for all customers
    - Uses keyword analysis to determine routing decisions
    - Provides fallback support when specialized agents are unavailable
    - Maintains conversation context for seamless handoffs
    """

    def __init__(self, config: Config):
        """Initialize the general support agent."""
        super().__init__(config, "general_support")

        # Define routing keywords for different agent types
        self.routing_keywords = {
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
                "compatibility",
                "performance",
                "slow",
                "freeze",
                "hang",
                "crashes",
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
                "coupon",
                "bill",
                "account",
                "payment method",
                "credit card",
                "debit card",
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
                "escalate",
                "escalation",
                "serious",
                "critical",
            ],
        }

    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the general support agent.

        Returns:
            str: System prompt defining the agent's role and capabilities
        """
        return """You are a professional customer support representative for a technology company. Your role is to:

1. **Provide Excellent Customer Service**: Be friendly, professional, and helpful in all interactions.

2. **Handle General Inquiries**: Answer questions about:
   - Product information and features
   - Company policies and procedures
   - General troubleshooting steps
   - Account management basics
   - Service availability and status

3. **Route to Specialists**: When customers have specific technical, billing, or complex issues, politely inform them that you'll connect them with a specialist.

4. **Maintain Professional Tone**: Always be courteous, patient, and solution-oriented.

5. **Provide Accurate Information**: Only provide information you're confident about. If unsure, offer to connect with a specialist.

6. **Escalate When Needed**: For urgent, complex, or sensitive issues, offer to escalate to a human supervisor.

Key Guidelines:
- Keep responses clear and concise
- Use a warm, professional tone
- Offer specific solutions when possible
- Acknowledge customer concerns
- Provide next steps when routing to specialists

Remember: You're the first point of contact, so make a great first impression!"""

    def can_handle_query(self, query: str) -> float:
        """
        Determine if this agent can handle the given query.

        This method analyzes the query to determine if it's a general inquiry
        that this agent can handle, or if it should be routed to a specialist.

        Args:
            query (str): The customer query to evaluate

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        query_lower = query.lower()

        # Check for routing keywords
        routing_scores = {}
        for agent_type, keywords in self.routing_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in query_lower:
                    score += 1
            routing_scores[agent_type] = score / len(keywords)

        # If any routing score is high, this agent should route rather than handle
        max_routing_score = max(routing_scores.values()) if routing_scores else 0

        # General queries typically have low routing scores
        if max_routing_score > 0.3:
            return 0.2  # Low confidence - should route to specialist
        elif max_routing_score > 0.1:
            return 0.5  # Medium confidence - can handle but may route
        else:
            return 0.9  # High confidence - general query

    def get_routing_recommendation(self, query: str) -> Dict[str, Any]:
        """
        Get routing recommendation for a query.

        This method analyzes the query and recommends which specialized agent
        would be best suited to handle it.

        Args:
            query (str): The customer query to analyze

        Returns:
            Dict[str, Any]: Routing recommendation with agent type and confidence
        """
        query_lower = query.lower()

        # Calculate scores for each agent type
        scores = {}
        for agent_type, keywords in self.routing_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in query_lower:
                    score += 1
            scores[agent_type] = score / len(keywords)

        # Find the best match
        best_agent = max(scores, key=scores.get) if scores else None
        best_score = max(scores.values()) if scores else 0

        return {
            "recommended_agent": best_agent,
            "confidence": best_score,
            "all_scores": scores,
        }

    def format_routing_message(self, agent_type: str, query: str) -> str:
        """
        Format a message when routing to a specialized agent.

        Args:
            agent_type (str): The type of agent being routed to
            query (str): The original customer query

        Returns:
            str: Formatted routing message
        """
        routing_messages = {
            "technical": "I understand you're experiencing a technical issue. Let me connect you with our technical support specialist who can provide more detailed assistance.",
            "billing": "I can see you have a billing or payment question. Let me transfer you to our billing specialist who can help with your account and payment matters.",
            "escalation": "I understand this is a complex matter that requires immediate attention. Let me connect you with a supervisor who can provide the assistance you need.",
        }

        base_message = routing_messages.get(
            agent_type,
            "Let me connect you with a specialist who can better assist you.",
        )

        return f"{base_message}\n\nYour query: '{query}'\n\nPlease wait while I transfer you to the appropriate specialist."
