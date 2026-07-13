FORMAT_ID = "voiceover_script"

EXAMPLE = """
EXAMPLE — sounds like someone talking, not narrating a documentary:

You know that feeling? Work's done, invoice sent, and then — nothing. No payment. No reply.
Just silence. For a lot of freelancers that's every single month. I tracked mine for 90
days. Eighteen days average. Three clients always over thirty. That delay? About two grand
a month I couldn't use. So I stopped winging it. One template. Two auto-reminders. One
dashboard. Thirty days later — four-day average. Same clients. Same rates. I just stopped
doing everything manually.
"""

FORMAT_PROMPT = """Write a voice-over script that sounds like natural spoken narration.

ONE story thread from the brief. Don't cover everything in the article.

LENGTH: 140–200 words. Hard stop at 200.

Rules:
- No headings. No stage directions. No [pause] tags.
- Write exactly what the narrator says — contractions, fragments, mid-thought starts.
- Mix short punchy lines ("One template. Two reminders.") with longer ones.
- Sound like a person telling a story, not reading a report.
- Cut anything that sounds written rather than spoken.
{example}
CONTENT BRIEF
{brief}

ARTICLE EXCERPT
{excerpt}"""
