"""
Simple Database Manager using pg8000 for order tracking.

This module provides direct PostgreSQL connectivity without SQLAlchemy
to avoid Python 3.13 compatibility issues.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import pg8000
from loguru import logger

from utils.config import Config
from utils.logger import LoggerMixin


class SimpleDatabaseManager(LoggerMixin):
    """
    Simple Database Manager using pg8000 for direct PostgreSQL access.

    This class provides database connectivity and operations for:
    - Order tracking and status queries
    - Customer order history
    - Order status updates
    - Database connection management
    """

    def __init__(self, config: Config):
        """Initialize the database manager."""
        super().__init__()
        self.config = config
        self.connection = None
        self.log_info("Simple Database Manager initialized")

    def connect(self) -> bool:
        """
        Establish database connection using pg8000.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Parse connection string
            db_url = self.config.database_url
            if db_url.startswith("postgresql://"):
                # Extract components from URL
                parts = db_url.replace("postgresql://", "").split("@")
                if len(parts) == 2:
                    user_pass, host_port_db = parts
                    user, password = user_pass.split(":")
                    host_port, database = host_port_db.split("/")
                    host, port = host_port.split(":")
                else:
                    # Fallback to config values
                    host = self.config.database_host
                    port = int(self.config.database_port)
                    database = self.config.database_name
                    user = self.config.database_user
                    password = self.config.database_password
            else:
                # Use config values directly
                host = self.config.database_host
                port = int(self.config.database_port)
                database = self.config.database_name
                user = self.config.database_user
                password = self.config.database_password

            # Create connection
            self.connection = pg8000.Connection(
                host=host, port=port, database=database, user=user, password=password
            )

            # Test connection
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()

            self.log_info(f"Database connected successfully to {database}")
            return True

        except Exception as e:
            self.log_error(f"Database connection failed: {e}")
            return False

    def create_tables(self) -> bool:
        """
        Check if database tables exist (no creation needed).

        Returns:
            bool: True if tables exist, False otherwise
        """
        try:
            cursor = self.connection.cursor()

            # Just check if order_order table exists
            cursor.execute("SELECT 1 FROM order_order LIMIT 1")
            cursor.fetchone()
            cursor.close()

            self.log_info("Database tables exist and are accessible")
            return True

        except Exception as e:
            self.log_error(f"Error checking database tables: {e}")
            return False

    async def get_order_by_number(self, order_number: str) -> Optional[Dict[str, Any]]:
        """
        Get order details by order number.

        Args:
            order_number (str): The order number to search for

        Returns:
            Optional[Dict[str, Any]]: Order details or None if not found
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT id, order_number, user_id, user_name, user_email, 
                       created, status, total_paid, total_paid_currency,
                       shipping_address, billing_address, customer_note, created, updated_at
                FROM order_order 
                WHERE order_number = %s
            """,
                (order_number,),
            )

            row = cursor.fetchone()
            cursor.close()

            if row:
                return {
                    "id": str(row[0]) if row[0] else None,
                    "order_number": row[1],
                    "user_id": row[2],
                    "user_name": row[3],
                    "user_email": row[4],
                    "created": row[5].isoformat() if row[5] else None,
                    "status": row[6],
                    "total_paid": float(row[7]) if row[7] else 0,
                    "total_paid_currency": row[8],
                    "shipping_address": row[9],
                    "billing_address": row[10],
                    "customer_note": row[11],
                    "created_at": row[12].isoformat() if row[12] else None,
                    "updated_at": row[13].isoformat() if row[13] else None,
                }
            return None

        except Exception as e:
            self.log_error(f"Database error getting order {order_number}: {e}")
            return None

    async def get_orders_by_email(self, email: str) -> List[Dict[str, Any]]:
        """
        Get all orders for a given customer email.

        Args:
            email (str): Email address to search for

        Returns:
            List[Dict[str, Any]]: Matching orders
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT id, order_number, user_name, user_email,
                       created, status, total_paid, total_paid_currency, created
                FROM order_order 
                WHERE user_email = %s
                ORDER BY created DESC
            """,
                (email,),
            )

            rows = cursor.fetchall()
            cursor.close()

            self.log_info(
                f"[DB QUERY] get_orders_by_email({email}) → {len(rows)} found"
            )

            return [
                {
                    "id": str(row[0]) if row[0] else None,
                    "order_number": row[1],
                    "user_name": row[2],
                    "user_email": row[3],
                    "created": row[4].isoformat() if row[4] else None,
                    "status": row[5],
                    "total_paid": float(row[6]) if row[6] else 0,
                    "total_paid_currency": row[7],
                    "created_at": row[8].isoformat() if row[8] else None,
                }
                for row in rows
            ]

        except Exception as e:
            self.log_error(f"[DB ERROR] get_orders_by_email failed for {email}: {e}")
            return []

    async def get_orders_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        Get all orders for a customer by customer ID.

        Args:
            customer_id (str): Customer ID to search for

        Returns:
            List[Dict[str, Any]]: List of orders for the customer
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT id, order_number, created, status, total_paid, total_paid_currency, created
                FROM order_order 
                WHERE user_id = %s
                ORDER BY created DESC
            """,
                (customer_id,),
            )

            rows = cursor.fetchall()
            cursor.close()

            return [
                {
                    "id": str(row[0]) if row[0] else None,
                    "order_number": row[1],
                    "created": row[2].isoformat() if row[2] else None,
                    "status": row[3],
                    "total_paid": float(row[4]) if row[4] else 0,
                    "total_paid_currency": row[5],
                    "created_at": row[6].isoformat() if row[6] else None,
                }
                for row in rows
            ]

        except Exception as e:
            self.log_error(
                f"Database error getting orders for customer {customer_id}: {e}"
            )
            return []

    async def search_orders(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search orders by order number, customer name, or email.

        Args:
            search_term (str): Search term to look for

        Returns:
            List[Dict[str, Any]]: Matching orders
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT id, order_number, user_name, user_email,
                       created, status, total_paid, total_paid_currency
                FROM order_order 
                WHERE order_number ILIKE %s 
                   OR user_name ILIKE %s 
                   OR user_email ILIKE %s
                ORDER BY created DESC
                LIMIT 10
            """,
                (
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                ),
            )

            rows = cursor.fetchall()
            cursor.close()

            return [
                {
                    "id": str(row[0]) if row[0] else None,
                    "order_number": row[1],
                    "user_name": row[2],
                    "user_email": row[3],
                    "created": row[4].isoformat() if row[4] else None,
                    "status": row[5],
                    "total_paid": float(row[6]) if row[6] else 0,
                    "total_paid_currency": row[7],
                }
                for row in rows
            ]

        except Exception as e:
            self.log_error(
                f"Database error searching orders with term '{search_term}': {e}"
            )
            return []

    async def get_order_status_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of order statuses.

        Returns:
            Dict[str, Any]: Order status summary
        """
        try:
            cursor = self.connection.cursor()

            # Get total orders
            cursor.execute("SELECT COUNT(*) FROM order_order")
            total_orders = cursor.fetchone()[0]

            # Get orders by status
            cursor.execute(
                """
                SELECT status, COUNT(*) 
                FROM order_order 
                GROUP BY status
            """
            )

            status_counts = dict(cursor.fetchall())
            cursor.close()

            return {
                "total_orders": total_orders,
                "status_breakdown": status_counts,
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.log_error(f"Database error getting order status summary: {e}")
            return {
                "total_orders": 0,
                "status_breakdown": {},
                "last_updated": datetime.utcnow().isoformat(),
            }

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.log_info("Database connection closed")
