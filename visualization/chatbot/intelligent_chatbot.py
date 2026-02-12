"""
Intelligent EV Chatbot with Hybrid Query Handling
Handles: General questions, SQL queries, and semantic search
"""

import os
import json
from typing import Dict, Tuple, Optional
from groq import Groq
from dotenv import load_dotenv

# Load .env from project root (parent of parent directory)
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)


class EVChatbot:
    def __init__(self, db_connection):
        """Initialize chatbot with Groq AI and database connection"""
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.db = db_connection
        # Updated to current supported model (as of 2024)
        self.model = "llama-3.3-70b-versatile"  # Current recommended model

    def ensure_db_connection(self):
        """Ensure database connection is healthy, reconnect if needed"""
        try:
            # Test the connection with a simple query
            cursor = self.db.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            self.db.commit()
            return True
        except Exception as e:
            print(f"Database connection lost: {e}")
            try:
                # Try to rollback and reconnect
                self.db.rollback()
                return True
            except:
                print("Could not recover connection")
                return False

    def classify_query(self, question: str) -> Dict:
        """Classify the question type using Groq AI"""

        classification_prompt = f"""Classify this question about electric vehicles:

Question: "{question}"

Determine if this is:
1. GENERAL - General knowledge about EVs OR questions about the dataset structure/contents
   Examples: "What is an EV?", "How do EVs work?", "Tell me about this dataset", "What data do you have?"
   
2. DATA_QUERY - Asking for specific data/statistics from database (requires actual query execution)
   Examples: "How many Teslas?", "Top 5 manufacturers", "Average range by year"
   
3. HYBRID - Needs both general knowledge AND database data
   Examples: "What is CAFV and how many qualify?", "Explain range anxiety and show averages"

IMPORTANT: 
- Questions like "explain the dataset", "what's in the database", "tell me about the data" are GENERAL
- Only use DATA_QUERY if specific numbers/counts/statistics are explicitly requested

Respond ONLY with valid JSON:
{{
    "type": "GENERAL" | "DATA_QUERY" | "HYBRID",
    "needs_database": true/false,
    "reasoning": "brief explanation"
}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": classification_prompt}],
            temperature=0.1,
            max_tokens=200,
        )

        try:
            return json.loads(response.choices[0].message.content)
        except:
            # Default to general if classification fails
            return {
                "type": "GENERAL",
                "needs_database": False,
                "reasoning": "Classification uncertain, defaulting to general",
            }

    def generate_sql(self, question: str) -> Optional[str]:
        """Generate SQL query from natural language"""

        schema_info = """
Database Schema:
- vehicle table: vin, model_year, ev_type, electric_range, cafv_eligibility, model_id, location_id
- model table: model_id, make, model
- location table: location_id, city, county, state, postal_code, vehicle_location (POINT)

Common queries:
- Count vehicles: SELECT COUNT(*) FROM vehicle
- Top makes: SELECT make, COUNT(*) FROM vehicle v JOIN model m ON v.model_id = m.model_id GROUP BY make
- Average range: SELECT AVG(electric_range) FROM vehicle WHERE electric_range > 0
"""

        sql_prompt = f"""{schema_info}

Convert this question to SQL:
Question: "{question}"

Generate ONLY the SQL query, no explanations.
If the question cannot be answered with the database, respond with: NO_SQL_NEEDED
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": sql_prompt}],
            temperature=0.1,
            max_tokens=300,
        )

        sql = response.choices[0].message.content.strip()

        if "NO_SQL_NEEDED" in sql:
            return None

        # Clean up SQL
        sql = sql.replace("```sql", "").replace("```", "").strip()
        return sql

    def execute_sql(self, sql: str) -> Tuple[bool, any]:
        """Execute SQL and return results with proper error handling"""
        cursor = None
        try:
            # Get a fresh cursor
            cursor = self.db.cursor()

            # Execute the query
            cursor.execute(sql)

            # Get results
            results = cursor.fetchall()
            columns = (
                [desc[0] for desc in cursor.description] if cursor.description else []
            )

            # Commit the transaction (even for SELECT queries)
            self.db.commit()

            return True, {"columns": columns, "rows": results}

        except Exception as e:
            # Rollback the failed transaction
            try:
                self.db.rollback()
            except:
                pass

            error_msg = str(e)
            print(f"SQL Error: {error_msg}")
            return False, error_msg

        finally:
            # Always close the cursor
            if cursor:
                try:
                    cursor.close()
                except:
                    pass

    def get_general_answer(self, question: str, context: Optional[Dict] = None) -> str:
        """Get general knowledge answer, optionally with database context"""

        system_prompt = """You are a friendly and knowledgeable expert on electric vehicles (EVs) and the EV dataset.

Your communication style:
- Write in complete, natural sentences
- Be conversational and easy to understand
- Use specific examples when helpful
- Avoid overly technical jargon unless asked
- Make complex topics accessible

You have access to a comprehensive EV database containing:
- 150,000+ electric vehicle records
- Vehicle details: make, model, year, VIN
- Electric range data for BEVs and PHEVs
- Geographic information (city, county, state)
- CAFV (Clean Alternative Fuel Vehicle) eligibility status
- Location coordinates for mapping

You provide helpful information about:
- EV technology and how it works
- Types of EVs (BEV, PHEV, etc.)
- Charging infrastructure
- Environmental benefits
- Market trends
- Policy and regulations
- The dataset structure and contents

When asked about "this dataset" or "the database", explain what data is available and what kinds of questions can be answered.

When you have database results, integrate them naturally into your answer rather than just listing facts."""

        user_message = question

        # Add database context if available
        if context and context.get("rows"):
            context_str = self._format_context(context)
            user_message = f"""{question}

Here's relevant data from our EV database:
{context_str}

Provide a natural, conversational answer that integrates this data seamlessly. 
Write in complete sentences as if explaining to a curious friend.
Use specific numbers and examples from the data to support your explanation."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=500,
        )

        return response.choices[0].message.content

    def _format_context(self, context: Dict) -> str:
        """Format database results into readable context"""
        if not context.get("rows"):
            return "No data found."

        columns = context.get("columns", [])
        rows = context["rows"][:10]  # Limit to 10 rows

        formatted = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            formatted.append(str(row_dict))

        return "\n".join(formatted)

    def answer_data_query(self, question: str, sql_results: Dict) -> str:
        """Generate natural language answer from SQL results"""

        context = self._format_context(sql_results)

        prompt = f"""You are answering a question about electric vehicle data.

