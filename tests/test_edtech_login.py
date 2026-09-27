from datetime import date

import pytest

from src.edtech_login import InfraiClient, InfraiError, LearnerDeadline, report_deadline


def test_deadline_report_marks_learner_overdue():
    item = LearnerDeadline("learner-7", "course-python", date(2026, 9, 1))
    assert report_deadline(item, date(2026, 9, 8))["state"] == "overdue"


def test_client_surfaces_business_envelope_error(monkeypatch):
    client = InfraiClient(base_url="https://example.test", api_key="env-key")

    def rejected(*args, **kwargs):
        raise InfraiError("REQUEST_REJECTED", {"message": "captcha rejected"}, 422)

    monkeypatch.setattr(client, "_request", rejected)
    with pytest.raises(InfraiError) as caught:
        client.verify_captcha("widget-7", "token")
    assert caught.value.status == 422


def test_verify_captcha_sends_required_widget_record_id(monkeypatch):
    client = InfraiClient(base_url="https://example.test", api_key="env-key")
    requests = []
    monkeypatch.setattr(client, "_request", lambda method, path, body: requests.append((method, path, body)))

    client.verify_captcha("widget-7", "token")

    assert requests == [("POST", "/v1/captcha/verify", {
        "widget_record_id": "widget-7", "token": "token", "action": "social_login",
    })]
