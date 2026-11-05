"""
agent.py
--------
Core simplification agent logic for CourseClarity AI.
Builds targeted prompts for IBM Granite and processes the responses
into structured, student-friendly output.
"""

from granite_client import generate_text


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

_SIMPLIFY_PROMPT = """\
You are an expert educational content simplifier working with AICTE (All India Council for Technical Education).
Your goal is to help first-generation learners and students from non-English-medium backgrounds understand complex academic material.

TASK: Simplify the following course content so that a Class 10 student can understand it clearly.

GUIDELINES:
- Replace technical jargon with simple, everyday words (but keep essential terms with brief explanations).
- Break long paragraphs into short, numbered points.
- Use simple sentence structures (subject-verb-object).
- Add one real-life analogy or example for each key concept.
- Avoid Latin phrases, passive voice, and abbreviations without explanation.
- Output in clear, plain English suitable for rural / non-English-medium students.

---
ORIGINAL CONTENT:
{content}
---

SIMPLIFIED VERSION:
"""

# Each entry: (persona description, language instruction)
_SUMMARY_LEVEL_GUIDE = {
    "general audience": (
        "a general audience with no technical background",
        "Use plain everyday language. Avoid jargon entirely. You may use a simple comparison to "
        "clarify an idea only if that comparison is directly supported by the source content — "
        "do not invent examples. Write as if explaining to a curious friend who has never studied this subject."
    ),
    "high school": (
        "a high-school student",
        "Use basic academic language. Introduce technical terms only when necessary and briefly "
        "explain each one in parentheses. Keep sentences short and clear."
    ),
    "undergraduate": (
        "an undergraduate university student",
        "Use appropriate college-level terminology. Explain how concepts relate to each other. "
        "You may assume familiarity with foundational ideas in the field."
    ),
    "postgraduate": (
        "a postgraduate researcher or advanced student",
        "Use precise academic and technical language. Discuss relationships, mechanisms, "
        "and implications at depth. Reference theoretical frameworks where relevant."
    ),
}

_SUMMARY_PROMPT = """\
You are an expert study assistant summarising academic content for {audience}.

STRICT RULES — follow all of these without exception:
1. Base the summary ONLY on the SOURCE CONTENT provided below. Do not add facts, career advice, \
assumptions, new applications, or any information not explicitly stated in the source.
2. Do NOT introduce topics, examples, or use-cases that are not mentioned in the source content.
3. Do NOT describe AI, machine learning, or any technology as "thinking", "understanding", \
"feeling", or acting like a human, unless the source content itself uses that language.
4. Do NOT produce a glossary. Do NOT define terms one by one.
5. Do NOT repeat the same idea in multiple takeaways.
6. If the source content is too short or unclear to summarise meaningfully, write: \
"The provided content is insufficient for a complete summary." — then stop.
7. {language_instruction}

OUTPUT FORMAT — output exactly these two sections with these exact headings, nothing else:

### Overview
One concise paragraph (3–5 sentences) that:
- States the main topic of the content
- Explains how the key concepts in the content relate to each other
- Conveys why these ideas matter, based solely on what the content says

### Key Takeaways
A list of 3–5 bullet points where each point:
- Communicates one important idea or relationship from the content
- Is a complete sentence (not a heading or a term definition)
- Uses language and terminology appropriate for {audience}

---
SOURCE CONTENT:
{content}
---

SUMMARY:
"""


def _get_level_context(level: str) -> tuple[str, str]:
    """Return (audience description, language instruction) for the given level key."""
    return _SUMMARY_LEVEL_GUIDE.get(
        level.lower(),
        _SUMMARY_LEVEL_GUIDE["undergraduate"],   # safe fallback
    )

_QUIZ_LEVEL_GUIDE = {
    "general audience": (
        "people with no technical background",
        "Use simple, everyday language. Avoid unexplained jargon. "
        "Test broad understanding of the ideas rather than memorised terms."
    ),
    "high school": (
        "high-school students",
        "Use clear academic language. Test key facts and basic concept understanding. "
        "Incorrect options should be plausible but obviously wrong on reflection."
    ),
    "undergraduate": (
        "undergraduate university students",
        "Use appropriate college-level terminology. Test conceptual understanding "
        "and the ability to apply or distinguish between ideas."
    ),
    "postgraduate": (
        "postgraduate researchers or advanced students",
        "Use precise technical language. Test deep understanding of mechanisms, "
        "relationships, and implications. Distractors should require careful analysis to rule out."
    ),
}

_QUIZ_PROMPT = """\
You are an exam preparation assistant creating a quiz for {audience}.

STRICT RULES:
1. Generate exactly {count} multiple-choice questions based ONLY on the SOURCE CONTENT below.
2. Do NOT invent facts, applications, or topics not present in the source.
3. Each question must have exactly four options: A, B, C, D.
4. Exactly one option must be correct per question.
5. Make incorrect options plausible but unambiguously wrong based on the content.
6. Do NOT repeat questions or reword the same question.
7. {language_instruction}

OUTPUT FORMAT — repeat this block exactly {count} times, numbered Q1 through Q{count}:

Q<n>. <question stem>
A. <option>
B. <option>
C. <option>
D. <option>
Answer: <letter>
Explanation: <one sentence explaining why the correct answer is right, based on the source content>

---
SOURCE CONTENT:
{content}
---

QUIZ:
"""


