"""
Technical Support Agent for handling technical issues and problems.

This agent is specialized in diagnosing and resolving technical problems,
providing step-by-step troubleshooting guidance, and handling software/hardware issues.
"""

import re
from typing import List, Dict, Any
from agents.base_agent import BaseAgent
from utils.config import Config


class TechnicalSupportAgent(BaseAgent):
    """
    Technical Support Agent for handling technical issues and problems.

    This agent is designed to:
    1. Diagnose technical problems through systematic questioning
    2. Provide step-by-step troubleshooting guidance
    3. Handle software and hardware issues
    4. Escalate complex technical problems when needed
    5. Provide technical documentation and resources

    Architecture Decision: Specialized Technical Agent
    - Deep expertise in technical problem-solving
    - Systematic approach to issue diagnosis
    - Access to technical knowledge base
    - Ability to escalate to human technicians for complex issues
    """

    def __init__(self, config: Config):
        """Initialize the technical support agent."""
        super().__init__(config, "technical_support")

        # Define technical keywords for better query matching
        self.technical_keywords = [
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
            "driver",
            "firmware",
            "configuration",
            "settings",
            "network",
            "connection",
            "login",
            "password",
            "authentication",
            "permission",
            "access",
            "security",
            "backup",
            "restore",
            "data",
            "file",
            "corrupt",
            "virus",
            "malware",
        ]

        # Define common technical problems and solutions
        self.common_solutions = {
            "performance": [
                "Check system resources (CPU, memory, disk space)",
                "Close unnecessary applications",
                "Update drivers and software",
                "Run system maintenance tools",
            ],
            "connection": [
                "Check network cables and connections",
                "Restart router/modem",
                "Check firewall settings",
                "Test with different network",
            ],
            "installation": [
                "Check system requirements",
                "Run as administrator",
                "Disable antivirus temporarily",
                "Download fresh copy of installer",
            ],
        }

    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the technical support agent.

        Returns:
            str: System prompt defining the agent's role and capabilities
        """
        return """You are a highly skilled technical support specialist with expertise in diagnosing and resolving technical issues. Your role is to:

1. **Systematic Problem Diagnosis**: 
   - Ask targeted questions to understand the issue
   - Gather relevant system information
   - Identify the root cause of problems

2. **Provide Step-by-Step Solutions**:
   - Give clear, actionable troubleshooting steps
   - Explain technical concepts in simple terms
   - Provide alternative solutions when possible

3. **Technical Expertise Areas**:
   - Software installation and configuration
   - Hardware compatibility and driver issues
   - Network connectivity problems
   - Performance optimization
   - Security and authentication issues
   - Data backup and recovery

4. **Escalation Guidelines**:
   - Escalate complex issues that require human intervention
   - Identify when hardware replacement is needed
   - Recognize when issues are beyond software fixes

5. **Communication Style**:
   - Use clear, non-technical language when possible
   - Be patient and thorough
   - Confirm understanding at each step
   - Provide context for why steps are necessary

6. **Safety and Security**:
   - Never ask for passwords or sensitive information
   - Recommend official sources for downloads
   - Warn about potential data loss risks
   - Suggest backup before major changes

Key Guidelines:
- Always start with basic troubleshooting steps
- Ask for specific error messages when available
- Provide multiple solution options when possible
- Document the troubleshooting process
- Know when to escalate to human support

Remember: Your goal is to solve problems efficiently while ensuring customer safety and data security."""

    def can_handle_query(self, query: str) -> float:
        """
        Determine if this agent can handle the given query.

        This method analyzes the query to determine if it's a technical issue
        that this agent can handle effectively.

        Args:
            query (str): The customer query to evaluate

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        query_lower = query.lower()

        # Count technical keywords in the query
        technical_matches = sum(
            1 for keyword in self.technical_keywords if keyword in query_lower
        )

        # Calculate confidence based on technical keyword density
        if technical_matches >= 3:
            return 0.95  # Very high confidence - clearly technical
        elif technical_matches >= 2:
            return 0.85  # High confidence - likely technical
        elif technical_matches >= 1:
            return 0.70  # Medium confidence - possibly technical
        else:
            return 0.20  # Low confidence - may not be technical

    def extract_technical_details(self, query: str) -> Dict[str, Any]:
        """
        Extract technical details from a query.

        This method analyzes the query to identify specific technical information
        that can help with diagnosis and troubleshooting.

        Args:
            query (str): The customer query to analyze

        Returns:
            Dict[str, Any]: Extracted technical details
        """
        query_lower = query.lower()

        details = {
            "error_messages": [],
            "system_info": [],
            "problem_type": None,
            "urgency_level": "normal",
        }

        # Extract error messages (text in quotes or after "error")
        error_patterns = [
            r'"([^"]*error[^"]*)"',
            r"error[:\s]+([^\n]+)",
            r"failed[:\s]+([^\n]+)",
            r"crash[:\s]+([^\n]+)",
        ]

        for pattern in error_patterns:
            matches = re.findall(pattern, query_lower)
            details["error_messages"].extend(matches)

        # Identify problem type
        if any(word in query_lower for word in ["slow", "performance", "lag"]):
            details["problem_type"] = "performance"
        elif any(word in query_lower for word in ["connection", "network", "internet"]):
            details["problem_type"] = "connection"
        elif any(word in query_lower for word in ["install", "setup", "configuration"]):
            details["problem_type"] = "installation"
        elif any(word in query_lower for word in ["crash", "freeze", "hang"]):
            details["problem_type"] = "stability"

        # Assess urgency
        urgent_words = ["urgent", "emergency", "critical", "broken", "not working"]
        if any(word in query_lower for word in urgent_words):
            details["urgency_level"] = "high"

        return details

    def get_troubleshooting_steps(self, problem_type: str) -> List[str]:
        """
        Get troubleshooting steps for a specific problem type.

        Args:
            problem_type (str): The type of technical problem

        Returns:
            List[str]: List of troubleshooting steps
        """
        return self.common_solutions.get(
            problem_type,
            [
                "1. Restart the application or device",
                "2. Check for software updates",
                "3. Clear cache and temporary files",
                "4. Contact support if the issue persists",
            ],
        )

    def should_escalate(self, query: str, technical_details: Dict[str, Any]) -> bool:
        """
        Determine if the issue should be escalated to human support.

        Args:
            query (str): The customer query
            technical_details (Dict[str, Any]): Extracted technical details

        Returns:
            bool: True if escalation is recommended
        """
        # Escalation criteria
        escalation_indicators = [
            "hardware failure" in query.lower(),
            "data loss" in query.lower(),
            "security breach" in query.lower(),
            technical_details["urgency_level"] == "high",
            len(technical_details["error_messages"]) > 2,
        ]

        return any(escalation_indicators)
