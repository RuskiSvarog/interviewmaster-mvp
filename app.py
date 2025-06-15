import streamlit as st
import openai, os, json

# ----- CONFIG -----
openai.api_key = st.secrets["OPENAI_API_KEY"]
ROLES = ["Retail", "Fast-food", "Warehouse", "Office / Admin"]
NUM_QUESTIONS = 5
MODEL = "gpt-4o-mini"  # use "gpt-4o" if available

PROMPT_Q = """
You are an HR interviewer for an ENTRY-LEVEL {role} position.
Ask question #{q_no} that a real recruiter would ask.
Keep it concise (max 25 words).
Return ONLY the question text.
"""

PROMPT_FEEDBACK = """
You are an expert interview coach for first-time job seekers.

1. Give the candidate ONE overall score from 1-5 for this answer (5 = excellent).
2. Provide exactly TWO actionable improvement tips.

Respond in this JSON format only:
{
  "score": <1-5>,
  "tips": ["tip 1", "tip 2"]
}

QUESTION: "{question}"
CANDIDATE_ANSWER: "{answer}"
"""

# ----- SESSION -----
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.role = None
    st.session_state.qa = []

# ----- UI -----
st.title("InterviewMasterAI – Beta Prototype")

if st.session_state.role is None:
    st.subheader("1 • Choose a job type")
    st.session_state.role = st.selectbox("Job type", [""] + ROLES)
    if st.session_state.role:
        st.session_state.step = 1
        st.experimental_rerun()

elif st.session_state.step <= NUM_QUESTIONS:
    q_no = st.session_state.step
    if len(st.session_state.qa) < q_no:
        prompt = PROMPT_Q.format(role=st.session_state.role, q_no=q_no)
        q_text = openai.ChatCompletion.create(
            model=MODEL,
            messages=[{"role": "system", "content": prompt}]
        ).choices[0].message.content.strip()
        st.session_state.qa.append([q_text, None, None])

    q_text = st.session_state.qa[q_no-1][0]
    st.subheader(f"Question {q_no} of {NUM_QUESTIONS}")
    st.write(q_text)

    answer = st.text_area("Your answer", key=f"ans_{q_no}")
    if st.button("Submit answer", key=f"btn_{q_no}") and answer.strip():
        fb_prompt = PROMPT_FEEDBACK.format(question=q_text, answer=answer)
        fb_raw = openai.ChatCompletion.create(
            model=MODEL,
            messages=[{"role": "system", "content": fb_prompt}]
        ).choices[0].message.content
        feedback = json.loads(fb_raw)
        st.session_state.qa[q_no-1][1] = answer
        st.session_state.qa[q_no-1][2] = feedback
        st.session_state.step += 1
        st.experimental_rerun()

    if st.session_state.qa[q_no-1][2]:
        fb = st.session_state.qa[q_no-1][2]
        st.success(f"Score: **{fb['score']} / 5**")
        st.write("**Tips:**")
        for t in fb["tips"]:
            st.write("•", t)

else:
    st.header("Session summary")
    avg = sum(fb["score"] for _,_,fb in st.session_state.qa)/NUM_QUESTIONS
    st.write(f"**Average score:** {avg:.1f} / 5")
    for i,(q,a,fb) in enumerate(st.session_state.qa,1):
        st.write(f"**Q{i}:** {q}")
        st.write(f"*Your answer:* {a}")
        st.write(f"Score {fb['score']} – Tips: {', '.join(fb['tips'])}")
        st.markdown("---")
    st.button("Start over", on_click=lambda: st.session_state.clear())
