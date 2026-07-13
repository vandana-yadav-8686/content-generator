FORMAT_ID = "instagram_carousel"

EXAMPLE = """
EXAMPLE FORMAT — 8-slide carousel (use YOUR article's topic, not this one):

### Slide 1
**How AI Is Transforming Software Development**
The future of coding is already here.

---

### Slide 2
**The Old Way**
Developers spent hours:
• Writing repetitive code
• Debugging manually
• Creating documentation
• Refactoring boilerplate

---

### Slide 3
**The AI-Powered Way**
AI can now:
✓ Generate code
✓ Explain complex logic
✓ Detect bugs
✓ Create documentation
✓ Speed up development

---

### Slide 4
**Does This Mean Developers Are Being Replaced?**
No.

AI is a productivity tool—not a software engineer.

---

### Slide 5
**What AI Still Can't Replace**
• Critical thinking
• System design
• Business understanding
• Architecture decisions
• Creative problem-solving

---

### Slide 6
**The Best Teams Use Both**
AI handles repetitive tasks.
Developers solve complex problems.

That's where real productivity happens.

---

### Slide 7
**Skills That Matter More Than Ever**
• Programming fundamentals
• System design
• Debugging
• AI tool proficiency

---

### Slide 8
**The Future**
Developers who learn to work with AI—not against it—will have the biggest advantage.

**Save this post and share it with someone who needs it!**
"""

FORMAT_PROMPT = """Write an Instagram carousel from the article content in the brief/excerpt.

Create exactly 8 slides matching the example format.

Format each slide EXACTLY like this:
### Slide N
**Bold Title Line**
Body text — short lines and/or bullet lists (• or ✓) using article facts.

---

Rules:
- Slide 1: Hook title + one-line teaser from the article.
- Slides 2-3: Contrast (before/after, problem/solution, or old way/new way).
- Slides 4-6: Core insights — one idea per slide, bullets welcome.
- Slide 7: Actionable takeaway or skills list from the article.
- Slide 8: Future-focused close + CTA (save, share, comment).
- Use **bold** for titles. Separate slides with --- on its own line.
- Do NOT copy the example topic — use only your article's subject matter.
- Each slide = ONE distinct point. No repeating the same idea.
{example}
CONTENT BRIEF
{brief}

ARTICLE EXCERPT
{excerpt}"""
