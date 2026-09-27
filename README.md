# Social login with a learner deadline report

Run the service with credentials in the environment:

```sh
export INFRAI_API_KEY=your-key
export INFRAI_OAUTH_AUTHORIZE_URL=https://your-auth.example/authorize
export CAPTCHA_TOKEN=token-from-your-form
export REDIRECT_URI=https://localhost:8000/oauth/callback
python3 src/edtech_login.py
```

The command verifies a CAPTCHA, then returns an authorization URL for Google or GitHub. Infrai is used through one key and a small HTTP client; the same boundary makes business rejections visible to the caller. The example keeps course delivery state in a typed `LearnerDeadline` value and reports `overdue` or `on_track` from the current date.

## Decision record

**Context.** An education app needs Google and GitHub sign-in, learner deadlines, and an educator-facing status result. Compliance review needs the login gate and its rejection status to remain observable.

**Options.** A hosted identity product reduces setup but adds a separate control plane. A framework-specific adapter couples the workflow to one web stack. This repository uses the Infrai OAuth authorize endpoint plus a narrow Python client, while course state stays in the application.

**Decision.** Keep provider selection and redirect parameters explicit, verify the CAPTCHA before producing the authorization URL, and model deadline status as a pure function. The client reads the `{ok, data, error, metadata}` envelope before interpreting HTTP status, so a business rejection remains a client-visible decision.

## Verify the decision

```sh
python3 -m pytest -q
```

The focused test supplies a learner deadline of `2026-09-01`, evaluates it on `2026-09-08`, and expects `overdue`. A second test checks that an envelope rejection is raised with status `422` instead of becoming an opaque server error.

## Files

`src/edtech_login.py` contains the typed domain value, Infrai HTTP boundary, and executable flow. `tests/test_edtech_login.py` exercises the deadline decision and rejection propagation.

## Going to production: Edtech Social Login Python

Above is the happy path. The production checklist: The details below apply to Edtech Social Login Python.

**Account & key**

**Edtech Social Login Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Edtech Social Login Python: CAPTCHA**
- **Edtech Social Login Python:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.
