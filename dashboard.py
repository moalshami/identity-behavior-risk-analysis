
import pandas as pd
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import streamlit as st
import matplotlib.pyplot as plt

LOG_FILE = "auth.log"
ODD_HOURS = {0, 1, 2, 3, 4, 5, 23}

# ---------- parsing helpers ----------
def parse_time(line: str):
    try:
        return datetime.strptime(line[:15], "%b %d %H:%M:%S")
    except:
        return None

def parse_user(line: str):
    if "for" not in line:
        return None
    try:
        return line.split("for")[1].split("from")[0].strip()
    except:
        return None

def count_fail_to_success_bursts(user_events, window_minutes=10, min_fails=3):
    window = timedelta(minutes=window_minutes)
    user_events = sorted(user_events, key=lambda x: x[0])

    bursts = 0
    for i, (ts, typ) in enumerate(user_events):
        if typ != "success":
            continue
        start = ts - window
        fails = 0
        j = i - 1
        while j >= 0 and user_events[j][0] >= start:
            if user_events[j][1] == "fail":
                fails += 1
            j -= 1
        if fails >= min_fails:
            bursts += 1
    return bursts

def clamp(x, lo=0, hi=100):
    return max(lo, min(hi, x))

def risk_score(success_count, fail_count, burst_count, hour):
    risk = 0
    risk += min(60, fail_count * 12)
    risk += min(40, burst_count * 30)
    if (success_count + fail_count) > 0 and hour in ODD_HOURS:
        risk += 10
    return clamp(risk)


@st.cache_data
def load_and_compute():
    success_by_user_hour = defaultdict(Counter)
    fail_by_user_hour    = defaultdict(Counter)
    events_by_user       = defaultdict(list)

    with open(LOG_FILE, "r", errors="ignore") as f:
        for line in f:
            ts = parse_time(line)
            if ts is None:
                continue

            if ("Accepted" in line) and ("for" in line):
                user = parse_user(line)
                if not user:
                    continue
                success_by_user_hour[user][ts.hour] += 1
                events_by_user[user].append((ts, "success"))

            elif ("Failed password" in line) and ("for" in line):
                user = parse_user(line)
                if not user:
                    continue
                fail_by_user_hour[user][ts.hour] += 1
                events_by_user[user].append((ts, "fail"))

    burst_count_by_user = {u: count_fail_to_success_bursts(evts) for u, evts in events_by_user.items()}

    all_users = sorted(set(success_by_user_hour) | set(fail_by_user_hour))

    
    rows = []
    risk_by_user_hour = {}

    for u in all_users:
        bursts = burst_count_by_user.get(u, 0)
        total_s = sum(success_by_user_hour[u].values())
        total_f = sum(fail_by_user_hour[u].values())

        risk_hours = []
        for hour in range(24):
            s = success_by_user_hour[u].get(hour, 0)
            f = fail_by_user_hour[u].get(hour, 0)
            r = risk_score(s, f, bursts, hour)
            risk_hours.append(r)

        risk_by_user_hour[u] = risk_hours
        rows.append({
            "user": u,
            "success_total": total_s,
            "fail_total": total_f,
            "bursts": bursts,
            "total_risk": sum(risk_hours)
        })

    df = pd.DataFrame(rows).sort_values("total_risk", ascending=False)
    return df, success_by_user_hour, fail_by_user_hour, risk_by_user_hour

# ---------- UI ----------
st.title("Identity Behavior Risk Dashboard (Auth Logs)")

df, success_by_user_hour, fail_by_user_hour, risk_by_user_hour = load_and_compute()

st.subheader("Top Risky Users")
st.dataframe(df.head(15), use_container_width=True)

user = st.selectbox("Select a user", df["user"].tolist())

# build series for selected user
hours = list(range(24))
success = [success_by_user_hour[user].get(h, 0) for h in hours]
fail    = [fail_by_user_hour[user].get(h, 0) for h in hours]
risk    = risk_by_user_hour[user]

st.subheader(f"User Detail: {user}")

col1, col2, col3 = st.columns(3)
col1.metric("Total Success", sum(success))
col2.metric("Total Fail", sum(fail))
col3.metric("Total Risk", sum(risk))

# Risk line chart
fig1 = plt.figure()
plt.plot(hours, risk, marker="o")
plt.xticks(hours)
plt.ylim(0, 100)
plt.xlabel("Hour")
plt.ylabel("Risk (0–100)")
plt.title("Risk by Hour")
st.pyplot(fig1)

# Success vs Fail bars
fig2 = plt.figure()
plt.bar(hours, success)
plt.xticks(hours)
plt.xlabel("Hour")
plt.ylabel("Success count")
plt.title("Successful Logins by Hour")
st.pyplot(fig2)

fig3 = plt.figure()
plt.bar(hours, fail)
plt.xticks(hours)
plt.xlabel("Hour")
plt.ylabel("Fail count")
plt.title("Failed Logins by Hour")
st.pyplot(fig3)

st.caption("Note: Risk score is a simple explainable heuristic using failures, bursts, and odd-hour activity.")
