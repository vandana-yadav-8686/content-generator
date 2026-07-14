"""
LangGraph generation prompts — used by the product Generate button.

Pipeline: validate → summarize → insights → tone → parallel formats →
quality review → MongoDB (via POST /api/repurpose/stream and /api/generate-content).
"""
