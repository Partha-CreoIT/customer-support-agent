# Google-Style AI Customer Support Agent

A comprehensive, multi-agent AI customer support system built with Python, featuring real-time WebSocket communication and Google's Generative AI integration.

## 🏗️ Architecture Overview

### Google ADK Root Agent Pattern

This system implements the **Google Agent Development Kit (ADK) Root Agent Pattern** with specialized agents for different customer support domains:

- **Root Agent**: Main orchestrator and entry point for all interactions
- **General Support Agent**: Handles general inquiries and routing
- **Technical Support Agent**: Specialized in technical issues and troubleshooting
- **Billing Support Agent**: Handles payment, billing, and subscription queries
- **Escalation Agent**: Manages complex cases and human handoffs

### ADK Architecture Benefits

1. **Root Agent Orchestration**: Centralized coordination following Google ADK patterns
2. **Specialized Expertise**: Each agent has deep knowledge in their domain
3. **Better Scalability**: Easy to add new specialized agents
4. **Improved Response Quality**: Domain-specific knowledge leads to better solutions
5. **ADK Compliance**: Follows Google's official agent development patterns
6. **Flexible Routing**: Intelligent query distribution based on agent capabilities

## 🚀 Features

- **Real-time Communication**: WebSocket-based messaging for instant responses
- **Intelligent Routing**: Automatic query distribution to the most appropriate agent
- **Conversation Management**: Maintains context across agent handoffs
- **Google AI Integration**: Powered by Google's Generative AI models
- **Session Tracking**: Comprehensive user session management
- **Scalable Design**: Easy to extend with new agents and features
- **Professional Logging**: Structured logging with rotation and error tracking

## 📋 Requirements

- Python 3.8+
- Google AI API key
- Internet connection for AI model access

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd customer_support_agent
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   - Copy `config.env` and update with your Google API key
   - The API key is already included in the config file

## ⚙️ Configuration

The system uses a `config.env` file for configuration:

```env
# Google AI API Configuration
GOOGLE_API_KEY=your_api_key_here

# WebSocket Server Configuration
WEBSOCKET_HOST=localhost
WEBSOCKET_PORT=8765

# Agent Configuration
AGENT_MODEL=gemini-pro
MAX_TOKENS=4096
TEMPERATURE=0.7

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/customer_support.log
```

## 🚀 Running the System

### Start the Server (Traditional)

```bash
python main.py
```

### Start with ADK Web Command

```bash
# Show ADK information
python adk_web.py --info

# Show system status
python adk_web.py --status

# Start the ADK web system
python adk_web.py --start

# Start without arguments (default)
python adk_web.py
```

The server will start on `ws://localhost:8765` and you'll see:
```
🚀 Starting ADK Web System...
   WebSocket URL: ws://localhost:8765
   Architecture: ADK Root Agent Pattern
   Press Ctrl+C to stop
```

### Test the System

Use the included test client:

```bash
python test_client.py
```

This provides an interactive chat interface to test all agents.

## 💬 Usage Examples

### General Inquiries
```
User: "What are your business hours?"
Agent: General Support Agent
Response: "Our business hours are Monday through Friday, 9 AM to 6 PM EST..."
```

### Technical Issues
```
User: "My software keeps crashing with error code 0x80070057"
Agent: Technical Support Agent
Response: "I understand you're experiencing a technical issue. Let me help you troubleshoot this error..."
```

### Billing Questions
```
User: "I was charged twice for my subscription this month"
Agent: Billing Support Agent
Response: "I apologize for the billing issue. Let me investigate this double charge for you..."
```

### Escalation Requests
```
User: "I need to speak to a human supervisor immediately"
Agent: Escalation Agent
Response: "I understand you'd like to speak with a human representative. Let me connect you with a supervisor..."
```

## 🔧 WebSocket API

### Message Format

All messages use JSON format:

