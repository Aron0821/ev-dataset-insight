#!/usr/bin/env python3
"""
Test script for the intelligent EV chatbot
Run this to verify your chatbot works correctly
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot.intelligent_chatbot import EVChatbot
from utils.database import get_connection
from dotenv import load_dotenv

# Load .env from project root (parent of visualization folder)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)

print(f"📂 Loading .env from: {env_path}")


def print_response(question, response):
    """Pretty print chatbot response"""
    print("\n" + "=" * 70)
    print(f"❓ QUESTION: {question}")
    print("=" * 70)
    print(f"\n📋 TYPE: {response['type'].upper()}")

    if response.get("sql"):
        print(f"\n🔧 SQL GENERATED:")
        print(response["sql"])

    print(f"\n💬 ANSWER:")
    print(response["answer"])

    if response.get("data") and response["data"].get("rows"):
        row_count = len(response["data"]["rows"])
        print(f"\n📊 DATA: {row_count} row(s) retrieved")

    print("\n" + "-" * 70)


def main():
    """Run test suite"""
    print("\n🤖 EV Chatbot Test Suite")
    print("=" * 70)

    # Check Groq API key
    if not os.getenv("GROQ_API_KEY"):
        print("❌ ERROR: GROQ_API_KEY not found in .env file")
        print("\n💡 Get your free key from: https://console.groq.com/")
        print("   Then add it to .env: GROQ_API_KEY=gsk_...")
        return

    print("✅ Groq API key found")

    # Connect to database
    print("\n📡 Connecting to database...")
    db = get_connection()

    if not db:
        print("❌ ERROR: Could not connect to database")
        print(
            "   Check your database configuration in db/src/scripts/util/db_connection.py"
        )
        return

    print("✅ Database connected")

    # Initialize chatbot
    print("\n🚀 Initializing chatbot...")
    chatbot = EVChatbot(db)
    print("✅ Chatbot ready!")

    # Test questions
    test_questions = [
        # GENERAL questions (no database needed)
        "What is an electric vehicle?",
        "How does regenerative braking work?",
        "What's the difference between BEV and PHEV?",
        # DATA_QUERY questions (database only)
        "How many vehicles are in the database?",
        "What are the top 5 manufacturers?",
        "What's the average electric range?",
        # HYBRID questions (knowledge + data)
        "What is CAFV eligibility and how many vehicles qualify?",
        "Explain range anxiety and show me the average ranges by year",
        "Are EVs becoming more popular? Show me the trend",
    ]

    print("\n" + "=" * 70)
    print("Starting tests...")
    print("=" * 70)

    for i, question in enumerate(test_questions, 1):
        print(f"\n\n📌 TEST {i}/{len(test_questions)}")

        try:
            response = chatbot.chat(question)
            print_response(question, response)

        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback

            traceback.print_exc()

    # Close database
    db.close()

    print("\n\n" + "=" * 70)
    print("✅ Test suite completed!")
    print("=" * 70)
    print("\n💡 TIP: Try these in the Streamlit dashboard's AI Analyst tab!")
    print("\nRun: streamlit run app.py")


if __name__ == "__main__":
    main()
