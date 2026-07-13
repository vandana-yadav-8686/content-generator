BATCH_PROMPT = """Write ALL 5 pieces of FINAL content using the brief and excerpt.

Sound like a real creator in every piece — spoken, punchy, human. NOT like articles or AI summaries.

Each piece must use a DIFFERENT hook and angle. Never reuse opening lines across formats.

Return JSON only:
{{
  "youtube_script": "",
  "reel_script": "",
  "linkedin_post": "",
  "instagram_carousel": "",
  "voiceover_script": ""
}}

RULES FOR ALL:
- Write like a person talks. Contractions. Short sentences. Fragments OK.
- NO essay language (Furthermore, Additionally, delve, landscape, robust, comprehensive).
- Pick one angle per piece — never summarize the whole article.
- Stay within word limits. Shorter beats longer.
- Banned: "game-changer", "Here's a script", "In this video", "Let's dive in".

youtube_script: 280-380 words. Headers: HOOK, SECTION 1, SECTION 2, SECTION 3, OUTRO.
reel_script: 130-220 words. Timed scenes: Hook (0-5s), Scene 1-4, Ending (55-60s), On-screen CTA.
linkedin_post: 180-320 words. Bold hook, bullet lists, question ending, 5-8 hashtags.
instagram_carousel: 8 slides. Format: ### Slide N, **title**, body/bullets, --- between slides.
voiceover_script: 140-200 words. Spoken narration only, no headings.

YOUTUBE EXAMPLE:
{example_youtube}

REEL EXAMPLE:
{example_reel}

LINKEDIN EXAMPLE:
{example_linkedin}

CAROUSEL EXAMPLE:
{example_carousel}

VOICEOVER EXAMPLE:
{example_voiceover}

CONTENT BRIEF
{brief}

ARTICLE EXCERPT
{excerpt}"""
