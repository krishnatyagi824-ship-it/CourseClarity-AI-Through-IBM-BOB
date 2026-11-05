"""
app.py
------
Streamlit front-end for CourseClarity AI.
An IBM Granite-Powered Course Content Simplification Agent.

Run:
    streamlit run app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv

from utils import extract_text_from_pdf, extract_text_from_docx, chunk_text
from agent import (
    simplify_content,
    summarize_content,
    generate_quiz,
    generate_glossary,
    translate_content,
)

load_dotenv()

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="CourseClarity AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* ── Design tokens ─────────────────────────────────────────────────────── */
    :root {
        --cc-blue:        #1d4ed8;   /* primary accent          */
        --cc-blue-soft:   #3b6fd4;   /* hover / secondary       */
        --cc-blue-tint:   #eff6ff;   /* very light blue surface */
        --cc-blue-border: #bfdbfe;   /* blue border             */
        --cc-purple:      #6d4fc2;   /* glossary accent         */
        --cc-surface:     #f6f8fa;   /* card / panel background */
        --cc-border:      #e2e8f0;   /* default border          */
        --cc-text:        #1e293b;   /* primary text            */
        --cc-muted:       #64748b;   /* secondary / muted text  */
        --cc-radius:      8px;
        --cc-radius-sm:   5px;
    }

    /* ── Global base ───────────────────────────────────────────────────────── */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
        font-size: 15px;
        line-height: 1.65;
    }

    /* ── Header banner ─────────────────────────────────────────────────────── */
    .cc-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 100%);
        padding: 1.6rem 2rem 1.4rem;
        border-radius: var(--cc-radius);
        color: #fff;
        margin-bottom: 1.25rem;
    }
    .cc-header h1 {
        margin: 0 0 0.2rem;
        font-size: 1.75rem;
        font-weight: 700;
        letter-spacing: -0.01em;
    }
    .cc-header .cc-tagline {
        margin: 0 0 0.15rem;
        font-size: 1rem;
        font-weight: 600;
        opacity: 0.95;
    }
    .cc-header .cc-subtitle {
        margin: 0;
        font-size: 0.85rem;
        opacity: 0.75;
    }

    /* ── Pill badges ───────────────────────────────────────────────────────── */
    .cc-badges { margin-bottom: 1rem; }
    .badge {
        display: inline-block;
        background: var(--cc-blue-tint);
        color: var(--cc-blue);
        border: 1px solid var(--cc-blue-border);
        border-radius: 20px;
        padding: 3px 11px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.15rem 0.2rem;
    }

    /* ── Generic result box (Simplify / raw fallback) ──────────────────────── */
    .result-box {
        background: var(--cc-surface);
        color: var(--cc-text);
        border: 1px solid var(--cc-border);
        border-left: 4px solid var(--cc-blue);
        border-radius: var(--cc-radius);
        padding: 1.1rem 1.3rem;
        margin-top: 0.6rem;
        font-size: 0.94rem;
        line-height: 1.75;
    }
    .result-box p, .result-box li, .result-box h1, .result-box h2,
    .result-box h3, .result-box h4, .result-box strong, .result-box em {
        color: var(--cc-text) !important;
    }

    /* ── Summary — Overview ────────────────────────────────────────────────── */
    .summary-overview {
        background: var(--cc-blue-tint);
        color: var(--cc-text);
        border: 1px solid var(--cc-blue-border);
        border-left: 4px solid var(--cc-blue);
        border-radius: var(--cc-radius) var(--cc-radius) 0 0;
        padding: 1.1rem 1.3rem 0.9rem;
        font-size: 0.94rem;
        line-height: 1.75;
    }
    .summary-overview p, .summary-overview strong, .summary-overview em {
        color: var(--cc-text) !important;
    }

    /* ── Summary — Key Takeaways ───────────────────────────────────────────── */
    .summary-takeaways {
        background: var(--cc-surface);
        color: var(--cc-text);
        border: 1px solid var(--cc-border);
        border-top: none;
        border-left: 4px solid var(--cc-blue-soft);
        border-radius: 0 0 var(--cc-radius) var(--cc-radius);
        padding: 0.9rem 1.3rem 1.1rem;
        font-size: 0.94rem;
        line-height: 1.75;
        margin-bottom: 0.6rem;
    }
    .summary-takeaways p, .summary-takeaways li,
    .summary-takeaways strong, .summary-takeaways em {
        color: var(--cc-text) !important;
    }

    /* ── Quiz — question card ──────────────────────────────────────────────── */
    .quiz-question {
        background: var(--cc-surface);
        color: var(--cc-text);
        border: 1px solid var(--cc-border);
        border-left: 3px solid var(--cc-blue);
        border-radius: var(--cc-radius);
        padding: 0.9rem 1.2rem 0.6rem;
        margin: 0.8rem 0 0.25rem;
    }
    .quiz-question p, .quiz-question strong, .quiz-question em,
    .quiz-question label, .quiz-question span {
        color: var(--cc-text) !important;
    }

    /* ── Quiz — correct (soft green) ──────────────────────────────────────── */
    .quiz-correct {
        background: #ecfdf5;
        color: #065f46;
        border: 1px solid #a7f3d0;
        border-left: 3px solid #34d399;
        border-radius: var(--cc-radius-sm);
        padding: 0.4rem 0.85rem;
        margin: 0.25rem 0;
        font-weight: 600;
        font-size: 0.93rem;
    }

    /* ── Quiz — incorrect (soft rose) ─────────────────────────────────────── */
    .quiz-incorrect {
        background: #fff1f2;
        color: #9f1239;
        border: 1px solid #fecdd3;
        border-left: 3px solid #fb7185;
        border-radius: var(--cc-radius-sm);
        padding: 0.4rem 0.85rem;
        margin: 0.25rem 0;
        font-weight: 600;
        font-size: 0.93rem;
    }

    /* ── Quiz — neutral option (results phase) ────────────────────────────── */
    .quiz-neutral {
        background: transparent;
        color: var(--cc-muted);
        border-radius: var(--cc-radius-sm);
        padding: 0.4rem 0.85rem;
        margin: 0.25rem 0;
        font-size: 0.93rem;
    }

    /* ── Quiz — score panel ────────────────────────────────────────────────── */
    .quiz-score {
        background: var(--cc-blue-tint);
        color: var(--cc-text);
        border: 1px solid var(--cc-blue-border);
        border-radius: var(--cc-radius);
        padding: 1.2rem 1.8rem;
        margin: 1rem 0;
        text-align: center;
    }
    .quiz-score p, .quiz-score strong { color: var(--cc-text) !important; }

    /* ── Quiz — explanation ────────────────────────────────────────────────── */
    .quiz-explanation {
        background: #fefce8;
        color: #713f12;
        border: 1px solid #fde68a;
        border-left: 3px solid #fbbf24;
        border-radius: var(--cc-radius-sm);
        padding: 0.45rem 0.85rem;
        margin-top: 0.35rem;
        font-size: 0.875rem;
        line-height: 1.6;
    }

    /* ── Glossary — term card ──────────────────────────────────────────────── */
    .glossary-card {
        background: var(--cc-surface);
        color: var(--cc-text);
        border: 1px solid var(--cc-border);
        border-left: 3px solid var(--cc-purple);
        border-radius: var(--cc-radius);
        padding: 0.8rem 1.2rem;
        margin: 0.5rem 0;
    }
    .glossary-card .glossary-term {
        font-size: 0.97rem;
        font-weight: 700;
        color: var(--cc-purple) !important;
        margin-bottom: 0.25rem;
    }
    .glossary-card .glossary-def {
        font-size: 0.91rem;
        color: var(--cc-text) !important;
        line-height: 1.65;
    }
    .glossary-card p, .glossary-card strong, .glossary-card em,
    .glossary-card span {
        color: var(--cc-text) !important;
    }

    /* ── Buttons ───────────────────────────────────────────────────────────── */
    .stButton > button {
        background-color: var(--cc-blue);
        color: #fff;
        border-radius: var(--cc-radius-sm);
        font-weight: 600;
        font-size: 0.9rem;
        border: none;
        padding: 0.45rem 1.1rem;
        transition: background-color 0.15s;
    }
    .stButton > button:hover {
        background-color: var(--cc-blue-soft);
        color: #fff;
    }

    /* ── Footer ────────────────────────────────────────────────────────────── */
    .cc-footer {
        border-top: 1px solid var(--cc-border);
        padding: 1rem 0 0.5rem;
        margin-top: 1rem;
        text-align: center;
    }
    .cc-footer .cc-footer-brand {
        font-size: 0.88rem;
        font-weight: 600;
        color: var(--cc-text);
        margin-bottom: 0.15rem;
    }
    .cc-footer .cc-footer-tagline {
        font-size: 0.78rem;
        color: var(--cc-muted);
        margin-bottom: 0.2rem;
    }
    .cc-footer .cc-footer-meta {
        font-size: 0.74rem;
        color: var(--cc-muted);
    }
    .cc-footer .cc-footer-meta a { color: var(--cc-blue); text-decoration: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="cc-header">
        <h1>CourseClarity AI</h1>
        <p class="cc-tagline">Understand More. Learn Better.</p>
        <p class="cc-subtitle">An IBM Granite-Powered Course Content Simplification Agent</p>
    </div>
    <div class="cc-badges">
        <span class="badge">IBM Granite</span>
        <span class="badge">IBM Cloud Lite</span>
        <span class="badge">First-Gen Learner Friendly</span>
        <span class="badge">Multilingual</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — Input
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Input Settings")

    st.subheader("📄 Content Source")
    input_method = st.radio(
        "Choose input method:",
        ["Paste Text", "Upload PDF", "Upload DOCX"],
        index=0,
    )

    raw_text = ""

    if input_method == "Paste Text":
        raw_text = st.text_area(
            "Paste your course content here:",
            height=300,
            placeholder="Paste lecture notes, textbook paragraphs, or research excerpts…",
        )

    elif input_method == "Upload PDF":
        uploaded = st.file_uploader("Upload a PDF file", type=["pdf"])
        if uploaded:
            with st.spinner("Extracting text from PDF…"):
                raw_text = extract_text_from_pdf(uploaded.read())
            st.success(f"Extracted {len(raw_text):,} characters from PDF.")

    elif input_method == "Upload DOCX":
        uploaded = st.file_uploader("Upload a Word document", type=["docx"])
        if uploaded:
            with st.spinner("Extracting text from DOCX…"):
                raw_text = extract_text_from_docx(uploaded.read())
            st.success(f"Extracted {len(raw_text):,} characters from DOCX.")

    st.divider()

    st.subheader("🌐 Translation (optional)")
    LANGUAGES = [
        "None",
        "Hindi",
        "Tamil",
        "Telugu",
        "Marathi",
        "Bengali",
        "Kannada",
        "Malayalam",
        "Gujarati",
        "Punjabi",
        "Odia",
        "Urdu",
    ]
    target_lang = st.selectbox("Translate simplified output to:", LANGUAGES)


# ---------------------------------------------------------------------------
# Main area — Action tabs
# ---------------------------------------------------------------------------
tab_simplify, tab_summary, tab_quiz, tab_glossary = st.tabs(
    ["✏️ Simplify", "📋 Summary", "❓ Quiz", "📖 Glossary"]
)


def _safe_run(label: str, fn, *args):
    """Run an agent function with spinner + user-friendly error handling."""
    with st.spinner(f"{label}…"):
        try:
            result = fn(*args)
            return result
        except EnvironmentError:
            st.error(
                "The AI service is not configured. "
                "Please contact the administrator to set up the service credentials."
            )
            return None
        except Exception:
            st.error(
                "Something went wrong while processing your request. "
                "Please try again, or contact support if the problem persists."
            )
            return None


def _render_result(text: str) -> None:
    """
    Render Granite-generated Markdown inside the styled result-box.

    Strategy: inject the opening <div> as raw HTML, then let st.markdown()
    process the text so Streamlit's Markdown parser handles **bold**,
    bullet lists, headings, etc.  Close the div with another raw HTML call.
    The explicit color on .result-box ensures visibility in both themes.
    """
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    st.markdown(text)
    st.markdown("</div>", unsafe_allow_html=True)


# ── Tab 1: Simplify ──────────────────────────────────────────────────────────
with tab_simplify:
    st.subheader("✏️ Simplified Explanation")
    st.caption(
        "Converts dense academic text into clear, plain-English explanations "
        "suitable for first-generation and non-English-medium learners."
    )

    if st.button("🚀 Simplify Content", key="btn_simplify"):
        if not raw_text.strip():
            st.warning("Please provide some content using the sidebar.")
        else:
            chunks = chunk_text(raw_text)
            results = []
            for i, chunk in enumerate(chunks):
                st.info(
                    f"Processing chunk {i+1}/{len(chunks)}…" if len(chunks) > 1
                    else "Sending to IBM Granite…"
                )
                result = _safe_run("Simplifying", simplify_content, chunk)
                if result:
                    results.append(result)

            if results:
                final = "\n\n---\n\n".join(results)
                _render_result(final)
                st.session_state["simplified_text"] = final

                if target_lang != "None":
                    st.subheader(f"🌐 Translation: {target_lang}")
                    translated = _safe_run(
                        f"Translating to {target_lang}",
                        translate_content,
                        final,
                        target_lang,
                    )
                    if translated:
                        _render_result(translated)

                st.download_button(
                    "⬇️ Download Simplified Text",
                    data=final,
                    file_name="simplified_content.txt",
                    mime="text/plain",
                )

# ── Tab 2: Summary ───────────────────────────────────────────────────────────
with tab_summary:
    st.subheader("📋 Content Summary")
    st.caption(
        "Generates an Overview paragraph and 3–5 Key Takeaways strictly from "
        "your source content. Language adapts to the selected proficiency level. "
        "Separate from the Glossary."
    )

    summary_level = st.radio(
        "Proficiency level:",
        ["General Audience", "High School", "Undergraduate", "Postgraduate"],
        index=2,
        horizontal=True,
        key="summary_level",
    )

    _LEVEL_HINTS = {
        "General Audience":  "Plain everyday language — no prior knowledge required.",
        "High School":       "Basic academic language with key terms briefly explained.",
        "Undergraduate":     "College-level terminology; foundational knowledge assumed.",
        "Postgraduate":      "Technical depth, relationships, and academic-level insights.",
    }
    st.caption(f"ℹ️ {_LEVEL_HINTS[summary_level]}")

    if st.button("📋 Generate Summary", key="btn_summary"):
        if not raw_text.strip():
            st.warning("Please provide some content using the sidebar.")
        else:
            result = _safe_run(
                "Generating summary",
                summarize_content,
                raw_text[:4000],
                summary_level.lower(),
            )
            if result:
                # Split on the Key Takeaways heading for separate visual panels
                _TAKEAWAYS_MARKER = "### Key Takeaways"
                if _TAKEAWAYS_MARKER in result:
                    overview_part, takeaways_part = result.split(
                        _TAKEAWAYS_MARKER, maxsplit=1
                    )
                    # Strip the "### Overview" heading from overview_part if present
                    overview_text = overview_part.replace("### Overview", "").strip()
                    st.markdown(
                        '<div class="summary-overview">'
                        '<p style="font-weight:700;color:#003f88;margin:0 0 0.5rem;">📄 Overview</p>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(overview_text)
                    st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown(
                        '<div class="summary-takeaways">'
                        '<p style="font-weight:700;color:#00509e;margin:0 0 0.5rem;">🔑 Key Takeaways</p>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(takeaways_part.strip())
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    # Fallback: render as a single result-box if model deviated from format
                    _render_result(result)

                st.download_button(
                    "⬇️ Download Summary",
                    data=result,
                    file_name="summary.txt",
                    mime="text/plain",
                )

# ── Tab 3: Quiz ──────────────────────────────────────────────────────────────

# ---------------------------------------------------------------------------
# Quiz helpers — parser and renderer (defined inside the tab scope guard so
# they are only evaluated when the Quiz tab exists; they do not use Streamlit
# API at definition time, so placing them here is safe).
# ---------------------------------------------------------------------------

def _parse_quiz(raw: str) -> list[dict]:
    """
    Parse IBM Granite's quiz output into a list of question dicts.

    Each dict has keys:
        n           (int)   — question number
        stem        (str)   — question text
        options     (dict)  — {"A": ..., "B": ..., "C": ..., "D": ...}
        answer      (str)   — correct letter, e.g. "A"
        explanation (str)   — why the answer is correct
    """
    import re
    questions = []
    # Split on question markers Q1. Q2. … (handles Q10+ too)
    blocks = re.split(r"\n(?=Q\d+\.)", raw.strip())
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines:
            continue

        # Question stem — first line, strip leading "Q<n>. "
        stem_match = re.match(r"Q(\d+)\.\s*(.+)", lines[0])
        if not stem_match:
            continue
        n = int(stem_match.group(1))
        stem = stem_match.group(2).strip()

        options = {}
        answer = ""
        explanation = ""

        for line in lines[1:]:
            opt = re.match(r"^([ABCD])\.\s*(.+)", line)
            ans = re.match(r"^Answer:\s*([ABCD])", line, re.IGNORECASE)
            exp = re.match(r"^Explanation:\s*(.+)", line, re.IGNORECASE)
            if opt:
                options[opt.group(1)] = opt.group(2).strip()
            elif ans:
                answer = ans.group(1).upper()
            elif exp:
                explanation = exp.group(1).strip()

        if stem and len(options) == 4 and answer:
            questions.append(
                dict(n=n, stem=stem, options=options,
                     answer=answer, explanation=explanation)
            )
    return questions


with tab_quiz:
    st.subheader("❓ Interactive Quiz")
    st.caption(
        "Generates MCQs from your source content. "
        "Select your answers and submit to see your score and explanations."
    )

    # ── Controls ─────────────────────────────────────────────────────────────
    qz_col1, qz_col2 = st.columns([2, 1])
    with qz_col1:
        quiz_level = st.radio(
            "Difficulty level:",
            ["General Audience", "High School", "Undergraduate", "Postgraduate"],
            index=2,
            horizontal=True,
            key="quiz_level",
        )
    with qz_col2:
        quiz_count = st.selectbox(
            "Number of questions:",
            [5, 10, 15, 20],
            index=0,
            key="quiz_count",
        )

    _QUIZ_LEVEL_HINTS = {
        "General Audience": "Broad conceptual questions — no technical background required.",
        "High School":      "Key facts and basic concept questions.",
        "Undergraduate":    "Conceptual and application-level questions.",
        "Postgraduate":     "Deep technical questions testing mechanisms and relationships.",
    }
    st.caption(f"ℹ️ {_QUIZ_LEVEL_HINTS[quiz_level]}")

    if st.button("❓ Generate Quiz", key="btn_quiz"):
        if not raw_text.strip():
            st.warning("Please provide some content using the sidebar.")
        else:
            raw_quiz = _safe_run(
                "Generating quiz",
                generate_quiz,
                raw_text[:4000],
                quiz_count,
                quiz_level.lower(),
            )
            if raw_quiz:
                parsed = _parse_quiz(raw_quiz)
                if not parsed:
                    st.error(
                        "Could not parse the quiz output. "
                        "Try again or reduce the question count."
                    )
                else:
                    # Store in session state; reset any prior answers / submission
                    st.session_state["quiz_questions"] = parsed
                    st.session_state["quiz_raw"] = raw_quiz
                    st.session_state["quiz_answers"] = {}
                    st.session_state["quiz_submitted"] = False

    # ── Render quiz if questions are available ────────────────────────────────
    if st.session_state.get("quiz_questions"):
        questions = st.session_state["quiz_questions"]
        submitted = st.session_state.get("quiz_submitted", False)

        if not submitted:
            # ── Answer-selection phase ────────────────────────────────────
            st.markdown(
                f"**{len(questions)} question{'s' if len(questions) > 1 else ''} generated.** "
                "Select one answer per question, then click **Submit Quiz**."
            )
            for q in questions:
                st.markdown(
                    f'<div class="quiz-question">'
                    f'<strong>Q{q["n"]}. {q["stem"]}</strong>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                option_labels = [
                    f"{letter}. {q['options'][letter]}"
                    for letter in ("A", "B", "C", "D")
                    if letter in q["options"]
                ]
                chosen = st.radio(
                    label=f"q{q['n']}_choice",
                    options=option_labels,
                    index=None,
                    key=f"quiz_radio_{q['n']}",
                    label_visibility="collapsed",
                )
                if chosen:
                    st.session_state["quiz_answers"][q["n"]] = chosen[0]  # store "A"/"B"/…

            st.divider()
            col_sub, col_dl = st.columns([1, 1])
            with col_sub:
                if st.button("✅ Submit Quiz", key="btn_submit_quiz"):
                    st.session_state["quiz_submitted"] = True
                    st.rerun()
            with col_dl:
                st.download_button(
                    "⬇️ Download Questions",
                    data=st.session_state.get("quiz_raw", ""),
                    file_name="quiz.txt",
                    mime="text/plain",
                    key="btn_dl_quiz_pre",
                )

        else:
            # ── Results phase ─────────────────────────────────────────────
            answers = st.session_state.get("quiz_answers", {})
            correct_count = sum(
                1 for q in questions
                if answers.get(q["n"], "") == q["answer"]
            )
            total = len(questions)
            pct = int(correct_count / total * 100) if total else 0

            st.markdown(
                f'<div class="quiz-score">'
                f'<p style="font-size:1.4rem;font-weight:700;margin:0;">🎯 Score: '
                f'{correct_count} / {total} &nbsp;({pct}%)</p>'
                f'<p style="margin:0.25rem 0 0;color:#57606a;">✅ Correct: {correct_count} &nbsp;'
                f'&nbsp; ❌ Incorrect: {total - correct_count}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

            st.markdown("#### Question Review")
            for q in questions:
                user_ans = answers.get(q["n"], None)
                correct_ans = q["answer"]
                is_correct = user_ans == correct_ans

                # Question stem
                icon = "✅" if is_correct else "❌"
                st.markdown(
                    f'<div class="quiz-question">'
                    f'<strong>{icon} Q{q["n"]}. {q["stem"]}</strong>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                # All four options with highlights
                for letter in ("A", "B", "C", "D"):
                    opt_text = q["options"].get(letter, "")
                    label = f"{letter}. {opt_text}"
                    if letter == correct_ans and letter == user_ans:
                        css = "quiz-correct"
                        tag = " — Your answer (correct)"
                    elif letter == correct_ans:
                        css = "quiz-correct"
                        tag = " — Correct answer"
                    elif letter == user_ans:
                        css = "quiz-incorrect"
                        tag = " — Your answer"
                    else:
                        css = "quiz-neutral"
                        tag = ""

                    st.markdown(
                        f'<div class="{css}">{label}{tag}</div>',
                        unsafe_allow_html=True,
                    )

                # Explanation
                if q.get("explanation"):
                    st.markdown(
                        f'<div class="quiz-explanation">'
                        f'💡 {q["explanation"]}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown("")  # spacing

            st.divider()
            col_ret, col_dl2 = st.columns([1, 1])
            with col_ret:
                if st.button("🔄 Retake Quiz", key="btn_retake_quiz"):
                    st.session_state["quiz_answers"] = {}
                    st.session_state["quiz_submitted"] = False
                    st.rerun()
            with col_dl2:
                st.download_button(
                    "⬇️ Download Quiz",
                    data=st.session_state.get("quiz_raw", ""),
                    file_name="quiz.txt",
                    mime="text/plain",
                    key="btn_dl_quiz_post",
                )

# ── Tab 4: Glossary ──────────────────────────────────────────────────────────

def _parse_glossary(raw: str) -> list[tuple[str, str]]:
    """
    Parse IBM Granite's glossary output into (term, definition) pairs.

    Accepts lines in the form:
        **Term**: Definition text
        Term: Definition text      (fallback — bold markers optional)
    Skips lines that have no definition part.
    """
    import re
    entries = []
    seen_terms = set()
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        # Match  **Term**: Definition  or  Term: Definition
        m = re.match(r"^\*{0,2}(.+?)\*{0,2}\s*:\s*(.+)$", line)
        if not m:
            continue
        term = m.group(1).strip().strip("*").strip()
        definition = m.group(2).strip()
        if not term or not definition:
            continue
        term_key = term.lower()
        if term_key in seen_terms:
            continue
        seen_terms.add(term_key)
        entries.append((term, definition))
    return entries


with tab_glossary:
    st.subheader("📖 Key Terms Glossary")
    st.caption(
        "Extracts 8–10 important terms from your source content and explains each one. "
        "Language adapts to the selected proficiency level."
    )

    glossary_level = st.radio(
        "Proficiency level:",
        ["General Audience", "High School", "Undergraduate", "Postgraduate"],
        index=2,
        horizontal=True,
        key="glossary_level",
    )

    _GLOSSARY_LEVEL_HINTS = {
        "General Audience": "Plain everyday language — no prior knowledge required.",
        "High School":      "Basic academic language; technical terms briefly unpacked.",
        "Undergraduate":    "College-level explanations with appropriate terminology.",
        "Postgraduate":     "Precise, technically detailed definitions.",
    }
    st.caption(f"ℹ️ {_GLOSSARY_LEVEL_HINTS[glossary_level]}")

    if st.button("📖 Build Glossary", key="btn_glossary"):
        if not raw_text.strip():
            st.warning("Please provide some content using the sidebar.")
        else:
            raw_glossary = _safe_run(
                "Building glossary",
                generate_glossary,
                raw_text[:4000],
                glossary_level.lower(),
            )
            if raw_glossary:
                st.session_state["glossary_raw"] = raw_glossary
                st.session_state["glossary_entries"] = _parse_glossary(raw_glossary)

    # ── Render glossary cards if available ───────────────────────────────────
    if st.session_state.get("glossary_entries") is not None:
        entries = st.session_state["glossary_entries"]
        if not entries:
            st.warning(
                "No terms could be parsed from the output. "
                "Try again or check whether the source content contains clear technical terms."
            )
        else:
            st.markdown(f"**{len(entries)} term{'s' if len(entries) != 1 else ''} found.**")
            for term, definition in entries:
                st.markdown(
                    f'<div class="glossary-card">'
                    f'<div class="glossary-term">📌 {term}</div>'
                    f'<div class="glossary-def">{definition}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            st.download_button(
                "⬇️ Download Glossary",
                data=st.session_state.get("glossary_raw", ""),
                file_name="glossary.txt",
                mime="text/plain",
                key="btn_dl_glossary",
            )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="cc-footer">
        <p class="cc-footer-brand">CourseClarity AI</p>
        <p class="cc-footer-tagline">Understand More. Learn Better.</p>
        <p class="cc-footer-meta">
            Powered by IBM Granite on IBM watsonx.ai &nbsp;&middot;&nbsp;
            IBM Cloud Lite
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
