"""
Escalation Agent for handling complex cases and human handoffs.

This agent is responsible for managing situations that require human intervention,
complex problem resolution, and ensuring customer satisfaction in difficult cases.
"""

import re
from typing import List, Dict, Any
from agents.base_agent import BaseAgent
from utils.config import Config


class EscalationAgent(BaseAgent):
    """
    Escalation Agent for handling complex cases and human handoffs.

    This agent is designed to:
    1. Handle complex issues that require human intervention
    2. Manage customer complaints and dissatisfaction
    3. Coordinate with human supervisors and specialists
    4. Ensure proper escalation protocols are followed
    5. Provide status updates and follow-up communication
    6. Handle urgent and emergency situations

    Architecture Decision: Escalation Agent for Complex Cases
    - Manages situations beyond AI capabilities
    - Ensures customer satisfaction in difficult cases
    - Coordinates with human support teams
    - Maintains escalation protocols and documentation
    """

    def __init__(self, config: Config):
        """Initialize the escalation agent."""
        super().__init__(config, "escalation")

        # Define escalation triggers and keywords
        self.escalation_keywords = [
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
            "unresolved",
            "multiple attempts",
            "still not working",
            "frustrated",
            "angry",
            "unacceptable",
            "terrible service",
            "worst experience",
        ]

        # Define escalation categories
        self.escalation_categories = {
            "urgent_technical": {
                "keywords": [
                    "urgent",
                    "emergency",
                    "critical",
                    "not working",
                    "broken",
                ],
                "priority": "high",
                "response_template": "I understand this is an urgent technical issue. Let me immediately connect you with our senior technical specialist.",
            },
            "customer_complaint": {
                "keywords": [
                    "complaint",
                    "dissatisfied",
                    "unhappy",
                    "terrible",
                    "worst",
                ],
                "priority": "medium",
                "response_template": "I apologize for your experience. Let me connect you with a supervisor who can address your concerns.",
            },
            "complex_billing": {
                "keywords": ["fraud", "unauthorized", "dispute", "complex billing"],
                "priority": "high",
                "response_template": "This billing matter requires immediate attention. Let me connect you with our billing specialist.",
            },
            "human_request": {
                "keywords": ["human", "real person", "speak to someone", "supervisor"],
                "priority": "medium",
                "response_template": "I understand you'd like to speak with a human representative. Let me connect you with a supervisor.",
            },
        }

    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the escalation agent.

        Returns:
            str: System prompt defining the agent's role and capabilities
        """
        return """You are a senior customer support escalation specialist responsible for handling complex cases and ensuring customer satisfaction. Your role is to:

1. **Handle Complex Escalations**:
   - Manage situations that require human intervention
   - Coordinate with supervisors and specialists
   - Ensure proper escalation protocols are followed
   - Provide status updates and follow-up communication

2. **Customer Satisfaction Focus**:
   - Address customer complaints and dissatisfaction
   - Apologize for poor experiences
   - Ensure customers feel heard and valued
   - Provide immediate solutions when possible

3. **Urgent Situation Management**:
   - Handle emergency and critical issues
   - Prioritize urgent cases appropriately
   - Coordinate with relevant departments
   - Provide immediate assistance and updates

4. **Communication Excellence**:
   - Use empathetic and understanding language
   - Acknowledge customer frustration
   - Provide clear next steps and timelines
   - Maintain professional composure under pressure

5. **Escalation Coordination**:
   - Connect customers with appropriate human representatives
   - Provide context to human agents
   - Ensure smooth handoffs
   - Follow up on escalated cases

6. **Documentation and Follow-up**:
   - Document all escalation details
   - Ensure proper case tracking
   - Schedule follow-up communications
   - Monitor resolution progress

Key Guidelines:
- Always acknowledge the customer's frustration or concern
- Provide immediate assistance when possible
- Explain escalation process clearly
- Ensure customer feels valued and heard
- Follow up on escalated cases
- Maintain detailed records of all interactions