def _get_quiz_level_context(level: str) -> tuple[str, str]:
    """Return (audience description, language instruction) for the given quiz level."""
    return _QUIZ_LEVEL_GUIDE.get(
        level.lower(),
        _QUIZ_LEVEL_GUIDE["undergraduate"],
    )

_GLOSSARY_LEVEL_GUIDE = {
    "general audience": (
        "a general audience with no technical background",
        "Write definitions in plain everyday language. Avoid all jargon. "
        "Use a short, familiar comparison only if it is directly supported by the source. "
        "Each definition must be one clear sentence."
    ),
    "high school": (
        "high-school students",
        "Use basic academic language. If the term itself is technical, briefly unpack it. "
        "Each definition must be one or two clear sentences."
    ),
    "undergraduate": (
        "undergraduate university students",
        "Use appropriate college-level terminology. "
        "Explain the term's meaning and its role in the subject area covered by the content. "
        "Each definition may be one to three sentences."
    ),
    "postgraduate": (
        "postgraduate researchers or advanced students",
        "Use precise academic and technical language. "
        "Include the term's formal meaning, any important nuances, and its significance "
        "within the context of the source content. Each definition may be two to four sentences."
    ),
}

_GLOSSARY_PROMPT = """\
You are a vocabulary assistant building a glossary for {audience}.

STRICT RULES:
1. Extract exactly 8–10 of the most important technical terms from the SOURCE CONTENT below.
   Do NOT invent terms that are absent from the source.
2. Every term MUST have a definition. Never output a term without its definition.
3. Base every definition ONLY on what the source content says. Do not add unsupported \
information, unrelated examples, or external facts.
4. If the source content does not provide enough context to define a term accurately, \
write: "Definition not sufficiently supported by the provided content."
5. Do NOT duplicate terms. Each term must appear exactly once.
6. {language_instruction}

OUTPUT FORMAT — one entry per line, exactly like this (no blank lines between entries):
**<Term>**: <Definition>

---
SOURCE CONTENT:
{content}
---

GLOSSARY:
"""


def _get_glossary_level_context(level: str) -> tuple[str, str]:
    """Return (audience description, language instruction) for the given glossary level."""
    return _GLOSSARY_LEVEL_GUIDE.get(
        level.lower(),
        _GLOSSARY_LEVEL_GUIDE["undergraduate"],
    )

_TRANSLATE_PROMPT = """\
You are a multilingual educational assistant supporting AICTE students.

TASK: Translate the following simplified academic content into {language}.
Keep technical terms in English but add the {language} translation in parentheses.
Keep the same bullet-point structure.

---
CONTENT:
{content}
---

TRANSLATION ({language}):
"""


# ---------------------------------------------------------------------------
# Public agent functions
# ---------------------------------------------------------------------------

def simplify_content(raw_text: str) -> str:
    """Simplify complex academic content using IBM Granite."""
    prompt = _SIMPLIFY_PROMPT.format(content=raw_text.strip())
    return generate_text(prompt)


def summarize_content(raw_text: str, level: str = "undergraduate") -> str:
    """
    Generate a structured summary: an Overview paragraph + 3–5 Key Takeaways.

    Args:
        raw_text: The source academic content to summarise.
        level:    Reader proficiency — one of:
                  "general audience", "high school", "undergraduate", "postgraduate".
                  Defaults to "undergraduate".
    """
    audience, language_instruction = _get_level_context(level)
    prompt = _SUMMARY_PROMPT.format(
        content=raw_text.strip(),
        audience=audience,
        language_instruction=language_instruction,
    )
    return generate_text(prompt)


def generate_quiz(raw_text: str, count: int = 5, level: str = "undergraduate") -> str:
    """
    Generate MCQs with one correct answer and an explanation per question.

    Args:
        raw_text: Source academic content.
        count:    Number of questions to generate (5, 10, 15, or 20).
        level:    Difficulty — "general audience", "high school",
                  "undergraduate", or "postgraduate".

    Returns:
        Raw text output from IBM Granite containing Q<n>/options/Answer/Explanation blocks.
    """
    audience, language_instruction = _get_quiz_level_context(level)
    prompt = _QUIZ_PROMPT.format(
        content=raw_text.strip(),
        count=count,
        audience=audience,
        language_instruction=language_instruction,
    )
    return generate_text(prompt)


def generate_glossary(raw_text: str, level: str = "undergraduate") -> str:
    """
    Extract 8–10 important terms from the source content and define each one.

    Args:
        raw_text: The source academic content.
        level:    Reader proficiency — "general audience", "high school",
                  "undergraduate", or "postgraduate". Defaults to "undergraduate".

    Returns:
        Raw text from IBM Granite with one **Term**: Definition entry per line.
    """
    audience, language_instruction = _get_glossary_level_context(level)
    prompt = _GLOSSARY_PROMPT.format(
        content=raw_text.strip(),
        audience=audience,
        language_instruction=language_instruction,
    )
    return generate_text(prompt)


def translate_content(simplified_text: str, language: str) -> str:
    """Translate simplified content into a regional language."""
    prompt = _TRANSLATE_PROMPT.format(content=simplified_text.strip(), language=language)
    return generate_text(prompt)
