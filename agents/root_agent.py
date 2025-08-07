import re
from typing import Dict, Any
from datetime import datetime

from agents.base_agent import BaseAgent, AgentResponse
from utils.config import Config
from utils.logger import LoggerMixin
from utils.simple_database import SimpleDatabaseManager


class RootAgent(BaseAgent, LoggerMixin):
    def __init__(self, config: Config):
        super().__init__(config, "root_agent")
        self.database_manager = None
        self.conversation_state = {}
        self.sub_agents = {}
        self.log_info("Root Agent initialized with direct database access")

    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the root agent.

        Returns:
            str: System prompt defining the agent's role and capabilities
        """
        return """You are a Customer Support Agent with direct database access. Your role is to help customers with:

1. **Order Status Inquiries**: Check the current status of orders
2. **Order Tracking**: Provide tracking information and delivery updates
3. **Order History**: Look up past orders for customers
4. **Order Search**: Find orders by order number, customer name, or email
5. **Order Details**: Provide comprehensive order information
6. **General Support**: Help with any customer inquiries

**Available Order Statuses:**
- pending: Order is being processed
- confirmed: Order has been confirmed
- processing: Order is being prepared
- shipped: Order has been shipped
- delivered: Order has been delivered
- cancelled: Order has been cancelled
- refunded: Order has been refunded

**CRITICAL RESPONSE GUIDELINES:**
- NEVER ask for login credentials or authentication
- Provide order information directly from the database
- If no orders are found, suggest alternative search terms
- Always be helpful and professional
- Include relevant order details when available
- For non-order queries, provide helpful general support

**Database Integration:**
You have direct access to a development database with order information. Simply provide the order data that is available without requiring any login or authentication.

