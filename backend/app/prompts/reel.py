FORMAT_ID = "reel_script"

EXAMPLE = """
EXAMPLE FORMAT — timed scenes for a 60-second Reel (use YOUR article's topic, not this one):

**Hook (0–5 sec)**
"AI isn't replacing software developers... it's replacing the way they work."

**Scene 1 (5–15 sec)**
Just a few years ago, developers spent hours writing boilerplate code, debugging simple issues, and documenting everything manually.

**Scene 2 (15–30 sec)**
Today, AI tools can generate code, explain complex functions, detect bugs, and even create documentation in seconds. What once took hours can now take minutes.

**Scene 3 (30–45 sec)**
But here's the catch: AI doesn't understand your business goals, system architecture, or user needs. It can suggest solutions—but developers still make the important decisions.

**Scene 4 (45–55 sec)**
The most successful engineering teams don't replace developers with AI. They combine AI-powered automation with human creativity, problem-solving, and technical expertise.

**Ending (55–60 sec)**
The future belongs to developers who know how to code and how to use AI effectively. Learn the fundamentals, master AI tools, and you'll stay ahead.

**On-screen CTA:**
"Do you think AI will replace developers? Share your thoughts below."
"""

FORMAT_PROMPT = """Write a 60-second Reel script using the article content in the brief/excerpt.

Match the EXACT structure below — timed scenes, spoken narration in each block.

Structure (use these exact section labels):
**Hook (0–5 sec)**
(one punchy opening line — quote it)

**Scene 1 (5–15 sec)**
(2-3 sentences — set up the problem or "before" state from the article)

**Scene 2 (15–30 sec)**
(2-3 sentences — the shift, solution, or "today" state with specific facts)

**Scene 3 (30–45 sec)**
(2-3 sentences — the nuance, catch, or limitation from the article)

**Scene 4 (45–55 sec)**
(2-3 sentences — the reframe or how successful people/teams approach it)

**Ending (55–60 sec)**
(1-2 sentences — clear takeaway tied to the article)

**On-screen CTA:**
(one engagement question or action for viewers)

Rules:
- 130–220 words total. Every scene must contain specific facts from the article.
- Write what the creator SAYS on camera — natural speech, contractions OK.
- Do NOT copy the example topic — use only your article's subject matter.
- Pick ONE angle from the article. Do not summarize every section of the source.
{example}
CONTENT BRIEF
{brief}

ARTICLE EXCERPT
{excerpt}"""
