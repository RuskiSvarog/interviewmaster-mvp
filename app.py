import streamlit as st, openai, json

# ── CONFIG ───────────────────────────────────────────
openai.api_key = st.secrets["OPENAI_API_KEY"]
MODEL   = "gpt-3.5-turbo"
ROLES   = ["Retail", "Fast-food", "Warehouse", "Office / Admin"]
NUM_Q   = 5

PROMPT_Q = """
You are an HR interviewer for an ENTRY-LEVEL {role} position.
Ask question #{n}. Keep it under 25 words. Return ONLY the question.
"""

PROMPT_FB = """
You are a friendly interview coach for first-time job seekers.

Respond ONLY in valid JSON:
{{"score": 1-5, "tips": ["tip 1","tip 2"]}}

QUESTION: "{q}"
ANSWER: "{a}"
"""

# ── SESSION STATE ────────────────────────────────────
if "step" not in st.session_state:
    st.session_state.update(step=0, role=None, qa=[])

st.title("InterviewMasterAI — Text Demo")

# ── SELECT ROLE ──────────────────────────────────────
if st.session_state.role is None:
    st.session_state.role = st.selectbox("Choose a job type", [""] + ROLES)
    if st.session_state.role:
        st.session_state.step = 1
        st.experimental_rerun()

# ── Q&A LOOP ─────────────────────────────────────────
elif st.session_state.step <= NUM_Q:
    n = st.session_state.step

    # create question if needed
    if len(st.session_state.qa) < n:
        try:
            q = openai.ChatCompletion.create(
                model=MODEL,
                messages=[{"role": "system",
                           "content": PROMPT_Q.format(role=st.session_state.role, n=n)}]
            ).choices[0].message.content.strip()
        except Exception as e:
            st.error(f"⚠️ OpenAI error: {e}")
            st.stop()

        st.session_state.qa.append([q, None, None])

    # Only display question and answer box if the question has been generated
    if len(st.session_state.qa) >= n:
        q = st.session_state.qa[n-1][0]
        st.subheader(f"Question {n}/{NUM_Q}")
        st.write(q)
        ans = st.text_area("Your answer", key=f"ans{n}")

        if st.button("Submit", key=f

