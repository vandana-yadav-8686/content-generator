from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

from app.graph.prompts.system import SYSTEM_ANALYST

INSIGHTS_JSON_SHAPE = """{
  "topic": "one sentence topic",
  "audience": "primary audience",
  "key_points": ["point 1", "point 2", "point 3"],
  "facts": ["concrete fact from article"],
  "statistics": [],
  "quotes": [],
  "cta": "",
  "keywords": []
}"""

prompt = ChatPromptTemplate.from_messages(
    [
        SYSTEM_ANALYST,
        HumanMessagePromptTemplate.from_template(
            "Extract structured insights from the article.\n\n"
            "Reply with ONE JSON object only. Use double quotes for all keys and strings.\n"
            "No markdown, no code fences, no explanation before or after the JSON.\n\n"
            "Required JSON shape (fill every field from the article; use [] if empty):\n"
            f"{INSIGHTS_JSON_SHAPE}\n\n"
            "SUMMARY:\n{summary}\n\n"
            "ARTICLE:\n{article}"
        ),
    ]
)

retry_prompt = ChatPromptTemplate.from_messages(
    [
        SYSTEM_ANALYST,
        HumanMessagePromptTemplate.from_template(
            "Your previous reply was not valid JSON. Try again.\n\n"
            "Return ONLY one JSON object. Double-quoted keys and strings. No markdown.\n\n"
            "Shape:\n"
            f"{INSIGHTS_JSON_SHAPE}\n\n"
            "SUMMARY:\n{summary}\n\n"
            "ARTICLE:\n{article}"
        ),
    ]
)
