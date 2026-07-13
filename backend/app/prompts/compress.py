COMPRESS_PROMPT = """The {format_label} below is too long and reads like an article, not like a creator talking.

Tighten it. Cut filler. Keep the human voice.

Requirements:
- Target {max_words} words or fewer. Cut ruthlessly — every line must earn its place.
- Keep contractions, short punchy lines, and the same format/structure.
- Remove essay language, redundant points, and anything that sounds written not spoken.
- Do NOT lose the specific facts and examples — just say them in fewer words.
- Output ONLY the shortened content.

CONTENT BRIEF
{brief}

CURRENT DRAFT (too long — tighten it)
{draft}"""
