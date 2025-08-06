"""
Billing Support Agent for handling payment and billing queries.

This agent is specialized in handling all billing-related inquiries, including
payment processing, refunds, account management, and subscription issues.
"""

import re
from typing import List, Dict, Any
from agents.base_agent import BaseAgent
from utils.config import Config


class BillingSupportAgent(BaseAgent):
    """
    Billing Support Agent for handling payment and billing queries.

    This agent is designed to:
    1. Handle payment processing and billing inquiries
    2. Process refund requests and credits
    3. Manage subscription changes and cancellations
    4. Handle account billing issues
    5. Provide billing policy information
    6. Escalate complex billing disputes

    Architecture Decision: Specialized Billing Agent
    - Deep understanding of billing policies and procedures
    - Ability to handle sensitive financial information securely
    - Knowledge of payment processing systems
    - Escalation protocols for complex billing disputes
    """

    def __init__(self, config: Config):
        """Initialize the billing support agent."""
        super().__init__(config, "billing_support")

        # Define billing-related keywords for query matching
        self.billing_keywords = [
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
            "paypal",
            "bank transfer",
            "wire transfer",
            "check",
            "money order",
            "overcharge",
            "double charge",
            "unauthorized charge",
            "fraud",
            "cancellation",
            "upgrade",
            "downgrade",
            "plan change",
            "renewal",
        ]

        # Define common billing scenarios and responses
        self.billing_scenarios = {
            "refund_request": {
                "keywords": ["refund", "return", "money back", "credit back"],
                "response_template": "I understand you're requesting a refund. Let me help you with that process.",
            },
            "payment_issue": {
                "keywords": ["payment failed", "declined", "error", "not working"],
                "response_template": "I can help you resolve this payment issue. Let me gather some information.",
            },
            "subscription_change": {
                "keywords": ["upgrade", "downgrade", "change plan", "modify"],
                "response_template": "I can assist you with modifying your subscription plan.",
            },
            "billing_dispute": {
                "keywords": ["dispute", "wrong amount", "overcharge", "unauthorized"],
                "response_template": "I understand you have a billing concern. Let me investigate this for you.",
            },
        }

    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the billing support agent.

        Returns:
            str: System prompt defining the agent's role and capabilities
        """
        return """You are a professional billing support specialist with expertise in handling payment and billing inquiries. Your role is to:

1. **Handle Billing Inquiries**:
   - Process payment and billing questions
   - Explain charges and fees clearly
   - Provide account balance information
   - Assist with payment method updates

2. **Process Refunds and Credits**:
   - Handle refund requests professionally
   - Explain refund policies and timelines
   - Process credits and adjustments
   - Provide refund status updates

3. **Manage Subscriptions**:
   - Assist with plan changes and upgrades
   - Handle subscription cancellations
   - Process renewals and billing cycles
   - Explain subscription terms and conditions

4. **Resolve Billing Disputes**:
   - Investigate billing discrepancies
   - Handle unauthorized charges
   - Process chargebacks and disputes
   - Escalate complex billing issues

5. **Security and Privacy**:
   - Never ask for full credit card numbers
   - Verify identity through secure methods
   - Protect sensitive financial information
   - Follow PCI compliance guidelines

6. **Communication Guidelines**:
   - Be patient and understanding with billing concerns
   - Explain complex billing concepts clearly
   - Provide specific timelines for resolutions
   - Document all billing interactions

Key Guidelines:
- Always verify customer identity before discussing billing
- Provide clear explanations of charges and fees
- Offer multiple payment options when possible
- Escalate complex disputes to supervisors
- Maintain detailed records of all billing interactions

