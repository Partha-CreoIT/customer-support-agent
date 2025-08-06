#!/usr/bin/env python3
"""
Setup script for the AI Customer Support Agent System.

This script helps users set up the system by checking dependencies,
creating necessary directories, and validating configuration.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    else:
        print(f"✅ Python version: {sys.version.split()[0]}")
        return True


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        "google-generativeai",
        "websockets",
        "python-dotenv",
        "pydantic",
        "loguru",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install"] + missing_packages
            )
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

    return True


def create_directories():
    """Create necessary directories."""
    directories = ["logs", "data"]

    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")


def check_configuration():
    """Check if configuration is properly set up."""
    config_file = Path("config.env")

    if not config_file.exists():
        print("❌ Configuration file 'config.env' not found")
        return False

    # Check if Google API key is configured
    try:
        with open(config_file, "r") as f:
            content = f.read()
            if (
                "GOOGLE_API_KEY=" in content
                and "AIzaSyCWOEpGzzmjYdlADHnZuTKsiaCV0lJ4tEs" in content
            ):
                print("✅ Configuration file found with Google API key")
                return True
            else:
                print("⚠️  Configuration file found but Google API key may not be set")
                return False
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")
        return False


def test_google_ai_connection():
    """Test Google AI API connection."""
    try:
        import google.generativeai as genai
        from dotenv import load_dotenv

        # Load environment variables
        load_dotenv("config.env")

        # Configure Google AI
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ Google API key not found in environment")
            return False

        genai.configure(api_key=api_key)

        # Test with a simple request
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content("Hello")

        if response.text:
            print("✅ Google AI API connection successful")
            return True
        else:
            print("❌ Google AI API test failed")
            return False

    except Exception as e:
        print(f"❌ Google AI API test failed: {e}")
        return False


def run_quick_test():
    """Run a quick test of the system."""
    print("\n🧪 Running quick system test...")

    try:
        # Test importing main modules
        from utils.config import Config
        from agents.agent_manager import AgentManager
        from websocket_server.server import WebSocketServer

        print("✅ All modules imported successfully")

        # Test configuration loading
        config = Config()
        print("✅ Configuration loaded successfully")

        print("✅ System test passed")
        return True

    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False


def show_next_steps():
    """Show next steps for the user."""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the server: python main.py")
    print("2. Test the system: python test_client.py")
    print("3. Run the demo: python demo.py")
    print("\n💡 Tips:")
    print("- The server runs on ws://localhost:8765")
    print("- Check logs/ directory for detailed logs")
    print("- Use Ctrl+C to stop the server")
    print("\n🚀 Ready to provide AI-powered customer support!")


def main():
    """Main setup function."""
    print("🤖 AI Customer Support Agent System Setup")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Please install missing dependencies manually:")
        print("   pip install -r requirements.txt")
        sys.exit(1)

    print("\n📁 Creating directories...")
    create_directories()

    print("\n⚙️  Checking configuration...")
    if not check_configuration():
        print("\n❌ Please check your configuration file")
        sys.exit(1)

    print("\n🔗 Testing Google AI connection...")
    if not test_google_ai_connection():
        print("\n⚠️  Google AI connection failed. Please check your API key.")
        print("   You can still run the system, but AI responses may not work.")

    print("\n🧪 Testing system components...")
    if not run_quick_test():
        print("\n❌ System test failed. Please check the error messages above.")
        sys.exit(1)

    show_next_steps()


if __name__ == "__main__":
    main()