Question: "{question}"

Database Results:
{context}

Provide a natural, conversational answer in complete sentences.
- Write like you're talking to a person, not listing data
- Use specific numbers from the results
- Format numbers nicely (use commas for thousands)
- Make it easy to understand
- Be concise but informative
- If asking about "best" or "highest", clearly state what the answer is

Example good answer: "The Tesla Model S has the highest electric range in our database at 337 miles, making it the best choice for long-distance travel."

Example bad answer: "TESLA, MODEL S, 337"

Your answer:"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=400,
        )

        return response.choices[0].message.content

    def chat(self, question: str) -> Dict:
        """Main chat function - routes to appropriate handler"""

        # Ensure database connection is healthy
        if not self.ensure_db_connection():
            return {
                "answer": "Database connection error. Please refresh the page and try again.",
                "type": "error",
                "sql": None,
                "data": None,
            }

        # Step 1: Classify the question
        classification = self.classify_query(question)
        query_type = classification["type"]

        print(f"🔍 Query Type: {query_type}")
        print(f"💭 Reasoning: {classification['reasoning']}")

        # Step 2: Handle based on type
        if query_type == "GENERAL":
            # Pure general knowledge
            answer = self.get_general_answer(question)
            return {"answer": answer, "type": "general", "sql": None, "data": None}

        elif query_type == "DATA_QUERY":
            # Generate and execute SQL
            sql = self.generate_sql(question)

            if not sql:
                return {
                    "answer": "I couldn't generate a database query for that question.",
                    "type": "error",
                    "sql": None,
                    "data": None,
                }

            print(f"📊 Generated SQL: {sql}")

            # Execute SQL
            success, result = self.execute_sql(sql)

            if not success:
                return {
                    "answer": f"Database error: {result}",
                    "type": "error",
                    "sql": sql,
                    "data": None,
                }

            # Generate natural language answer
            answer = self.answer_data_query(question, result)

            return {"answer": answer, "type": "data_query", "sql": sql, "data": result}

        else:  # HYBRID
            # Try to get database context first
            sql = self.generate_sql(question)
            context = None

            if sql:
                print(f"📊 Generated SQL: {sql}")
                success, result = self.execute_sql(sql)
                if success:
                    context = result

            # Get answer with context
            answer = self.get_general_answer(question, context)

            return {"answer": answer, "type": "hybrid", "sql": sql, "data": context}


# ============================================
# Usage Example
# ============================================

if __name__ == "__main__":
    from utils.database import get_connection

    # Initialize chatbot
    db = get_connection()
    chatbot = EVChatbot(db)

    # Test questions
    test_questions = [
        "What is an electric vehicle?",  # GENERAL
        "How many Tesla vehicles are in the database?",  # DATA_QUERY
        "What are the benefits of EVs and which models are most popular?",  # HYBRID
        "Show me average range by manufacturer",  # DATA_QUERY
        "Explain PHEV vs BEV and show me the distribution in our data",  # HYBRID
    ]

    for q in test_questions:
        print("\n" + "=" * 60)
        print(f"❓ Question: {q}")
        print("=" * 60)

        response = chatbot.chat(q)

        print(f"\n💬 Answer:\n{response['answer']}")

        if response["sql"]:
            print(f"\n🔧 SQL Used:\n{response['sql']}")

        print("\n")

    db.close()
