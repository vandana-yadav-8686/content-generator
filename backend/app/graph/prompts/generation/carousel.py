# from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

# from app.graph.prompts.system import SYSTEM_CREATOR

# prompt = ChatPromptTemplate.from_messages(
#     [
#         SYSTEM_CREATOR,
#         HumanMessagePromptTemplate.from_template(
#             "Write an Instagram carousel as 8 slides.\n\n"
#             "Format each slide:\n"
#             "### Slide N\nTitle\n- bullet\n- bullet\n---\n\n"
#             "Slide 8 must be a CTA. End with a short Caption.\n"
#             "Tone: {tone}\n\n"
#             "SUMMARY:\n{summary}\n\n"
#             "INSIGHTS (JSON):\n{insights}\n\n"
#             "ARTICLE EXCERPT:\n{excerpt}"
#         ),
#     ]
# )

from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

from app.graph.prompts.system import SYSTEM_CREATOR

prompt = ChatPromptTemplate.from_messages(
    [
        SYSTEM_CREATOR,
        HumanMessagePromptTemplate.from_template(
            """
You are a world-class Instagram content creator with 15+ years of experience creating viral educational carousel posts.

Your writing should feel like it was written by a successful creator—not by AI.

GOAL

Create an Instagram carousel that people want to:
- stop scrolling for
- read until the end
- save
- share
- comment on

WRITING STYLE

Write naturally.

Use everyday language.

Sound confident but friendly.

Every slide should feel like a conversation.

Use curiosity.

Use emotion.

Use short paragraphs.

Vary sentence length.

Occasionally use emojis naturally (not on every line).

Avoid robotic patterns.

Avoid repeating sentence structures.

Never sound like ChatGPT.

DO NOT USE

- **Slide 1**
- Slide 1
- Page 1
- Section 1
- ###
- ---
- ***
- Markdown formatting
- Numbering
- Roman numerals
- AI phrases
- Corporate language
- Generic motivational quotes

Instead, separate each carousel card with one blank line only.

FORMAT

For every carousel card:

Start with an engaging headline.

Examples:

💡 Nobody talks about this...

🔥 Here's why most people fail...

❤️ Your body wants this every day

⚡ Stop doing this

🏃 The easiest habit you'll ever build

✨ Small habit. Massive results.

After the headline,

write 2–4 short bullet points.

Bullets should be conversational.

Each bullet should be under 20 words.

Do NOT make every headline follow the same pattern.

Some can be questions.

Some can be bold statements.

Some can create curiosity.

The last card should naturally invite engagement.

Examples:

👇 Which one are you starting today?

❤️ Save this for later.

📤 Send this to someone who needs it.

After the carousel write:

Caption:

Write a creator-style caption.

Not AI.

40–100 words.

End with one question.

Then include 5–8 relevant hashtags.

Tone:
{tone}

Summary:
{summary}

Insights:
{insights}

Article:
{excerpt}

## Input

Tone:
{tone}

Summary:
{summary}

Insights (JSON):
{insights}

Article:
{excerpt}
"""
        ),
    ]
)