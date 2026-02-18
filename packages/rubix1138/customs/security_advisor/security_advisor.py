#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2025 rubix1138
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------
"""AI-powered security advisor mech tool using Claude by Anthropic.

Accepts a natural-language security question or scenario and returns a
structured JSON analysis with severity rating, detailed analysis, and
actionable recommendations. Specialised for autonomous agent and blockchain
security contexts.

Example prompt:
    "Should I expose SSH port 22 directly to the internet on my agent server?"

Example response (JSON string):
    {
        "summary": "...",
        "severity": "critical|high|medium|low|info",
        "analysis": "...",
        "recommendations": ["...", "..."],
        "risks_if_ignored": "..."
    }
"""

import json
from typing import Any, Dict, Optional, Tuple


TOOL_NAME = "security_advisor"
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 1024
MAX_PROMPT_CHARS = 3000

ALLOWED_TOOLS = [TOOL_NAME]

MechResponse = Tuple[str, Optional[str], Optional[Dict[str, Any]], Any, Any]

SYSTEM_PROMPT = """You are an expert cybersecurity advisor specialising in \
autonomous AI agent systems, blockchain infrastructure, and crypto key management. \
You help AI agents and their operators make secure architectural decisions.

Respond with a JSON object using exactly this structure:
{
  "summary": "1-2 sentence plain-language description of the security situation",
  "severity": "critical|high|medium|low|info",
  "analysis": "Detailed analysis of the risks and security considerations (2-4 paragraphs)",
  "recommendations": ["specific action 1", "specific action 2", "specific action 3"],
  "risks_if_ignored": "Concrete description of what happens if this is not addressed"
}

Severity guide:
- critical: immediate exploitation risk, private key exposure, active attack
- high: serious vulnerability requiring prompt action
- medium: significant risk requiring attention within days
- low: best-practice improvement, low immediate risk
- info: informational, no direct risk

Return ONLY the JSON object, no markdown fences or other text."""


def error_response(msg: str) -> MechResponse:
    """Return an error mech response."""
    return msg, None, None, None, None


def run(**kwargs) -> MechResponse:
    """Run the security advisor task.

    kwargs:
        prompt (str): The security question or scenario to analyse.
        api_keys (dict): API key map; expects ``{"anthropic": "<key>"}``.

    Returns:
        MechResponse: 5-tuple of (response_json, prompt, None, None, None).
    """
    prompt = kwargs.get("prompt", "")
    if isinstance(prompt, bytes):
        prompt = prompt.decode("utf-8")
    prompt = str(prompt).strip()

    if not prompt:
        return error_response("No prompt provided. Please ask a security question.")

    if len(prompt) > MAX_PROMPT_CHARS:
        prompt = prompt[:MAX_PROMPT_CHARS]

    api_keys = kwargs.get("api_keys", {})
    anthropic_key = api_keys.get("anthropic", "") if isinstance(api_keys, dict) else ""

    if not anthropic_key:
        return error_response(
            "No Anthropic API key supplied. Add 'anthropic' to the mech api_keys config."
        )

    try:
        import anthropic  # noqa: PLC0415

        client = anthropic.Anthropic(api_key=anthropic_key)
        message = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()

        # Strip markdown code fences if the model added them
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(
                lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
            ).strip()

        # Validate JSON; fall back to wrapping raw text if malformed
        try:
            json.loads(raw)
        except json.JSONDecodeError:
            raw = json.dumps(
                {
                    "summary": "Security analysis complete.",
                    "severity": "info",
                    "analysis": raw,
                    "recommendations": [],
                    "risks_if_ignored": "See analysis above.",
                }
            )

        return raw, prompt, None, None, None

    except Exception as exc:  # noqa: BLE001
        return error_response(f"Analysis failed: {exc}")
