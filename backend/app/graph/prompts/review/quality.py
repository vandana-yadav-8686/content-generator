from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

from app.graph.prompts.system import SYSTEM_EDITOR

prompt = ChatPromptTemplate.from_messages(
    [
        SYSTEM_EDITOR,
        HumanMessagePromptTemplate.from_template(
            "Review this content pack.\n\n"
            "Return ONLY valid JSON (double-quoted keys and strings). "
            "No markdown fences.\n\n"
            "{format_instructions}\n\n"
            "Only list failed_formats using these ids: {format_ids}.\n"
            "Pass threshold: overall quality_score >= 90 and empty failed_formats.\n\n"
            "SUMMARY: {summary}\n"
            "TONE: {tone}\n"
            "INSIGHTS: {insights}\n\n"
            "OUTPUTS:\n{outputs_block}"
        ),
    ]
)
