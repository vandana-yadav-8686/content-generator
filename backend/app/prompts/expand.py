EXPAND_PROMPT = """The {format_label} below is too short or sounds too generic/robotic.

Rewrite it as FINAL ready-to-publish content. Sound like a real creator talking — not an AI.

Requirements:
- Target {min_words}–{max_words} words. Do NOT exceed {max_words}.
- Use contractions. Short sentences mixed with longer ones. Fragments OK.
- Use specific facts from the brief — say them like a person would, not like a report.
- Keep the same format/structure.
- No essay language (Furthermore, Additionally, In conclusion, delve, landscape, robust).
- Output ONLY the rewritten content.

CONTENT BRIEF
{brief}

ARTICLE EXCERPT
{excerpt}

CURRENT DRAFT (replace entirely)
{draft}"""
