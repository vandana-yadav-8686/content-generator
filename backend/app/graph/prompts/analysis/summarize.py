from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

from app.graph.prompts.system import SYSTEM_ANALYST

prompt = ChatPromptTemplate.from_messages(
    [
        SYSTEM_ANALYST,
        HumanMessagePromptTemplate.from_template(
            "Summarize the article in 4–6 sentences for content creators.\n"
            "Cover: topic, audience, core argument, and takeaway.\n\n"
            "ARTICLE:\n{article}"
        ),
    ]
)
