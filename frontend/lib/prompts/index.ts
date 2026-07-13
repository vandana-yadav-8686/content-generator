export type PromptCategory = "global" | "format";

export interface PromptMeta {
  id: string;
  label: string;
  category: PromptCategory;
  is_customized: boolean;
  placeholders: string[];
}

export interface GlobalPrompt extends PromptMeta {
  category: "global";
  content: string;
}

export interface FormatPrompt extends PromptMeta {
  category: "format";
  format_prompt: string;
  example: string;
}

export type Prompt = GlobalPrompt | FormatPrompt;

export interface PromptListResponse {
  prompts: Prompt[];
}

export const PROMPT_SECTIONS = [
  {
    title: "Core",
    items: [{ id: "system", label: "System Prompt", file: "system.py" }],
  },
  {
    title: "Formats",
    items: [
      { id: "youtube_script", label: "YouTube", file: "youtube.py" },
      { id: "reel_script", label: "Reel", file: "reel.py" },
      { id: "linkedin_post", label: "LinkedIn", file: "linkedin.py" },
      { id: "instagram_carousel", label: "Carousel", file: "carousel.py" },
      { id: "voiceover_script", label: "Voiceover", file: "voiceover.py" },
    ],
  },
] as const;

export function isFormatPrompt(p: Prompt): p is FormatPrompt {
  return p.category === "format";
}
