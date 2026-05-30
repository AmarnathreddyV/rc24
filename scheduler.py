import sqlite3

DB = "data/rc24.db"


def update_match(mid, s1, s2):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "UPDATE matches SET s1=?,s2=?,done=1 WHERE id=?",
        (s1, s2, mid)
    )

    c.execute(
        "SELECT p1,p2 FROM matches WHERE id=?",
        (mid,)
    )

    p1, p2 = c.fetchone()

    apply(c, p1, p2, s1, s2)

    conn.commit()
    conn.close()


def apply(c, p1, p2, s1, s2):
    if s1 > s2:
        w, l = p1, p2
    elif s2 > s1:
        w, l = p2, p1
    else:
        w = l = None

    c.execute(
        "UPDATE standings SET played=played+1,rrd=rrd+? WHERE player=?",
        (s1-s2, p1)
    )

    c.execute(
        "UPDATE standings SET played=played+1,rrd=rrd+? WHERE player=?",
        (s2-s1, p2)
    )

    if w:
        c.execute(
            "UPDATE standings SET win=win+1,pts=pts+3 WHERE player=?",
            (w,)
        )
        c.execute(
            "UPDATE standings SET loss=loss+1 WHERE player=?",
            (l,)
        )
    else:
        c.execute(
            "UPDATE standings SET tie=tie+1,pts=pts+1 WHERE player=?",
            (p1,)
        )
        c.execute(
            "UPDATE standings SET tie=tie+1,pts=pts+1 WHERE player=?",
            (p2,)
        )