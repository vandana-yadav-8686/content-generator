"""Request-scoped context for authenticated user."""

from __future__ import annotations

from contextvars import ContextVar

current_user_id: ContextVar[str | None] = ContextVar("current_user_id", default=None)


def get_user_id() -> str | None:
    return current_user_id.get()


def set_user_id(user_id: str | None) -> None:
    current_user_id.set(user_id)
