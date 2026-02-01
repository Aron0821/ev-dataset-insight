import psycopg2
import openai
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langchain_classic.schema import HumanMessage
import re
load_dotenv()


def db_connect():
    # connection
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
    )

    return conn

# Load environment variables
load_dotenv()
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    temperature=0,
)
# # PostgreSQL connection
# def db_connect():
#     return psycopg2.connect(
#         dbname="your_db_name",
#         user="your_user",
#         password="your_password",
#         host="localhost",
#         port="5432"
#     )
def extract_schema(conn, schema_name="public") -> str:
    """
    Extracts PostgreSQL schema in LLM-friendly format.
    """
    query = """
    SELECT
        table_name,
        column_name,
        data_type
    FROM information_schema.columns
    WHERE table_schema = %s
    ORDER BY table_name, ordinal_position;
    """

    cur = conn.cursor()
    cur.execute(query, (schema_name,))
    rows = cur.fetchall()
    cur.close()

    schema = {}
    for table, column, dtype in rows:
        schema.setdefault(table, []).append(f"{column} {dtype}")

    schema_text = ""
    for table, columns in schema.items():
        schema_text += f"{table}(\n"
        for col in columns:
            schema_text += f"  {col},\n"
        schema_text = schema_text.rstrip(",\n") + "\n)\n\n"

    return schema_text.strip()

# Prompt template for NL → SQL
def build_prompt(user_query: str, schema_text: str) -> str:
    return f"""
You are an expert PostgreSQL SQL generator.

DATABASE SCHEMA:
{schema_text}

RULES:
- Output ONLY valid PostgreSQL SQL
- Use proper JOINs
- SELECT-only queries
- generate sql queries only and nothing else
- do not give any suggestions
- Default LIMIT 100

USER QUERY:
{user_query}
"""

# Generate SQL from natural language
def nl_to_sql(nl_query: str):
    conn = db_connect()
    schema_text = extract_schema(conn)
    prompt = build_prompt(nl_query, schema_text)
    
    response = llm.invoke([
        HumanMessage(content=prompt)
    ])

    sql_query = response.content.strip()  # Extract the SQL string
    return sql_query



# Execute SQL in PostgreSQL
def execute_sql(sql_query: str):
    conn = db_connect()
    cur = conn.cursor()
    schema_text = extract_schema(conn)
    try:
        cur.execute(sql_query)
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        result = [dict(zip(colnames, row)) for row in rows]
    except Exception as e:
        result = {"error": str(e)}
    finally:
        cur.close()
        conn.close()
    return result
def clean_sql(llm_output: str) -> str:
    """
    Extracts ONLY the first SQL query from LLM output and
    removes markdown fences, backticks, and stray quotes.
    """

    # 1️⃣ Extract first ```sql ... ``` block
    sql_block = re.search(
        r"```sql\s*(.*?)\s*```",
        llm_output,
        flags=re.IGNORECASE | re.DOTALL
    )

    if sql_block:
        sql = sql_block.group(1)
    else:
        # 2️⃣ Fallback: first SELECT/WITH statement
        select_stmt = re.search(
            r"\b(select|with)\b[\s\S]*?(?=;|\Z)",
            llm_output,
            flags=re.IGNORECASE
        )

        if not select_stmt:
            raise ValueError("No valid SQL found in LLM output")

        sql = select_stmt.group(0)

    # 3️⃣ Cleanup
    sql = sql.strip()

    # Remove trailing semicolon
    sql = sql.rstrip(";")

    # Remove stray triple backticks or single backticks
    sql = sql.replace("```", "").replace("`", "")

    # Remove wrapping single or double quotes
    sql = re.sub(r'^[\'"]+|[\'"]+$', '', sql)

    return sql.strip()
def build_interpretation_prompt(user_query, sql_result):
    return f"""
You are a data analyst assistant.

Your task:
- Answer the user's question clearly and concisely
- Base your answer ONLY on the provided result
- Do NOT mention SQL, databases, or queries
- If the result is a number, explain what it represents
- If no data is present, say no matching records were found

USER QUESTION:
{user_query}

DATA RESULT:
{sql_result}

FINAL ANSWER:
"""
def interprate_final_result(interpretation_prompt):
    final_response = llm.invoke([
        HumanMessage(content=interpretation_prompt)
    ])
    return final_response
# Main
if __name__ == "__main__":
    user_query = input("Enter your natural language query: ")
    sql_query = nl_to_sql(user_query)
    print("Generated SQL:\n", sql_query)
    clean_sql_query = clean_sql(sql_query)
    print("Generated clean SQL:\n", clean_sql_query)
    results = execute_sql(clean_sql_query)
    print("\nResults:\n", results)
    interpretation_prompt = build_interpretation_prompt(user_query, results)

    final_response = interprate_final_result(interpretation_prompt)
    print("-"*80)
    print(final_response.content)

