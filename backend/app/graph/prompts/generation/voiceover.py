from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

from app.graph.prompts.system import SYSTEM_CREATOR

prompt = ChatPromptTemplate.from_messages(
    [
        SYSTEM_CREATOR,
        HumanMessagePromptTemplate.from_template(
            "Write a voice-over script for AI narration.\n\n"
            "Rules: conversational; mark short pauses with …; "
            "no headings or stage directions; 110–200 words.\n"
            "Tone: {tone}\n\n"
            "SUMMARY:\n{summary}\n\n"
            "INSIGHTS (JSON):\n{insights}\n\n"
            "ARTICLE EXCERPT:\n{excerpt}"
        ),
    ]
)
