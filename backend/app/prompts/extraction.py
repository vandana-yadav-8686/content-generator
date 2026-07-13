EXTRACTION_PROMPT = """Read the article carefully. Extract SPECIFIC content for repurposing.

Return JSON only. Fill every field with real details from the article — not generic summaries.
For "key_points", each one must be a distinct, non-overlapping idea — not the same point
reworded three times.

{{
  "topic": "exact topic in 1 sentence",
  "audience": "who this is for",
  "main_problem": "specific problem from article",
  "main_solution": "specific solution from article",
  "key_points": ["specific point 1", "specific point 2", "specific point 3"],
  "examples": ["real example or case from article"],
  "facts": ["stat, number, or concrete fact from article"],
  "quotes": ["memorable phrase or insight from article"],
  "steps": ["actionable step if article has any"],
  "tone": "voice style",
  "best_hook": "opening line using a specific detail from the article",
  "second_best_hook": "a DIFFERENT specific detail, to use for a different format so hooks don't repeat"
}}

ARTICLE

{article}"""
