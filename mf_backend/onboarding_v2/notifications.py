from __future__ import annotations

import json
import logging

import requests
from django.conf import settings


logger = logging.getLogger(__name__)


def notify_saas_alert(title: str, payload: dict | None = None):
    """
    Send a lightweight Slack notification for SAAS webhook/task events.
    Expects SAAS_SLACK_WEBHOOK_URL in settings/env.
    """
    url = getattr(settings, "SAAS_SLACK_WEBHOOK_URL", None)
    if not url:
        return

    # Keep payload concise and safe to log
    body = {
        "text": title,
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*{title}*"}},
        ],
    }
    if payload:
        body["blocks"].append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "```" + json.dumps(payload, indent=2) + "```"},
            }
        )

    try:
        requests.post(url, json=body, timeout=5)
    except Exception:
        logger.exception("Failed to notify Slack for SAAS alert")


def notify_app_step_error(application_id: str, step: str, error: str, payload: dict | None = None):
    """
    Notify a single message for a failing step in the application lifecycle.
    """
    title = f"Onboarding step failed | app={application_id} step={step}"
    notify_saas_alert(title, {"application_id": application_id, "step": step, "error": error, "payload": payload})
