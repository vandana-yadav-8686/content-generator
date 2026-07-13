FORMAT_ID = "linkedin_post"

EXAMPLE = """
EXAMPLE FORMAT — LinkedIn post structure (use YOUR article's topic, not this one):

**AI won't replace great software developers—but it will change how they work.**

Software development is entering a new era.

AI coding assistants can now:
✅ Generate code in seconds
✅ Detect bugs faster
✅ Explain complex logic
✅ Automate documentation

These capabilities help developers spend less time on repetitive work and more time solving real business problems.

But there's an important distinction.

AI can generate code, but it doesn't truly understand product requirements, system architecture, scalability, security, or user experience. Those decisions still depend on skilled engineers.

The developers who will thrive over the next decade won't be the ones competing against AI—they'll be the ones who know how to collaborate with it.

The winning combination is:
• Strong programming fundamentals
• System design knowledge
• Critical thinking
• Effective use of AI tools

AI is becoming a powerful teammate, not a replacement.

The future belongs to developers who combine technical expertise with AI-assisted productivity.

**What's your opinion? Will AI transform software development or eventually replace most coding jobs?**

#ArtificialIntelligence #SoftwareDevelopment #Programming #Developer #Tech
"""

FORMAT_PROMPT = """Write a LinkedIn post from the article content in the brief/excerpt.

Match the EXACT structure in the example — bold hook, short paragraphs, bullet lists, question ending, hashtags.

Structure:
- Line 1: **Bold hook** — one contrarian or insight-driven sentence from the article.
- 1-2 short setup sentences.
- Bullet list with ✅ (3-5 items — specific capabilities, facts, or points from the article).
- 2-3 short paragraphs developing the main argument with article details.
- "But there's an important distinction." or similar pivot (rephrase for your topic).
- Bullet list with • (3-5 items — skills, takeaways, or what still matters).
- 1-2 closing sentences with the main thesis.
- **Bold question** inviting comments.
- 5-8 relevant hashtags on the last line.

Rules:
- 180–320 words. Use specific facts, numbers, and examples from the article.
- Short paragraphs. Lots of line breaks. Professional but readable.
- Do NOT copy the example topic — use only your article's subject matter.
- Pick ONE angle. Not a full article summary.
{example}
CONTENT BRIEF
{brief}

ARTICLE EXCERPT
{excerpt}"""
