import json
import copy
from pathlib import Path

from app.config import settings
from app.prompts.defaults import (
    ALL_FORMAT_IDS,
    FORMAT_LABELS,
    build_defaults,
)


class PromptStore:
    """Loads default prompts from app/prompts/*.py and merges user overrides from JSON."""

    def __init__(self) -> None:
        self._defaults = build_defaults()
        self._path = Path(settings.database_path).parent / "custom_prompts.json"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._overrides: dict = self._load_overrides()

    def _load_overrides(self) -> dict:
        if not self._path.exists():
            return {}
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_overrides(self) -> None:
        self._path.write_text(
            json.dumps(self._overrides, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _active(self) -> dict:
        active = copy.deepcopy(self._defaults)
        if "system" in self._overrides:
            active["system"] = self._overrides["system"]
        if "extraction" in self._overrides:
            active["extraction"] = self._overrides["extraction"]
        if "batch" in self._overrides:
            active["batch"] = self._overrides["batch"]
        if "expand" in self._overrides:
            active["expand"] = self._overrides["expand"]
        for fmt_id, fields in self._overrides.get("formats", {}).items():
            if fmt_id not in active["formats"]:
                continue
            if "format_prompt" in fields:
                active["formats"][fmt_id]["format_prompt"] = fields["format_prompt"]
            if "example" in fields:
                active["formats"][fmt_id]["example"] = fields["example"]
        return active

    def get_system_prompt(self) -> str:
        return self._active()["system"]

    def get_extraction_prompt(self) -> str:
        return self._active()["extraction"]

    def get_batch_prompt(self) -> str:
        return self._active()["batch"]

    def get_expand_prompt(self) -> str:
        return self._active()["expand"]

    def get_format_prompt(self, fmt: str) -> str:
        return self._active()["formats"][fmt]["format_prompt"]

    def get_format_example(self, fmt: str) -> str:
        return self._active()["formats"][fmt]["example"]

    def get_format_prompts(self) -> dict[str, str]:
        return {fmt: self.get_format_prompt(fmt) for fmt in ALL_FORMAT_IDS}

    def get_format_examples(self) -> dict[str, str]:
        return {fmt: self.get_format_example(fmt) for fmt in ALL_FORMAT_IDS}

    def is_customized(self, key: str) -> bool:
        if key in ("system", "extraction", "batch", "expand"):
            return key in self._overrides
        if key in ALL_FORMAT_IDS:
            fmt_overrides = self._overrides.get("formats", {}).get(key, {})
            return bool(fmt_overrides)
        return False

    def list_prompts(self) -> list[dict]:
        active = self._active()
        items: list[dict] = [
            {
                "id": "system",
                "label": "System Prompt",
                "category": "global",
                "content": active["system"],
                "is_customized": self.is_customized("system"),
                "placeholders": [],
            },
            {
                "id": "extraction",
                "label": "Article Extraction",
                "category": "global",
                "content": active["extraction"],
                "is_customized": self.is_customized("extraction"),
                "placeholders": ["{article}"],
            },
            {
                "id": "batch",
                "label": "Batch Generation",
                "category": "global",
                "content": active["batch"],
                "is_customized": self.is_customized("batch"),
                "placeholders": [
                    "{brief}",
                    "{excerpt}",
                    "{example_youtube}",
                    "{example_reel}",
                    "{example_linkedin}",
                    "{example_carousel}",
                    "{example_voiceover}",
                ],
            },
            {
                "id": "expand",
                "label": "Expand / Retry",
                "category": "global",
                "content": active["expand"],
                "is_customized": self.is_customized("expand"),
                "placeholders": ["{format_label}", "{min_words}", "{brief}", "{excerpt}", "{draft}"],
            },
        ]
        for fmt_id in ALL_FORMAT_IDS:
            fmt = active["formats"][fmt_id]
            items.append({
                "id": fmt_id,
                "label": FORMAT_LABELS.get(fmt_id, fmt_id),
                "category": "format",
                "format_prompt": fmt["format_prompt"],
                "example": fmt["example"],
                "is_customized": self.is_customized(fmt_id),
                "placeholders": ["{brief}", "{excerpt}", "{example}"],
            })
        return items

    def get_prompt(self, prompt_id: str) -> dict | None:
        for item in self.list_prompts():
            if item["id"] == prompt_id:
                return item
        return None

    def update_prompt(self, prompt_id: str, data: dict) -> dict:
        if prompt_id in ("system", "extraction", "batch", "expand"):
            content = data.get("content", "").strip()
            if not content:
                raise ValueError("Prompt content cannot be empty")
            self._overrides[prompt_id] = content
            self._save_overrides()
            return self.get_prompt(prompt_id)  # type: ignore[return-value]

        if prompt_id in ALL_FORMAT_IDS:
            fmt_overrides = self._overrides.setdefault("formats", {}).setdefault(prompt_id, {})
            if "format_prompt" in data:
                fmt_overrides["format_prompt"] = data["format_prompt"].strip()
            if "example" in data:
                fmt_overrides["example"] = data["example"].strip()
            if not fmt_overrides.get("format_prompt") and not fmt_overrides.get("example"):
                raise ValueError("At least one of format_prompt or example is required")
            self._save_overrides()
            return self.get_prompt(prompt_id)  # type: ignore[return-value]

        raise ValueError(f"Unknown prompt id: {prompt_id}")

    def reset_prompt(self, prompt_id: str | None = None) -> None:
        if prompt_id is None:
            self._overrides = {}
            self._save_overrides()
            return

        if prompt_id in ("system", "extraction", "batch", "expand"):
            self._overrides.pop(prompt_id, None)
        elif prompt_id in ALL_FORMAT_IDS:
            formats = self._overrides.get("formats", {})
            formats.pop(prompt_id, None)
            if not formats:
                self._overrides.pop("formats", None)
            else:
                self._overrides["formats"] = formats
        else:
            raise ValueError(f"Unknown prompt id: {prompt_id}")
        self._save_overrides()

    def get_defaults_for(self, prompt_id: str) -> dict:
        defaults = self._defaults
        if prompt_id in ("system", "extraction", "batch", "expand"):
            return {"id": prompt_id, "content": defaults[prompt_id]}
        if prompt_id in ALL_FORMAT_IDS:
            fmt = defaults["formats"][prompt_id]
            return {
                "id": prompt_id,
                "format_prompt": fmt["format_prompt"],
                "example": fmt["example"],
            }
        raise ValueError(f"Unknown prompt id: {prompt_id}")


prompt_store = PromptStore()