Remember: Customers should get information immediately without any login requirements."""

    def can_handle_query(self, query: str) -> float:
        """
        Determine if this agent can handle the given query.

        Args:
            query (str): The customer query to evaluate

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        # Root agent can handle all queries
        return 1.0

    async def process_query(self, query: str, user_id: str = None) -> AgentResponse:
        """
        Process a customer query with direct database access.

        Args:
            query (str): The customer query to process
            user_id (str): Optional user identifier for session tracking

        Returns:
            AgentResponse: The agent's response with metadata
        """
        try:
            # Update conversation state
            self.update_conversation_state(user_id, "root_agent", query)

            # Handle query directly with database access
            return await self._handle_query_with_database(query, user_id)

        except Exception as e:
            self.log_error(f"Error in root agent processing: {e}")
            return AgentResponse(
                response="I apologize, but I encountered an error processing your request. Please try again.",
                confidence=0.0,
                agent_type="root_agent",
                timestamp=datetime.now(),
                metadata={"error": str(e)},
            )

    async def _handle_query_with_database(
        self, query: str, user_id: str
    ) -> AgentResponse:
        """
        Handle query with direct database access.

        Args:
            query (str): The customer query
            user_id (str): User identifier

        Returns:
            AgentResponse: Response with order data
        """
        try:
            # Get conversation state to track if we're waiting for customer info
            conversation_state = self.get_conversation_state(user_id)

            # Check if we're in the middle of collecting customer information
            if conversation_state.get("waiting_for_customer_info"):
                # User is providing their contact information
                customer_info = self._extract_customer_info(query)
                if customer_info.get("email") or customer_info.get("phone"):
                    # We have customer info, now search for their orders
                    order_data = await self._get_orders_by_customer_info(customer_info)
                    response = await self._generate_customer_orders_response(
                        query, order_data, customer_info
                    )

                    # Clear the waiting state
                    self._clear_waiting_state(user_id)

                    return AgentResponse(
                        response=response,
                        agent_type="root_agent",
                        confidence=1.0,
                        timestamp=datetime.now(),
                        metadata={
                            "order_data": order_data,
                            "customer_info": customer_info,
                            "user_id": user_id,
                            "query_type": "customer_orders",
                        },
                    )
                else:
                    # Still waiting for proper customer info
                    return AgentResponse(
                        response="I need your email address to look up your orders. Please provide your email address (e.g., john@example.com).",
                        agent_type="root_agent",
                        confidence=0.8,
                        timestamp=datetime.now(),
                        metadata={"waiting_for_info": True, "user_id": user_id},
                    )

            # Check if this is an initial order inquiry
            if self._is_order_inquiry(query):
                # Set waiting state and ask for customer info
                self._set_waiting_state(user_id)
                return AgentResponse(
                    response="I'd be happy to help you check your orders! To look up your order history, I'll need your email address. Please provide your email and I'll find your orders right away.",
                    agent_type="root_agent",
                    confidence=1.0,
                    timestamp=datetime.now(),
                    metadata={"waiting_for_info": True, "user_id": user_id},
                )

            # Handle specific order number queries
            order_info = self._extract_order_info(query)
            if order_info.get("order_number"):
                order_data = await self._get_order_data(query, order_info)
                response = await self._generate_response(query, order_data, user_id)

                return AgentResponse(
                    response=response,
                    agent_type="root_agent",
                    confidence=1.0,
                    timestamp=datetime.now(),
                    metadata={
                        "order_data": order_data,
                        "user_id": user_id,
                        "query_type": "specific_order",
                    },
                )

            # Handle general queries
            response = await self._generate_general_response(query, user_id)
            return AgentResponse(
                response=response,
                agent_type="root_agent",
                confidence=0.9,
                timestamp=datetime.now(),
                metadata={"user_id": user_id, "query_type": "general"},
            )

        except Exception as e:
            self.log_error(f"Error handling query with database: {e}")
            return AgentResponse(
                response="I apologize, but I'm having trouble accessing the order information right now. Please try again in a moment or contact our support team for assistance.",
                agent_type="root_agent",
                confidence=0.3,
                timestamp=datetime.now(),
                metadata={"error": str(e)},
            )

    def _extract_order_info(self, query: str) -> Dict[str, Any]:
        query_lower = query.lower()
        self.log_info(f"[INFO] Extracting order info from query: {query}")

        order_number_patterns = [
            r"order\s+#?(\w+)",
            r"order\s+number\s+#?(\w+)",
            r"#(\w+)",
            r"order\s+(\w+)",
        ]

        order_number = None
        for pattern in order_number_patterns:
            match = re.search(pattern, query_lower)
            if match:
                order_number = match.group(1).upper()
                break

        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        email_match = re.search(email_pattern, query)
        customer_email = email_match.group(0) if email_match else None

        self.log_info(
            f"[PARSE] Extracted → order_number: {order_number}, email: {customer_email}"
        )

        return {
            "order_number": order_number,
            "customer_email": customer_email,
            "query_type": "order_inquiry",
        }

    def _extract_customer_info(self, query: str) -> Dict[str, Any]:
        self.log_info(f"[INFO] Parsing customer info from query: {query}")
        customer_info = {"email": None, "phone": None, "name": None}

        # Email
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        email_match = re.search(email_pattern, query)
        if email_match:
            customer_info["email"] = email_match.group(0)

        # Phone
        phone_patterns = [r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", r"\b\d{10}\b"]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, query)
            if phone_match:
                customer_info["phone"] = phone_match.group(0)
                break

        # Name
        name_patterns = [
            r"my name is (\w+\s+\w+)",
            r"i am (\w+\s+\w+)",
            r"call me (\w+\s+\w+)",
            r"(\w+\s+\w+) is my name",
        ]
        for pattern in name_patterns:
            name_match = re.search(pattern, query.lower())
            if name_match:
                customer_info["name"] = name_match.group(1).title()
                break

        self.log_info(
            f"[PARSE] Extracted → email: {customer_info['email']} | phone: {customer_info['phone']} | name: {customer_info['name']}"
        )
        return customer_info

    async def _get_order_data(
        self, query: str, order_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        order_data = {
            "found": False,
            "orders": [],
            "order_details": None,
            "status_history": [],
        }
        try:
            if not self.database_manager:
                self.log_error("Database manager not initialized")
                return order_data

            # Search by order number
            if order_info.get("order_number"):
                order_num = order_info["order_number"]
                self.log_info(
                    f"[API CALL] → get_order_by_number(order_number={order_num})"
                )
                order_details = await self.database_manager.get_order_by_number(
                    order_num
                )
                self.log_info(f"[API RESULT] ← {order_details}")

                if order_details:
                    order_data["found"] = True
                    order_data["order_details"] = order_details
                    self.log_info(f"[SUCCESS] Found order details for {order_num}")
                else:
                    self.log_info(f"[NOT FOUND] No order found for {order_num}")

            # Search by customer email
            elif order_info.get("customer_email"):
                email = order_info["customer_email"]
                self.log_info(f"[API CALL] → get_orders_by_email(email={email})")
                orders = await self.database_manager.get_orders_by_email(email)
                self.log_info(f"[API RESULT] ← {orders}")

                if orders:
                    order_data["found"] = True
                    order_data["orders"] = orders
                    self.log_info(f"[SUCCESS] Found {len(orders)} orders for {email}")
                else:
                    self.log_info(f"[NOT FOUND] No orders for email {email}")

        except Exception as e:
            self.log_error(f"[ERROR] get_order_data exception: {e}")
        return order_data

    async def _get_orders_by_customer_info(
        self, customer_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        order_data = {
            "found": False,
            "orders": [],
            "customer_name": None,
            "search_method": None,
        }
        try:
            if not self.database_manager:
                self.log_error("Database manager not initialized")
                return order_data

            # Search by email
            if customer_info.get("email"):
                email = customer_info["email"]
                self.log_info(f"[API CALL] → get_orders_by_email(email={email})")
                orders = await self.database_manager.get_orders_by_email(email)
                self.log_info(f"[API RESULT] ← {orders}")

                if orders:
                    order_data["found"] = True
                    order_data["orders"] = orders
                    order_data["search_method"] = "email"
                    order_data["customer_name"] = orders[0].get("user_name", "Customer")
                    self.log_info(f"[SUCCESS] Found {len(orders)} orders via email")
                else:
                    self.log_info(f"[NOT FOUND] No orders for email: {email}")

        except Exception as e:
            self.log_error(f"[ERROR] _get_orders_by_customer_info exception: {e}")
        return order_data

    def _is_order_inquiry(self, query: str) -> bool:
        """
        Check if the query is asking about orders.

        Args:
            query (str): The customer query

        Returns:
            bool: True if it's an order inquiry
        """
        order_keywords = [
            "order",
            "orders",
            "my order",
            "my orders",
            "check order",
            "check orders",
            "order status",
            "order history",
            "track order",
            "find order",
            "find orders",
            "show order",
            "show orders",
            "list order",
            "list orders",
            "order list",
            "order tracking",
            "order details",
            "order information",
        ]

        query_lower = query.lower()
        return any(keyword in query_lower for keyword in order_keywords)

    def _set_waiting_state(self, user_id: str):
        """
        Set the conversation state to waiting for customer information.

        Args:
            user_id (str): User identifier
        """
        if user_id not in self.conversation_state:
            self.conversation_state[user_id] = {}

        self.conversation_state[user_id]["waiting_for_customer_info"] = True
        self.conversation_state[user_id]["waiting_since"] = datetime.now().isoformat()

    def _clear_waiting_state(self, user_id: str):
        """
        Clear the waiting state for customer information.

        Args:
            user_id (str): User identifier
        """
        if user_id in self.conversation_state:
            self.conversation_state[user_id].pop("waiting_for_customer_info", None)
            self.conversation_state[user_id].pop("waiting_since", None)

    def get_conversation_state(self, user_id: str) -> Dict[str, Any]:
        """
        Get conversation state for a user.

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
        Update conversation state.

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

    async def _generate_customer_orders_response(
        self, query: str, order_data: Dict[str, Any], customer_info: Dict[str, Any]
    ) -> str:
        """
        Generate response for customer orders.

        Args:
            query (str): The customer query
            order_data (Dict[str, Any]): Order data
            customer_info (Dict[str, Any]): Customer information

        Returns:
            str: Generated response
        """
        if not order_data["found"]:
            return f"I couldn't find any orders for the email address {customer_info.get('email', 'provided')}. Please check if the email address is correct, or try providing a different email address that you used when placing orders."

        customer_name = order_data.get("customer_name", "there")
        order_count = len(order_data["orders"])

        if order_count == 1:
            order = order_data["orders"][0]
            return f"Hello {customer_name}! I found 1 order for you:\n\nOrder #{order['order_number']} - Status: {order['status']} - Placed on {order['created']} - Total: {order['total_paid']} {order['total_paid_currency']}"
        else:
            response = (
                f"Hello {customer_name}! I found {order_count} orders for you:\n\n"
            )
            for i, order in enumerate(
                order_data["orders"][:5], 1
            ):  # Show first 5 orders
                response += f"{i}. Order #{order['order_number']} - Status: {order['status']} - Placed on {order['created']} - Total: {order['total_paid']} {order['total_paid_currency']}\n"

            if order_count > 5:
                response += f"\n... and {order_count - 5} more orders."

            return response

    async def _generate_response(
        self, query: str, order_data: Dict[str, Any], user_id: str
    ) -> str:
        """
        Generate a response using AI based on order data.

        Args:
            query (str): The customer query
            order_data (Dict[str, Any]): Order data from database
            user_id (str): User identifier

        Returns:
            str: Generated response
        """
        # If no orders found, use fallback
        if not order_data["found"]:
            return "I couldn't find any orders matching your search criteria. Please try searching with a different order number, email, or contact our support team for assistance."

        # Prepare context for AI
        context = self._prepare_context(query, order_data)

        # Generate response using AI with strict instructions
        prompt = f"""
Customer Query: {query}

Available Order Data: {context}

CRITICAL INSTRUCTIONS:
- You have direct access to order data from the database
- DO NOT ask for login, authentication, or account access
- Simply provide the order information that is available
- If no specific orders are found, suggest alternative search terms
- NEVER mention logging in or account access

Provide a direct response with the order information available.
"""

        try:
            response = await self._get_ai_response(prompt)
            # If AI response mentions login, use fallback instead
            if any(
                word in response.lower()
                for word in ["login", "account", "password", "sign in"]
            ):
                return self._generate_fallback_response(query, order_data)
            return response
        except Exception as e:
            self.log_error(f"Error generating AI response: {e}")
            return self._generate_fallback_response(query, order_data)

    def _prepare_context(self, query: str, order_data: Dict[str, Any]) -> str:
        """
        Prepare context for AI response generation.

        Args:
            query (str): The customer query
            order_data (Dict[str, Any]): Order data from database

        Returns:
            str: Formatted context
        """
        if not order_data["found"]:
            return "No orders found matching the search criteria."

        context_parts = []

        if order_data["order_details"]:
            order = order_data["order_details"]
            context_parts.append(
                f"""
Order Details:
- Order Number: {order['order_number']}
- Customer: {order['user_name']} ({order['user_email']})
- Order Date: {order['created']}
- Status: {order['status']}
- Total Amount: {order['total_paid']} {order['total_paid_currency']}
"""
            )

        elif order_data["orders"]:
            context_parts.append(f"Found {len(order_data['orders'])} orders:")
            for order in order_data["orders"][:5]:  # Show first 5 orders
                context_parts.append(
                    f"""
- Order {order['order_number']}: {order['status']} ({order['total_paid']} {order['total_paid_currency']}) - {order['created']}
"""
                )

        return "\n".join(context_parts)

    def _generate_fallback_response(
        self, query: str, order_data: Dict[str, Any]
    ) -> str:
        """
        Generate a fallback response when AI fails.

        Args:
            query (str): The customer query
            order_data (Dict[str, Any]): Order data from database

        Returns:
            str: Fallback response
        """
        if not order_data["found"]:
            return "I couldn't find any orders matching your search criteria. Please try searching with a different order number, email, or contact our support team for assistance."

        if order_data["order_details"]:
            order = order_data["order_details"]
            return f"Here's your order information: Order #{order['order_number']} - Status: {order['status']} - Placed on {order['created']} - Total: {order['total_paid']} {order['total_paid_currency']}."

        elif order_data["orders"]:
            return f"I found {len(order_data['orders'])} orders. Most recent: Order #{order_data['orders'][0]['order_number']} - Status: {order_data['orders'][0]['status']}."

        return "I have order information available, but I'm having trouble displaying it right now. Please try again or contact our support team."

    async def _generate_general_response(self, query: str, user_id: str) -> str:
        """
        Generate response for general queries.

        Args:
            query (str): The customer query
            user_id (str): User identifier

        Returns:
            str: Generated response
        """
        prompt = f"""
Customer Query: {query}

This is a general customer support query. Provide a helpful, professional response. 

Guidelines:
- Be friendly and professional
- Offer to help with order inquiries if relevant
- Provide useful information
- Don't ask for login credentials
- Keep responses concise but helpful

Respond naturally to the customer's query.
"""

        try:
            response = await self._get_ai_response(prompt)
            return response
        except Exception as e:
            self.log_error(f"Error generating general response: {e}")
            return "Thank you for contacting us! How can I help you today? If you have any questions about your orders, I'd be happy to help you check your order status or history."