Remember: Your role is to turn difficult situations into positive customer experiences through empathy, professionalism, and effective coordination."""

    def can_handle_query(self, query: str) -> float:
        """
        Determine if this agent can handle the given query.

        This method analyzes the query to determine if it requires escalation
        or human intervention.

        Args:
            query (str): The customer query to evaluate

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        query_lower = query.lower()

        # Count escalation keywords in the query
        escalation_matches = sum(
            1 for keyword in self.escalation_keywords if keyword in query_lower
        )

        # Calculate confidence based on escalation keyword density
        if escalation_matches >= 3:
            return 0.95  # Very high confidence - clearly needs escalation
        elif escalation_matches >= 2:
            return 0.85  # High confidence - likely needs escalation
        elif escalation_matches >= 1:
            return 0.70  # Medium confidence - possibly needs escalation
        else:
            return 0.20  # Low confidence - probably doesn't need escalation

    def identify_escalation_category(self, query: str) -> Dict[str, Any]:
        """
        Identify the specific escalation category from the query.

        Args:
            query (str): The customer query to analyze

        Returns:
            Dict[str, Any]: Identified escalation category and details
        """
        query_lower = query.lower()

        category_details = {
            "category": None,
            "priority": "normal",
            "confidence": 0.0,
            "keywords_found": [],
            "urgency_level": "normal",
        }

        # Check each escalation category
        for category_name, category_info in self.escalation_categories.items():
            keywords_found = [
                kw for kw in category_info["keywords"] if kw in query_lower
            ]
            if keywords_found:
                category_details["category"] = category_name
                category_details["keywords_found"] = keywords_found
                category_details["priority"] = category_info["priority"]
                category_details["confidence"] = len(keywords_found) / len(
                    category_info["keywords"]
                )
                break

        # Assess urgency level
        urgent_words = ["urgent", "emergency", "critical", "immediate", "now"]
        if any(word in query_lower for word in urgent_words):
            category_details["urgency_level"] = "high"

        return category_details

    def extract_escalation_details(self, query: str) -> Dict[str, Any]:
        """
        Extract escalation-specific details from a query.

        Args:
            query (str): The customer query to analyze

        Returns:
            Dict[str, Any]: Extracted escalation details
        """
        query_lower = query.lower()

        details = {
            "customer_emotion": None,
            "issue_duration": None,
            "previous_attempts": None,
            "impact_level": "normal",
            "requested_action": None,
        }

        # Identify customer emotion
        emotion_indicators = {
            "frustrated": ["frustrated", "frustration", "annoyed", "irritated"],
            "angry": ["angry", "mad", "furious", "outraged", "livid"],
            "dissatisfied": ["dissatisfied", "unhappy", "disappointed", "let down"],
            "urgent": ["urgent", "emergency", "critical", "immediate"],
        }

        for emotion, keywords in emotion_indicators.items():
            if any(keyword in query_lower for keyword in keywords):
                details["customer_emotion"] = emotion
                break

        # Identify issue duration
        duration_patterns = [
            r"(\d+)\s*(?:days?|weeks?|months?)\s*(?:ago|for)",
            r"(?:been|trying)\s+(?:for|since)\s+(\d+)\s*(?:days?|weeks?|months?)",
            r"(?:issue|problem)\s+(?:for|since)\s+(\d+)\s*(?:days?|weeks?|months?)",
        ]

        for pattern in duration_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                details["issue_duration"] = matches[0]
                break

        # Identify previous attempts
        attempt_patterns = [
            r"(\d+)\s*(?:times?|attempts?)",
            r"(?:tried|called|contacted)\s+(\d+)\s*(?:times?|attempts?)",
            r"(?:multiple|several)\s+(?:times?|attempts?)",
        ]

        for pattern in attempt_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                details["previous_attempts"] = matches[0]
                break

        # Assess impact level
        high_impact_words = ["critical", "urgent", "emergency", "broken", "not working"]
        if any(word in query_lower for word in high_impact_words):
            details["impact_level"] = "high"

        return details

    def should_escalate_to_human(
        self, query: str, escalation_details: Dict[str, Any]
    ) -> bool:
        """
        Determine if the issue should be escalated to a human.

        Args:
            query (str): The customer query
            escalation_details (Dict[str, Any]): Extracted escalation details

        Returns:
            bool: True if human escalation is recommended
        """
        escalation_indicators = [
            "human" in query.lower(),
            "real person" in query.lower(),
            "supervisor" in query.lower(),
            escalation_details["customer_emotion"] in ["angry", "frustrated"],
            escalation_details["impact_level"] == "high",
            escalation_details["previous_attempts"] is not None,
        ]

        return any(escalation_indicators)

    def get_escalation_response(self, category: str, query: str) -> str:
        """
        Get an appropriate escalation response for the category.

        Args:
            category (str): The escalation category
            query (str): The original customer query

        Returns:
            str: Formatted escalation response
        """
        category_info = self.escalation_categories.get(category, {})
        base_response = category_info.get(
            "response_template",
            "I understand this requires immediate attention. Let me connect you with a specialist.",
        )

        return f"{base_response}\n\nYour concern: '{query}'\n\nI'm escalating this to ensure you receive the assistance you need."

    def get_estimated_resolution_time(self, category: str) -> str:
        """
        Get estimated resolution time for an escalation category.

        Args:
            category (str): The escalation category

        Returns:
            str: Estimated resolution time
        """
        resolution_times = {
            "urgent_technical": "within 2-4 hours",
            "customer_complaint": "within 24 hours",
            "complex_billing": "within 4-8 hours",
            "human_request": "within 1-2 hours",
        }

        return resolution_times.get(category, "within 24 hours")
