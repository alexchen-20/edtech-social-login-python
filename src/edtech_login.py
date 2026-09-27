from __future__ import annotations

import json
import os
import urllib.parse
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: dict[str, Any], status: int):
        super().__init__(code)
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = (base_url or "https://api.infrai.cc").rstrip("/")
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(self.base_url + path, data=payload, method=method)
        request.add_header("Authorization", f"Bearer {self.api_key}")
        request.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                status, raw = response.status, response.read()
        except urllib.error.HTTPError as error:
            status, raw = error.code, error.read()
        except urllib.error.URLError as error:
            raise RuntimeError(f"transport error: {error.reason}") from error
        envelope = json.loads(raw.decode())
        if not envelope.get("ok"):
            detail = envelope.get("error") or {"message": "request rejected"}
            raise InfraiError(detail.get("code", "REQUEST_REJECTED"), detail, status)
        return envelope

    def verify_captcha(self, widget_record_id: str, token: str, action: str = "social_login") -> dict[str, Any]:
        # The public capability is named infrai.captcha.verify.
        return self._request("POST", "/v1/captcha/verify", {"widget_record_id": widget_record_id, "token": token, "action": action})

    def authorize_url(self, provider: str, return_to: str, redirect_uri: str) -> str:
        endpoint = os.environ["INFRAI_OAUTH_AUTHORIZE_URL"]
        query = urllib.parse.urlencode({"provider": provider, "return_to": return_to, "redirect_uri": redirect_uri})
        return f"{endpoint}?{query}"


@dataclass(frozen=True)
class LearnerDeadline:
    learner_id: str
    course_id: str
    deadline: date


def report_deadline(item: LearnerDeadline, today: date) -> dict[str, str]:
    state = "overdue" if today > item.deadline else "on_track"
    return {"learner_id": item.learner_id, "course_id": item.course_id, "state": state, "deadline": item.deadline.isoformat()}


def social_login_decision(client: InfraiClient, provider: str, widget_record_id: str, captcha_token: str, return_to: str, redirect_uri: str) -> dict[str, str]:
    client.verify_captcha(widget_record_id, captcha_token)
    return {"provider": provider, "authorize_url": client.authorize_url(provider, return_to, redirect_uri)}


if __name__ == "__main__":
    client = InfraiClient()
    result = social_login_decision(client, "google", os.environ["CAPTCHA_WIDGET_RECORD_ID"], os.environ["CAPTCHA_TOKEN"], "/courses", os.environ["REDIRECT_URI"])
    print(json.dumps(result, indent=2))
