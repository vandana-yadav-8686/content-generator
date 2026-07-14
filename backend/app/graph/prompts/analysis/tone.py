from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

from app.graph.prompts.system import SYSTEM_ANALYST

prompt = ChatPromptTemplate.from_messages(
    [
        SYSTEM_ANALYST,
        HumanMessagePromptTemplate.from_template(
            "Classify the dominant tone of this article.\n\n"
            "Return ONLY valid JSON (double-quoted keys and strings). "
            "No markdown fences.\n\n"
            "{format_instructions}\n\n"
            "ARTICLE:\n{article}"
        ),
    ]
)
