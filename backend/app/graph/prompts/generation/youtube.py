from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

from app.graph.prompts.system import SYSTEM_CREATOR

prompt = ChatPromptTemplate.from_messages(
    [
        SYSTEM_CREATOR,
        HumanMessagePromptTemplate.from_template(
            """
Write a YouTube script using the article below.

Goal:
Teach the viewer, don't summarize the article.

Structure (use exactly):

🎬 HOOK

📚 SECTION 1

⚡ SECTION 2

🚀 SECTION 3

🎯 OUTRO / CTA

Requirements:

• 280–380 words.
• Sound like a real YouTuber talking to the camera.
• Use simple, conversational English.
• Keep paragraphs to 2–4 short sentences.
• No Markdown (#, ##, **, bullets, tables, or code blocks).
• Output only the script.

Writing Style:

• Explain concepts instead of listing them.
• For each major concept, explain:
  - What it is
  - Why it matters
  - One simple real-world example
• Use analogies when helpful.
• Connect sections naturally.
• Teach from beginner to intermediate.

Avoid:

• "This article explains..."
• "This guide covers..."
• Documentation-style writing.
• Copying the article structure.
• Filler or repeated ideas.

Good Example:

Instead of:
"Variables store values."

Say:
"Think of a variable like a labeled box. If you're building a shopping app, you might store the customer's name in a variable so you can reuse it anywhere in your code."

Before finishing, make sure the script:
• Sounds natural.
• Is technically accurate.
• Is engaging.
• Includes practical examples.
• Is ready for voice-over without editing.

Tone:
{tone}

SUMMARY:
{summary}

INSIGHTS:
{insights}

ARTICLE:
{excerpt}
"""
        ),
    ]
)