import sqlite3
import os
import streamlit as st

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate

DB = "data/rc24.db"

api_key = st.secrets.get(
    "MISTRAL_API_KEY",
    os.getenv("MISTRAL_API_KEY"),
)

llm = ChatMistralAI(
    model="mistral-small-latest",
    api_key=api_key,
    temperature=0,
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are the RCPL Champions League tournament assistant.

Answer ONLY using the tournament data.

Rules:
- Win = 3 points
- Tie = 1 point
- Loss = 0 points
- Rank by pts then rrd

Very important:
- Never guess.
- If a match is not played say "pending".
- If asked top 4, return exactly top 4.
- Use team names exactly as provided.
- Use standings table first before answering.
- Keep answers short and accurate.
""",
        ),
        (
            "human",
            """
Tournament Data:

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

    # standings
    c.execute("""
        SELECT player, played, win, loss, tie, pts, rrd
        FROM standings
        ORDER BY pts DESC, rrd DESC
    """)

    standings_rows = c.fetchall()

    standings_text = "STANDINGS:\n"

    for row in standings_rows:
        standings_text += (
            f"{row[0]} | "
            f"P:{row[1]} "
            f"W:{row[2]} "
            f"L:{row[3]} "
            f"T:{row[4]} "
            f"Pts:{row[5]} "
            f"RRD:{row[6]}\n"
        )

    # pending
    c.execute("""
        SELECT id,p1,p2
        FROM matches
        WHERE done=0
        ORDER BY id
    """)

    pending_rows = c.fetchall()

    pending_text = "\nPENDING MATCHES:\n"

    for row in pending_rows:
        pending_text += (
            f"Match {row[0]}: "
            f"{row[1]} vs {row[2]}\n"
        )

    # completed
    c.execute("""
        SELECT id,p1,p2,s1,s2
        FROM matches
        WHERE done=1
        ORDER BY id
    """)

    done_rows = c.fetchall()

    completed_text = "\nCOMPLETED MATCHES:\n"

    for row in done_rows:
        completed_text += (
            f"Match {row[0]}: "
            f"{row[1]} {row[3]} - "
            f"{row[4]} {row[2]}\n"
        )

    conn.close()

    return (
        standings_text
        + completed_text
        + pending_text
    )


def ask_bot(question):
    chain = prompt | llm

    response = chain.invoke(
        {
            "context": get_context(),
            "question": question,
        }
    )

    return response.content
