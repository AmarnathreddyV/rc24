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
You are the RCPL Champions League assistant.

Player ↔ Team mapping:

Sricharan (Maruti Masters)
kailash (Demon Slayers)
Mohith (Pampers)
Suman (Urban Strikers)
Venkat (Dashing Risers)
Kartikeya (Thunder Buddies)
Amarnath (Amarnath)
Venith (Kanyaraasi)
Vishnu (Lightning Stricker)
Hrishikesh (Knight Riders)

IMPORTANT:
- Always mention player + team together.
- Never say only team name.
- Never say only player name.

Examples:

Correct:
Sricharan (Maruti Masters)
Venkat (Dashing Risers)

Wrong:
Maruti Masters
Venkat

Rules:
- Win = 3
- Tie = 1
- Loss = 0

Use only tournament data.
Never guess.
Keep answers short and accurate.
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

    c.execute("""
        SELECT player, played, win, loss, tie, pts, rrd
        FROM standings
        ORDER BY pts DESC, rrd DESC
    """)

    rows = c.fetchall()

    standings = "STANDINGS:\n"

    for row in rows:
        standings += (
            f"{row[0]} | "
            f"P:{row[1]} "
            f"W:{row[2]} "
            f"L:{row[3]} "
            f"T:{row[4]} "
            f"Pts:{row[5]} "
            f"RRD:{row[6]}\n"
        )

    c.execute("""
        SELECT id,p1,p2
        FROM matches
        WHERE done=0
        ORDER BY id
    """)

    pending = "\nPENDING MATCHES:\n"

    for row in c.fetchall():
        pending += (
            f"Match {row[0]}: "
            f"{row[1]} vs {row[2]}\n"
        )

    conn.close()

    return standings + pending


def ask_bot(question):
    chain = prompt | llm

    response = chain.invoke(
        {
            "context": get_context(),
            "question": question,
        }
    )

    return response.content
