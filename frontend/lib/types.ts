export type ProviderId =
  | "openai"
  | "gemini"
  | "anthropic"
  | "groq"
  | "openrouter"
  | "mistral"
  | "cohere"
  | "deepseek";

export interface ModelOption {
  id: string;
  name: string;
  modality: string;
}

export interface ProviderConfig {
  provider_id: ProviderId;
  name: string;
  description: string;
  enabled: boolean;
  api_key_masked: string | null;
  has_api_key: boolean;
  model: string;
  available_models: ModelOption[];
  base_url: string | null;
}

export interface ProviderConfigUpdate {
  enabled: boolean;
  api_key?: string;
  model: string;
  base_url?: string;
}

export interface TestConnectionResponse {
  success: boolean;
  message: string;
  latency_ms?: number;
}

export interface RepurposeOutput {
  format: string;
  content: string;
}

export interface ContentBrief {
  topic: string;
  audience: string;
  main_problem?: string;
  main_solution?: string;
  key_points: string[];
  examples: string[];
  facts: string[];
  quotes?: string[];
  steps?: string[];
  tone: string;
  best_hook?: string;
  second_best_hook?: string;
}

export interface RepurposeResponse {
  provider_id: ProviderId;
  model: string;
  outputs: RepurposeOutput[];
  brief?: ContentBrief;
}

export type StreamEvent =
  | { type: "status"; message: string }
  | { type: "extraction"; data: ContentBrief }
  | { type: "format_start"; format: string; label: string }
  | { type: "chunk"; format: string; content: string }
  | { type: "format_done"; format: string; content: string }
  | { type: "done"; provider_id: string; model: string }
  | { type: "error"; message: string };

export const TONE_OPTIONS = [
  { id: "professional", label: "Professional" },
  { id: "casual", label: "Casual" },
  { id: "witty", label: "Witty" },
  { id: "educational", label: "Educational" },
  { id: "bold", label: "Bold" },
] as const;

export type ToneId = (typeof TONE_OPTIONS)[number]["id"];

export const FORMAT_LABELS: Record<string, string> = {
  youtube_script: "YouTube Script",
  reel_script: "60-Second Reel Script",
  linkedin_post: "LinkedIn Post",
  instagram_carousel: "Instagram Carousel",
  voiceover_script: "Voice-over Script",
};

export const FORMAT_DESCRIPTIONS: Record<string, string> = {
  youtube_script: "3–4 min video script — spoken, natural, not essay-style",
  reel_script: "60-second Reel with timed scenes (Hook, Scene 1-4, Ending, CTA)",
  linkedin_post: "Bold hook, bullet lists, short paragraphs, question + hashtags",
  instagram_carousel: "8-slide carousel with titles, bullets, and CTA slide",
  voiceover_script: "Natural spoken narration — no headings or stage directions",
};

export const ALL_FORMATS = [
  "youtube_script",
  "reel_script",
  "linkedin_post",
  "instagram_carousel",
  "voiceover_script",
] as const;
