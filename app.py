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
    page_title="RC24 Blitz Championship",
    page_icon="🏏",
    layout="wide",
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

    h1,h2,h3,label {{
        color:white !important;
    }}

    .stButton button {{
        width:100%;
        border-radius:14px;
        font-weight:bold;
        font-size:16px;
        background: linear-gradient(
            135deg,#ff9800,#ff5722
        );
        color:white;
        border:none;
        padding:10px;
    }}

    .stTextInput > div > div > input {{
        border-radius:12px;
        background: rgba(255,255,255,0.15);
        color:white;
    }}

    .stNumberInput input {{
        border-radius:12px;
    }}

    [data-testid="stTabs"] {{
        background: rgba(255,255,255,0.08);
        border-radius:20px;
        padding:10px;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- TITLE ----------
st.markdown(
    "<h1>🏏 RC24 BLITZ WHEEL CHAMPIONSHIP</h1>",
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

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT p1,p2,done FROM matches WHERE id=?",
        (mid,),
    )

    match = c.fetchone()

    conn.close()

    team1 = match[0]
    team2 = match[1]
    done = match[2]

    st.markdown(
        f"""
### 🏏 Match {mid}

**{team1} vs {team2}**
"""
    )

    # already saved
    if done == 1:
        st.error(
            "❌ Already updated. Can't update now."
        )

    else:
        file = st.file_uploader(
            "Upload Screenshot (optional)"
        )

        detected_s1 = None
        detected_s2 = None

        if file:
            path = f"screenshots/{file.name}"

            with open(path, "wb") as f:
                f.write(file.getbuffer())

            detected_s1, detected_s2 = read_scores(path)

            if detected_s1 is not None:
                st.success(
                    f"OCR detected: {team1} {detected_s1} - {detected_s2} {team2}"
                )
            else:
                st.info(
                    "OCR unavailable. Enter manually."
                )

        score1 = st.number_input(
            f"{team1} score",
            min_value=0,
            step=1,
            value=detected_s1 or 0,
        )

        score2 = st.number_input(
            f"{team2} score",
            min_value=0,
            step=1,
            value=detected_s2 or 0,
        )

        if st.button("Save Result"):
            update_match(mid, score1, score2)

            st.success(
                f"✅ Saved: {team1} {score1} - {score2} {team2}"
            )

            st.rerun()

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
