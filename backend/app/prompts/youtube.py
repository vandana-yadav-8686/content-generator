FORMAT_ID = "youtube_script"

EXAMPLE = """
EXAMPLE — sounds like someone talking to camera, not reading an article:

HOOK
Okay so — 18 days. That's how long I was waiting to get paid on average. Three clients?
Always over 30.

SECTION 1
And here's the thing nobody talks about. Every day that invoice sits there, you're basically
loaning money to someone else's business. I ran the numbers on mine — two grand a month.
Just sitting in their accounts.

SECTION 2
So I got tired of chasing people. Built three things: one invoice template, a reminder on
day 3, another on day 7. That's it. No spreadsheets. No "just following up" at midnight.

SECTION 3
Month later? Average payment time — 4 days. Same clients. Same rates. Only thing that
changed was I stopped doing it manually.

OUTRO
If you're still invoicing from memory — that's your leak. Fix that one thing this week.
"""

FORMAT_PROMPT = """Write a YouTube script that sounds like a creator talking to camera — NOT an
article being read aloud.

Pick ONE angle from the brief. Do not cover the whole article.

LENGTH: 280–380 words total. Hard stop at 380. Shorter is better if it still lands.

Structure (exact headers):
HOOK
SECTION 1
SECTION 2
SECTION 3
OUTRO

Rules:
- HOOK: start mid-thought or with a number — like you already started talking before they hit play.
- Each section = 2-4 sentences max. One idea per section.
- Use contractions. Vary rhythm — some lines should be 3 words, others 15.
- No transition words (Furthermore, Additionally, In conclusion).
- Sound spoken, not written. Read it aloud in your head before outputting.
{example}
CONTENT BRIEF
{brief}

ARTICLE EXCERPT
{excerpt}"""
