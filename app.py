import streamlit as st
import pandas as pd
import sqlite3
import os
import base64

from db import init_db
from ocr_reader import read_scores
from scheduler import update_match
from chatbot import ask_bot

DB = "data/rc24.db"

os.makedirs("screenshots", exist_ok=True)

st.set_page_config(
    page_title="RCPL Tournament AI Chatbot",
    page_icon="🏏",
    layout="wide"
)


def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


init_db()

bg_img = get_base64("rcpic.jpg")


# ---------- CUSTOM CSS ----------
st.markdown(
    f"""
    <style>

    .stApp {{
        background-image: url("data:image/jpg;base64,{bg_img}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    .main > div {{
        background: rgba(0,0,0,0.35);
        border-radius: 20px;
        padding: 25px;
    }}

    h1, h2, h3 {{
        color: white !important;
        text-align: center;
    }}

    label {{
        color: white !important;
        font-weight: bold;
    }}

    [data-testid="stTabs"] {{
        background: rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 10px;
    }}

    [data-testid="stDataFrame"] {{
        background: rgba(255,255,255,0.08);
        border-radius: 18px;
    }}

    .stTextInput > div > div > input {{
        border-radius: 12px;
        background: rgba(255,255,255,0.15);
        color: white;
        border: 1px solid rgba(255,255,255,0.25);
    }}

    .stNumberInput input {{
        border-radius: 12px;
    }}

    .stButton button {{
        width: 100%;
        border-radius: 14px;
        font-weight: bold;
        font-size: 16px;
        background: linear-gradient(
            135deg,
            #ff9800,
            #ff5722
        );
        color: white;
        border: none;
        padding: 10px;
    }}

    .stButton button:hover {{
        transform: scale(1.02);
    }}

    .block-container {{
        padding-top: 2rem;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- TITLE ----------
st.markdown(
    "<h1>🏏 RCPL Tournament AI Chatbot</h1>",
    unsafe_allow_html=True,
)


# ---------- TABS ----------
tab1, tab2, tab3 = st.tabs(
    [
        "📸 Upload Result",
        "📊 Points Table",
        "🤖 Ask Bot",
    ]
)


# ---------- TAB 1 ----------
with tab1:
    st.subheader("Upload Match Result")

    mid = st.number_input(
        "Match Number",
        min_value=1,
        max_value=25,
        step=1,
    )

    file = st.file_uploader(
        "Upload Screenshot"
    )

    if file:
        path = f"screenshots/{file.name}"

        with open(path, "wb") as f:
            f.write(file.getbuffer())

        s1, s2 = read_scores(path)

        st.success(
            f"Detected Score: {s1} - {s2}"
        )

        if st.button("Save Result"):
            update_match(mid, s1, s2)
            st.success("Result saved successfully ✅")


# ---------- TAB 2 ----------
with tab2:
    st.subheader("Live Points Table")

    conn = sqlite3.connect(DB)

    df = pd.read_sql(
        """
        SELECT *
        FROM standings
        ORDER BY pts DESC, rrd DESC
        """,
        conn,
    )

    conn.close()

    st.dataframe(
        df,
        use_container_width=True,
    )


# ---------- TAB 3 ----------
with tab3:
    st.subheader("Ask Tournament Assistant")

    q = st.text_input(
        "Ask anything..."
    )

    if q:
        with st.spinner("Thinking..."):
            ans = ask_bot(q)

        st.success(ans)
