from dotenv import load_dotenv
import os
import sqlite3

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

DB = "data/rc24.db"


llm = ChatMistralAI(
    model="mistral-small-latest",
    api_key=os.getenv("MISTRAL_API_KEY"),
    temperature=0.2,
)


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are RC24 Blitz Wheel Championship Assistant.

Tournament rules:
- Win = 3 points
- Tie = 1 point
- Loss = 0 points
- Rank by points first
- If tied, use RRD

Answer only using tournament data.

You can answer:
- who has pending matches
- top 4 standings
- next fixtures
- qualification chances
- player stats

Keep answers short and accurate.
""",
        ),
        (
            "human",
            """
Tournament Context:
{context}

Question:
{question}
""",
        ),
    ]
)


def get_context():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        """
        SELECT *
        FROM standings
        ORDER BY pts DESC, rrd DESC
        """
    )
    standings = c.fetchall()

    c.execute(
        """
        SELECT *
        FROM matches
        WHERE done = 0
        """
    )
    pending = c.fetchall()

    c.execute(
        """
        SELECT *
        FROM matches
        WHERE done = 1
        """
    )
    completed = c.fetchall()

    conn.close()

    context = f"""
Standings:
{standings}

Pending Matches:
{pending}

Completed Matches:
{completed}
"""

    return context


def ask_bot(question):
    context = get_context()

    chain = prompt | llm

    response = chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )

    return response.content