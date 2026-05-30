import sqlite3
import os
import streamlit as st

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate

DB = "data/rc24.db"

PLAYER_MAP = {
    "Sricharan": "Maruti Masters",
    "Gaylash": "Demon Slayers",
    "Mohith": "Pampers",
    "Suman": "Urban Strikers",
    "Venkat": "Dashing Risers",
    "Kartikeya": "Thunder Buddies",
    "Amarnath": "Amarnath",
    "Venith": "Kanyaraasi",
    "Vishnu": "Lightning Stricker",
    "Hrishikesh": "Knight Riders",
}

TEAM_TO_PLAYER = {v: k for k, v in PLAYER_MAP.items()}

api_key = st.secrets.get(
    "MISTRAL_API_KEY",
    os.getenv("MISTRAL_API_KEY"),
)

llm = ChatMistralAI(
    model="mistral-small-latest",
    api_key=api_key,
    temperature=0,
)


def fmt(team):
    player = TEAM_TO_PLAYER.get(team, team)
    return f"{player} ({team})"


def get_context():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # standings
    c.execute("""
        SELECT player, played, win, loss, tie, pts, rrd
        FROM standings
        ORDER BY pts DESC, rrd DESC
    """)

    standings = "STANDINGS:\n"

    for row in c.fetchall():
        standings += (
            f"{fmt(row[0])} | "
            f"P:{row[1]} "
            f"W:{row[2]} "
            f"L:{row[3]} "
            f"T:{row[4]} "
            f"Pts:{row[5]} "
            f"RRD:{row[6]}\n"
        )

    # pending exact from DB
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
            f"{fmt(row[1])} vs {fmt(row[2])}\n"
        )

    # completed exact from DB
    c.execute("""
        SELECT id,p1,p2,s1,s2
        FROM matches
        WHERE done=1
        ORDER BY id
    """)

    completed = "\nCOMPLETED MATCHES:\n"

    for row in c.fetchall():
        completed += (
            f"Match {row[0]}: "
            f"{fmt(row[1])} {row[3]} - "
            f"{row[4]} {fmt(row[2])}\n"
        )

    conn.close()

    return standings + completed + pending


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are RCPL Champions League assistant.

Important:
- Use ONLY provided tournament data.
- Never invent fixtures.
- Never repeat duplicate fixtures unless they exist in data.
- If user asks pending matches, answer from exact pending list.
- Mention player + team.
- Keep answers short and correct.
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


def ask_bot(question):
    chain = prompt | llm

    response = chain.invoke(
        {
            "context": get_context(),
            "question": question,
        }
    )

    return response.content