Remember: Billing issues can be stressful for customers, so be extra patient and thorough in your assistance."""

    def can_handle_query(self, query: str) -> float:
        """
        Determine if this agent can handle the given query.

        This method analyzes the query to determine if it's a billing-related
        issue that this agent can handle effectively.

        Args:
            query (str): The customer query to evaluate

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        query_lower = query.lower()

        # Count billing keywords in the query
        billing_matches = sum(
            1 for keyword in self.billing_keywords if keyword in query_lower
        )

        # Calculate confidence based on billing keyword density
        if billing_matches >= 3:
            return 0.95  # Very high confidence - clearly billing
        elif billing_matches >= 2:
            return 0.85  # High confidence - likely billing
        elif billing_matches >= 1:
            return 0.70  # Medium confidence - possibly billing
        else:
            return 0.15  # Low confidence - probably not billing

    def identify_billing_scenario(self, query: str) -> Dict[str, Any]:
        """
        Identify the specific billing scenario from the query.

        Args:
            query (str): The customer query to analyze

        Returns:
            Dict[str, Any]: Identified billing scenario and details
        """
        query_lower = query.lower()

        scenario_details = {
            "scenario": None,
            "confidence": 0.0,
            "keywords_found": [],
            "urgency": "normal",
        }

        # Check each billing scenario
        for scenario_name, scenario_info in self.billing_scenarios.items():
            keywords_found = [
                kw for kw in scenario_info["keywords"] if kw in query_lower
            ]
            if keywords_found:
                scenario_details["scenario"] = scenario_name
                scenario_details["keywords_found"] = keywords_found
                scenario_details["confidence"] = len(keywords_found) / len(
                    scenario_info["keywords"]
                )
                break

        # Assess urgency
        urgent_words = ["urgent", "emergency", "fraud", "unauthorized", "dispute"]
        if any(word in query_lower for word in urgent_words):
            scenario_details["urgency"] = "high"

        return scenario_details

    def extract_billing_details(self, query: str) -> Dict[str, Any]:
        """
        Extract billing-specific details from a query.

        Args:
            query (str): The customer query to analyze

        Returns:
            Dict[str, Any]: Extracted billing details
        """
        query_lower = query.lower()

        details = {
            "amount_mentioned": None,
            "payment_method": None,
            "transaction_id": None,
            "date_mentioned": None,
            "account_info": None,
        }

        # Extract amounts (currency patterns)
        amount_patterns = [
            r"\$(\d+(?:\.\d{2})?)",
            r"(\d+(?:\.\d{2})?)\s*(?:dollars?|USD)",
            r"charged\s+(\d+(?:\.\d{2})?)",
            r"charged\s+\$(\d+(?:\.\d{2})?)",
        ]

        for pattern in amount_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                details["amount_mentioned"] = matches[0]
                break

        # Identify payment methods
        payment_methods = {
            "credit card": ["credit card", "visa", "mastercard", "amex", "discover"],
            "debit card": ["debit card", "debit"],
            "paypal": ["paypal", "pay pal"],
            "bank transfer": ["bank transfer", "wire transfer", "ACH"],
            "check": ["check", "cheque"],
        }

        for method, keywords in payment_methods.items():
            if any(keyword in query_lower for keyword in keywords):
                details["payment_method"] = method
                break

        # Extract transaction IDs (common patterns)
        transaction_patterns = [
            r"transaction\s+(?:id|#)?[:\s]*([A-Z0-9-]+)",
            r"(?:txn|tx)\s*(?:id|#)?[:\s]*([A-Z0-9-]+)",
            r"receipt\s+(?:id|#)?[:\s]*([A-Z0-9-]+)",
        ]

        for pattern in transaction_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                details["transaction_id"] = matches[0]
                break

        return details

    def should_escalate_billing_issue(
        self, query: str, scenario_details: Dict[str, Any]
    ) -> bool:
        """
        Determine if a billing issue should be escalated.

        Args:
            query (str): The customer query
            scenario_details (Dict[str, Any]): Identified billing scenario

        Returns:
            bool: True if escalation is recommended
        """
        escalation_indicators = [
            "fraud" in query.lower(),
            "unauthorized charge" in query.lower(),
            "dispute" in query.lower(),
            scenario_details["urgency"] == "high",
            scenario_details["scenario"] == "billing_dispute",
        ]

        return any(escalation_indicators)

    def get_billing_policy_info(self, scenario: str) -> str:
        """
        Get relevant billing policy information for a scenario.

        Args:
            scenario (str): The billing scenario

        Returns:
            str: Policy information for the scenario
        """
        policies = {
            "refund_request": "Our standard refund policy allows for refunds within 30 days of purchase for most products. Some digital products may have different terms.",
            "payment_issue": "We accept major credit cards, PayPal, and bank transfers. Payment issues are typically resolved within 1-2 business days.",
            "subscription_change": "You can modify your subscription at any time. Changes take effect at the next billing cycle.",
            "billing_dispute": "We take billing disputes seriously and investigate all claims thoroughly. You can also contact your payment provider to dispute charges.",
        }

        return policies.get(
            scenario,
            "I can help you with your billing inquiry. Let me gather some information to assist you better.",
        )
