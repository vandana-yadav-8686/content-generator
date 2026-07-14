from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

from app.graph.prompts.system import SYSTEM_CREATOR

prompt = ChatPromptTemplate.from_messages(
    [
        SYSTEM_CREATOR,
        HumanMessagePromptTemplate.from_template(
            "Write a 60-second Reel script.\n\n"
            "Structure (exact labels):\n"
            "**Hook (0–5 sec)**\n"
            "**Scene 1 (5–15 sec)**\n"
            "**Scene 2 (15–30 sec)**\n"
            "**Scene 3 (30–45 sec)**\n"
            "**Scene 4 (45–55 sec)**\n"
            "**Ending (55–60 sec)**\n"
            "**On-screen CTA:**\n\n"
            "130–220 words. Spoken narration. Tone: {tone}\n\n"
            "SUMMARY:\n{summary}\n\n"
            "INSIGHTS (JSON):\n{insights}\n\n"
            "ARTICLE EXCERPT:\n{excerpt}"
        ),
    ]
)
