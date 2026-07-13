from app.prompts import batch, carousel, expand, extraction, linkedin, reel, system, voiceover, youtube

FORMAT_MODULES = {
    youtube.FORMAT_ID: youtube,
    reel.FORMAT_ID: reel,
    linkedin.FORMAT_ID: linkedin,
    carousel.FORMAT_ID: carousel,
    voiceover.FORMAT_ID: voiceover,
}

ALL_FORMAT_IDS = list(FORMAT_MODULES.keys())

FORMAT_LABELS = {
    "youtube_script": "YouTube Script",
    "reel_script": "60-Second Reel Script",
    "linkedin_post": "LinkedIn Post",
    "instagram_carousel": "Instagram Carousel",
    "voiceover_script": "Voice-over Script",
}

MIN_WORD_COUNTS = {
    "youtube_script": 200,
    "reel_script": 120,
    "linkedin_post": 150,
    "instagram_carousel": 120,
    "voiceover_script": 110,
}

MAX_WORD_COUNTS = {
    "youtube_script": 400,
    "reel_script": 250,
    "linkedin_post": 350,
    "instagram_carousel": 450,
    "voiceover_script": 210,
}

FORMAT_MAX_TOKENS = {
    "youtube_script": 800,
    "reel_script": 500,
    "linkedin_post": 550,
    "instagram_carousel": 900,
    "voiceover_script": 450,
}

OPEN_WEIGHT_MAX_TOKENS = {
    "youtube_script": 650,
    "reel_script": 420,
    "linkedin_post": 480,
    "instagram_carousel": 750,
    "voiceover_script": 380,
}

MAX_ARTICLE_CHARS = 12000
EXCERPT_CHARS = 3000

OPEN_WEIGHT_PROVIDERS = frozenset({"groq", "openrouter", "mistral", "deepseek"})
FREE_TIER_PROVIDERS = frozenset({"gemini"})

GENERIC_PHRASES = [
    "game-changer",
    "worth a try",
    "you should try",
    "you should definitely",
    "consider using",
    "it's worth checking",
    "level the playing field",
    "here's a script",
    "in this video",
    "let's dive in",
    "growing concerns about",
    "it's no wonder",
    "join the millions",
    "represents much more than",
    "is looking brighter than ever",
    "now is the time",
    "is experiencing one of the biggest transformations",
    "is undergoing a transformation",
    "furthermore",
    "additionally",
    "moreover",
    "in conclusion",
    "it's important to note",
    "it's worth mentioning",
    "in today's fast-paced",
    "in today's digital",
    "navigate the landscape",
    "delve into",
    "robust solution",
    "comprehensive guide",
    "utilize",
    "facilitate",
    "streamline your",
    "at the end of the day",
    "when it comes to",
]

BANNED_PHRASE_REPLACEMENTS: list[tuple[str, str]] = [
    (r"\bgame-changer\b", ""),
    (r"\bworth a try\b", ""),
    (r"\byou should (?:definitely )?try\b", ""),
    (r"\bconsider using\b", ""),
    (r"\bleverage\b", "use"),
    (r"\bunlock\b", "open up"),
    (r"\butilize\b", "use"),
    (r"\bfacilitate\b", "help"),
    (r"\bnavigate the landscape\b", "work in this space"),
    (r"\bdelve into\b", "look at"),
    (r"\bFurthermore,?\s*", ""),
    (r"\bAdditionally,?\s*", ""),
    (r"\bMoreover,?\s*", ""),
    (r"\bIn conclusion,?\s*", ""),
    (r"\bIt's important to note that\s*", ""),
    (r"Here's a script[^.]*\.\s*", ""),
    (r"In this video,?\s*", ""),
    (r"Let's dive in\.?\s*", ""),
]


def build_defaults() -> dict:
    """Return the full default prompt bundle used to seed the store."""
    formats: dict[str, dict[str, str]] = {}
    for fmt_id, module in FORMAT_MODULES.items():
        formats[fmt_id] = {
            "format_prompt": module.FORMAT_PROMPT,
            "example": module.EXAMPLE,
        }

    return {
        "system": system.SYSTEM_PROMPT,
        "extraction": extraction.EXTRACTION_PROMPT,
        "batch": batch.BATCH_PROMPT,
        "expand": expand.EXPAND_PROMPT,
        "formats": formats,
    }
