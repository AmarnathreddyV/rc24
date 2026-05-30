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

# change this password
ADMIN_PASSWORD = "rc24admin"

os.makedirs("screenshots", exist_ok=True)

st.set_page_config(
    page_title="RCPL Champions League",
    page_icon="🏏",
    layout="wide",
)


def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def recalculate_standings():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # reset standings
    c.execute("""
        UPDATE standings
        SET
            played=0,
            win=0,
            loss=0,
            tie=0,
            pts=0,
            rrd=0
    """)

    # replay completed matches
    c.execute("""
        SELECT p1,p2,s1,s2
        FROM matches
        WHERE done=1
    """)

    matches = c.fetchall()

    for p1, p2, s1, s2 in matches:

        c.execute(
            "UPDATE standings SET played=played+1, rrd=rrd+? WHERE player=?",
            (s1 - s2, p1),
        )

        c.execute(
            "UPDATE standings SET played=played+1, rrd=rrd+? WHERE player=?",
            (s2 - s1, p2),
        )

        if s1 > s2:
            c.execute(
                "UPDATE standings SET win=win+1, pts=pts+3 WHERE player=?",
                (p1,),
            )
            c.execute(
                "UPDATE standings SET loss=loss+1 WHERE player=?",
                (p2,),
            )

        elif s2 > s1:
            c.execute(
                "UPDATE standings SET win=win+1, pts=pts+3 WHERE player=?",
                (p2,),
            )
            c.execute(
                "UPDATE standings SET loss=loss+1 WHERE player=?",
                (p1,),
            )

        else:
            c.execute(
                "UPDATE standings SET tie=tie+1, pts=pts+1 WHERE player=?",
                (p1,),
            )
            c.execute(
                "UPDATE standings SET tie=tie+1, pts=pts+1 WHERE player=?",
                (p2,),
            )

    conn.commit()
    conn.close()


init_db()

bg_img = get_base64("rcpic.jpg")

# ---------- CSS ----------
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
    "<h1>🏏 RCPL CHAMPIONS LEAGUE</h1>",
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
        "SELECT p1,p2,s1,s2,done FROM matches WHERE id=?",
        (mid,),
    )

    match = c.fetchone()

    conn.close()

    team1, team2, old1, old2, done = match

    st.markdown(
        f"""
### 🏏 Match {mid}

**{team1} vs {team2}**
"""
    )

    # already updated
    if done == 1:
        st.warning(
            f"Already updated: {team1} {old1} - {old2} {team2}"
        )

        st.markdown("### 🔐 Admin Edit")

        pwd = st.text_input(
            "Admin Password",
            type="password",
        )

        if pwd == ADMIN_PASSWORD:

            new1 = st.number_input(
                f"{team1} corrected score",
                min_value=0,
                value=old1,
                key=f"a1_{mid}",
            )

            new2 = st.number_input(
                f"{team2} corrected score",
                min_value=0,
                value=old2,
                key=f"a2_{mid}",
            )

            if st.button("Update as Admin"):

                conn = sqlite3.connect(DB)
                c = conn.cursor()

                c.execute(
                    """
                    UPDATE matches
                    SET s1=?, s2=?
                    WHERE id=?
                    """,
                    (new1, new2, mid),
                )

                conn.commit()
                conn.close()

                recalculate_standings()

                st.success(
                    "✅ Match corrected successfully"
                )

                st.rerun()

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

        score1 = st.number_input(
            f"{team1} score",
            min_value=0,
            value=detected_s1 or 0,
        )

        score2 = st.number_input(
            f"{team2} score",
            min_value=0,
            value=detected_s2 or 0,
        )

        if st.button("Save Result"):
            update_match(mid, score1, score2)

            st.success("✅ Saved")

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