```json
{
  "type": "message",
  "content": "Your message here",
  "user_id": "optional_user_id",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Response Format

```json
{
  "type": "message",
  "content": "Agent response",
  "agent_type": "general_support",
  "confidence": 0.85,
  "timestamp": "2024-01-01T12:00:00Z",
  "metadata": {
    "user_id": "user123",
    "conversation_length": 5
  }
}
```

### Status Requests

Get system status:
```json
{
  "type": "status",
  "status_type": "system"
}
```

Get agent status:
```json
{
  "type": "status",
  "status_type": "agents"
}
```

## 🏗️ Project Structure

```
customer_support_agent/
├── main.py                 # Main entry point
├── adk_web.py             # ADK web command
├── requirements.txt        # Python dependencies
├── config.env             # Configuration file
├── test_client.py         # Test client for WebSocket
├── demo.py                # Demo script
├── setup.py               # Setup script
├── README.md              # This file
├── agents/                # AI Agents (ADK Pattern)
│   ├── __init__.py
│   ├── base_agent.py      # Base agent class
│   ├── root_agent.py      # ADK Root Agent (main orchestrator)
│   ├── agent_manager.py   # Agent orchestration
│   ├── general_support_agent.py
│   ├── technical_support_agent.py
│   ├── billing_support_agent.py
│   └── escalation_agent.py
├── websocket_server/      # WebSocket server
│   ├── __init__.py
│   └── server.py
├── utils/                 # Utilities
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   └── logger.py          # Logging setup
└── logs/                  # Log files (created automatically)
```

## 🔍 Agent Capabilities

### General Support Agent
- **Domain**: General inquiries, product information, company policies
- **Keywords**: General questions, information requests, basic troubleshooting
- **Confidence**: High for general queries, routes specialized issues

### Technical Support Agent
- **Domain**: Technical problems, software/hardware issues, troubleshooting
- **Keywords**: Error, bug, crash, not working, technical, software, hardware
- **Confidence**: High for technical issues, provides step-by-step solutions

### Billing Support Agent
- **Domain**: Payment processing, billing inquiries, refunds, subscriptions
- **Keywords**: Payment, billing, invoice, charge, refund, subscription
- **Confidence**: High for billing-related queries, handles financial matters

### Escalation Agent
- **Domain**: Complex cases, human handoffs, urgent situations
- **Keywords**: Manager, supervisor, human, urgent, emergency, complaint
- **Confidence**: High for escalation requests, coordinates with human support

## 🧪 Testing

### Manual Testing
1. Start the server: `python main.py`
2. Run test client: `python test_client.py`
3. Try different types of queries to test agent routing

### Example Test Queries

**General**: "What are your business hours?"
**Technical**: "My app keeps crashing with error 0x80070057"
**Billing**: "I was charged twice this month"
**Escalation**: "I need to speak to a human supervisor"

## 🔧 Development

### Adding New Agents

1. Create a new agent class inheriting from `BaseAgent`
2. Implement required methods: `get_system_prompt()`, `can_handle_query()`
3. Add the agent to `AgentManager.initialize()`
4. Update routing logic if needed

### Extending Functionality

- **Database Integration**: Add persistence for conversations and user data
- **Analytics**: Implement conversation analytics and agent performance metrics
- **Human Handoff**: Add seamless transition to human agents
- **Multi-language Support**: Extend agents to handle multiple languages

## 📊 Monitoring

The system provides comprehensive logging and monitoring:

- **Structured Logging**: All operations are logged with context
- **Agent Performance**: Track agent confidence and routing decisions
- **Session Management**: Monitor user sessions and conversation flow
- **Error Tracking**: Detailed error logging for debugging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper documentation
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues or questions:
1. Check the logs in the `logs/` directory
2. Verify your Google API key is valid
3. Ensure all dependencies are installed
4. Check the WebSocket connection on the correct port

## 🎯 Future Enhancements

- **Voice Integration**: Add speech-to-text and text-to-speech capabilities
- **Multi-language Support**: Extend to support multiple languages
- **Advanced Analytics**: Implement conversation analytics and insights
- **Integration APIs**: Add REST APIs for external system integration
- **Mobile App**: Create mobile applications for customer support
- **AI Training**: Implement continuous learning from conversations 