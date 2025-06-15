import streamlit as st
import openai
import json

# ---------- CONFIG ----------
openai.api_key = st.secrets["OPENAI_API_KEY"]

ROLES = [
    "Retail",
    "Fast-food",
    "Warehouse",
    "Office / Admin",
]
NUM_Q = 5
MODEL = "gpt-3.5-turbo"

PROMPT_Q = """
You are an HR interviewer for an ENTRY-LEVEL {role} position.
Ask question #{n}. Keep it under 25 words. Return ONLY the question.
"""

PROMPT_FB = """
You are a friendly interview coach for first-time job seekers.

Respond ONLY in valid JSON:
{
  "score": 1-5,
  "tips": ["tip 1","tip 2"]
}

QUESTION: "{q}"
ANSWER: "{a}"
"""

# ---------- SESSION ----------
if "step" not in st.session_state:
    st.session_state.update(step=0, role=None, qa=[])

st.title("InterviewMasterAI – Text Demo")

# ---------- SELECT ROLE ----------
if st.session_state.role is None:
    st.session_state.role = st.selectbox("Choose a job type:", [""] + ROLES)
    if st.session_state.role:
        st.session_state.step = 1
        st.experimental_rerun()

# ---------- Q&A LOOP ----------
elif st.session_state.step <= NUM_Q:
    n = st.session_state.step

    # -- get a new question (with error guard) --
    if len(st.session_state.qa) < n:
        try:
            q = openai.ChatCompletion.create(
                model=MODEL,
                messages=[{
                    "role": "system",
                    "content": PROMPT_Q.format(role=st.session_state.role, n=n)
                }]
            ).choices[0].message.content.strip()
        except Exception as e:
            st.error(f"⚠️ OpenAI error: {e}")
            st.stop()

        st.session_state.qa.append([q, None, None])

q = st.session_state.qa[n-1][0]
st.subheader(f"Question {n}/{NUM_Q}")
st.write(q)

    ans = st.text_area("Your answer:", key=f"ans{n}")

    if st.button("Submit", key=f"btn{n}") and ans.strip():
        try:
            fb_raw = openai.ChatCompletion.create(
                model=MODEL,
                messages=[{
                    "role": "system",
                    "content": PROMPT_FB.format(q=q, a=ans)
                }]
            ).choices[0].message.content
            fb = json.loads(fb_raw)
        except Exception as e:
            st.error(f"⚠️ OpenAI error: {e}")
            st.stop()

        st.session_state.qa[n-1][1:] = [ans, fb]
        st.session_state.step += 1
        st.experimental_rerun()

    # show feedback if already answered
    if st.session_state.qa[n-1][2]:
        fb = st.session_state.qa[n-1][2]
        st.success(f"Score: {fb['score']} / 5")
        st.write("Tips:")
        for t in fb["tips"]:
            st.write("•", t)

# ---------- SUMMARY ----------
else:
    st.header("Session summary")
    avg = sum(item[2]["score"] for item in st.session_state.qa) / NUM_Q
    st.write(f"Average score: **{avg:.1f} / 5**")
    for i, (q, a, fb) in enumerate(st.session_state.qa, 1):
        st.write(f"**Q{i}:** {q}")
        st.write(f"_Your answer:_ {a}")
        st.write(f"Score {fb['score']} – Tips: {', '.join(fb['tips'])}")
        st.markdown("---")
    if st.button("Start over"):
        st.session_state.clear()
