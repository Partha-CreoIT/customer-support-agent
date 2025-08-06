# Google ADK Setup Guide

This guide explains how to use the Customer Support Agent System with Google Agent Development Kit (ADK) patterns.

## 🏗️ ADK Architecture

The system follows the **Google ADK Root Agent Pattern** as described in the [Google ADK documentation](https://google.github.io/adk-docs/tutorials/):

### Root Agent Pattern
- **Root Agent**: Main orchestrator and entry point for all interactions
- **Sub-Agents**: Specialized agents for different domains
- **Delegation**: Root agent routes queries to appropriate sub-agents
- **State Management**: Maintains conversation context across agents

## 📁 Directory Structure

You should run ADK commands from the **root directory** of your project:

```
/Users/parthas/PycharmProjects/customer_support_agent/
├── adk_web.py             # ADK web command
├── main.py                 # Traditional entry point
├── agents/
│   ├── root_agent.py      # ADK Root Agent
│   └── ...                # Sub-agents
└── ...
```

## 🚀 Running ADK Commands

### From the Root Directory

Navigate to your project root:
```bash
cd /Users/parthas/PycharmProjects/customer_support_agent
```

### ADK Web Commands

```bash
# Show ADK information
python adk_web.py --info

# Show system status with ADK metadata
python adk_web.py --status

# Start the ADK web system
python adk_web.py --start

# Start without arguments (default)
python adk_web.py
```

### Traditional Commands

```bash
# Setup the system
python setup.py

# Start the server
python main.py

# Test the system
python test_client.py

# Run demo
python demo.py
```

## 🔍 ADK Information

When you run `python adk_web.py --info`, you'll see:

```
🤖 ADK Information:
   Root Agent: root_agent
   Sub Agents: general, technical, billing, escalation
   Conversation States: 0
   Architecture: ADK Root Agent Pattern
```

## 📊 ADK System Status

When you run `python adk_web.py --status`, you'll see:

```
📊 ADK System Status:
   Total Conversations: 0
   Active Sessions: 0
   Agents Count: 4
   Architecture: ADK Root Agent Pattern
```

## 🏗️ ADK Architecture Benefits

1. **Root Agent Orchestration**: Centralized coordination following Google ADK patterns
2. **Specialized Expertise**: Each agent has deep knowledge in their domain
3. **Better Scalability**: Easy to add new specialized agents
4. **Improved Response Quality**: Domain-specific knowledge leads to better solutions
5. **ADK Compliance**: Follows Google's official agent development patterns
6. **Flexible Routing**: Intelligent query distribution based on agent capabilities

## 🔧 ADK Agent Hierarchy

```
Root Agent (root_agent)
├── General Support Agent (general)
├── Technical Support Agent (technical)
├── Billing Support Agent (billing)
└── Escalation Agent (escalation)
```

## 💬 ADK Conversation Flow

1. **Customer Query** → Root Agent
2. **Root Agent Analysis** → Determines best sub-agent
3. **Delegation** → Routes to appropriate sub-agent
4. **Sub-Agent Response** → Processes query with domain expertise
5. **Response Return** → Root agent returns response with metadata

## 🎯 ADK Routing Logic

The Root Agent uses keyword analysis to route queries:

- **General**: Basic inquiries, company information
- **Technical**: Error, bug, crash, software, hardware issues
- **Billing**: Payment, billing, invoice, refund, subscription
- **Escalation**: Manager, supervisor, human, urgent, emergency

## 📈 ADK Metadata

The system provides comprehensive ADK metadata:

- **Agent Hierarchy**: Complete agent structure
- **Conversation States**: User session tracking
- **Delegation History**: Agent handoff tracking
- **Performance Metrics**: Agent usage statistics

## 🔗 ADK WebSocket API

The system provides ADK-compliant WebSocket API:

```json
{
  "type": "message",
  "content": "Your query",
  "user_id": "optional_user_id",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

Response includes ADK metadata:
```json
{
  "type": "message",
  "content": "Agent response",
  "agent_type": "technical_support",
  "confidence": 0.85,
  "metadata": {
    "delegated_by": "root_agent",
    "delegation_timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## 🎉 Getting Started

1. **Setup**: `python setup.py`
2. **ADK Info**: `python adk_web.py --info`
3. **Start ADK**: `python adk_web.py --start`
4. **Test**: `python test_client.py`

The system is now running with Google ADK patterns! 🚀 