from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

from app.graph.prompts.system import SYSTEM_CREATOR

prompt = ChatPromptTemplate.from_messages(
    [
        SYSTEM_CREATOR,
        HumanMessagePromptTemplate.from_template(
            "Write a LinkedIn post.\n\n"
            "Include: bold first-line hook, short paragraphs/bullets, "
            "one question near the end, and 5–8 hashtags.\n"
            "180–320 words. Tone: {tone}\n\n"
            "SUMMARY:\n{summary}\n\n"
            "INSIGHTS (JSON):\n{insights}\n\n"
            "ARTICLE EXCERPT:\n{excerpt}"
        ),
    ]
)
