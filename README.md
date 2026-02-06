# Identity Behavior Risk Analysis

This project looks at **how users log in over time** and tries to answer a simple question:

**Does this login behavior look normal, or does it look risky?**

Instead of focusing on complex attacks, the system focuses on **behavior** — how often someone logs in, when they log in, and how many times they fail.

---

## What the project does 

- Reads authentication (login) logs  
- Looks at each user’s login behavior over time  
- Detects patterns that may be risky, such as:
  - Many failed login attempts
  - Logins happening late at night or at unusual hours
  - Unusual login frequency
- Combines these signals into a **simple risk score**
- Shows the results in a visual dashboard

The goal is not to block users, but to **highlight behavior that deserves attention**.

---

## Why this matters

In real life, many security incidents don’t look like obvious attacks.

They look like:
- valid users
- valid credentials
- slightly unusual behavior

By focusing on **behavior instead of rules**, this project shows how suspicious activity can be spotted even when no clear attack signature exists.

---

## What’s in this repository

- `dashboard.py`  
  The main file that analyzes the logs and displays the dashboard.

- Screenshots  
  Example outputs showing:
  - Top risky users
  - User login summaries
  - Risk changes over time

> Real authentication logs are **not included** to avoid sharing sensitive data.

---

## Tools used

- Python
- Pandas (data handling)
- Streamlit (dashboard)
- Matplotlib (charts)

---

## Limitations 

- Uses one type of log source
- Risk scoring is rule-based (no machine learning yet)
- Not real-time

These choices keep the project **simple, explainable, and easy to understand**.

---

## Future ideas

- Add anomaly detection using machine learning
- Support more signals (IP, location, devices)
- Track behavior changes over longer time windows

---

## Disclaimer
This project is for learning and demonstration purposes only.  
It does not analyze real production systems or sensitive user data.

This project is for learning and demonstration purposes only.  
It does not analyze real production systems or sensitive user data.
