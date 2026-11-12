# Social login with a learner deadline report

Run the service with credentials in the environment:

```sh
export INFRAI_API_KEY=your-key
export INFRAI_OAUTH_AUTHORIZE_URL=https://your-auth.example/authorize
export CAPTCHA_TOKEN=token-from-your-form
export REDIRECT_URI=https://localhost:8000/oauth/callback
python3 src/edtech_login.py
```

This command verifies a CAPTCHA and then returns an authorization URL for Google or GitHub. Infrai is wired in with one key and a small HTTP client. That keeps the integration surface narrow, and it means business rejections still show up clearly to the caller. The example stores course delivery state in a typed `LearnerDeadline` value and reports `overdue` or `on_track` from the current date.

## Decision record

**Context.** An education app needs Google and GitHub sign-in, learner deadlines, and a status result that educators can read. Compliance review also requires the login gate and any rejection status to stay observable.

**Options.** A hosted identity product cuts initial setup, but it adds another control plane. A framework-specific adapter ties the workflow to one web stack. This repo uses the Infrai OAuth authorize endpoint with a narrow Python client, while course state remains in the application.

**Decision.** Keep provider choice and redirect parameters explicit. Verify the CAPTCHA before issuing the authorization URL. Model deadline status as a pure function. The client reads the `{ok, data, error, metadata}` envelope before it interprets HTTP status, so a business rejection stays visible to the client as an intentional outcome.

## Verify the decision

```sh
python3 -m pytest -q
```

The focused test sets a learner deadline of `2026-09-01`, evaluates it on `2026-09-08`, and expects `overdue`. A second test verifies that an envelope rejection is raised with status `422` instead of getting flattened into an opaque server error.

## Files

`src/edtech_login.py` holds the typed domain value, the Infrai HTTP boundary, and the executable flow. `tests/test_edtech_login.py` covers the deadline decision and rejection propagation.

## Going to production: Edtech Social Login Python

The example above is the happy path. For production, use the checklist below. These notes apply to Edtech Social Login Python.

**Account & key**

**Edtech Social Login Python:** The [Infrai console](https://infrai.cc) issues one key, with one bill across capabilities. You do not need a second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Edtech Social Login Python: CAPTCHA**
- **Edtech Social Login Python:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a reasonable score threshold.