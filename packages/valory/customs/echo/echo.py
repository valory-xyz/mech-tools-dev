#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2021-2025 Valory AG
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
"""This module contains the echo tool."""

from typing import Optional, Dict, Any, Tuple

ALLOWED_TOOLS = ["echo"]


def error_response(msg: str) -> Tuple[Optional[str], Optional[Dict[str, Any]], Any, Any]:
    """Return an error mech response."""
    return msg, None, None, None


def run(**kwargs) -> Tuple[Optional[str], Optional[Dict[str, Any]], Any, Any]:
    """Run the task"""

    # Get all the required parameters
    prompt = kwargs.get("prompt", None)

    # Check all the parameters
    if prompt is None:
        return error_response("No prompt has been given.")

    response = "Echo: " + prompt

    return response, prompt, None, None, None
