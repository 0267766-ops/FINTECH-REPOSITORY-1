# VALORA AI Work Log

One entry per work session. Record what the AI did, what the project partners
decided, and any reviewer flags. Keep credentials and real personal or financial
information out of this file.

## 2026-11-16 - VALORA MVP implementation

- **Goal:** Build the classroom prototype's core flow in line with the VALORA scope.
- **AI did:** Implemented account creation and sign-in, a financial profile form,
  explainable investor-profile and category-level portfolio logic, and a dashboard
  with invented activity and performance data.
- **We decided:** Continue with the limited four-step MVP and use fictional demo
  information; the application does not connect to real financial services.
- **Reviewer flags:** Four automated tests passed for the core flow, profile-rule
  boundaries, cross-user portfolio access, and login/logout with CSRF protection.

## 2026-11-17 - Render deployment setup

- **Goal:** Make the classroom demo accessible through a shareable URL.
- **AI did:** Added Gunicorn, configured the Flask factory for Render's port and
  secret-key environment variable, and documented the Render build and start
  commands.
- **We decided:** The project owner confirmed that both partners approved the
  Gunicorn dependency and its documentation.
- **Reviewer flags:** The Render service reached Live at
  <https://fintech-repository-1-1.onrender.com>. Its local SQLite storage is
  ephemeral; use fictional demo data only.

## 2026-11-17 - Text encoding and color contrast

- **Goal:** Correct garbled punctuation visible in the interface and reverse the
  page's light/dark contrast as requested.
- **AI did:** Replaced malformed text punctuation with plain-text separators and
  updated the styles to use a forest-green page background with ivory cards.
- **We decided:** Keep the requested green background and maintain high contrast on
  cards, forms, and controls.
- **Reviewer flags:** Five automated tests passed, including a homepage encoding
  and color-style check. The updated local files still need to be committed to the
  deployment repository before Render can serve these visual changes.

## Outstanding review item

- **Goal:** Confirm that all publicly accessible repository content uses fictional
  data only.
- **AI did:** Noted that the public deployment repository contains `valora.db`.
- **We decided:** Confirmation of the database contents and any required cleanup
  remains with the project partners/repository owner.
- **Reviewer flags:** Do not assume the database is safe based only on the app's
  demo-data labels. If it contains real personal information, restrict access and
  remove the file from repository history following the team's process.

## 2026-11-17 - Activity page error fix

- **Goal:** Fix the authenticated Activity page that failed while rendering.
- **AI did:** Passed the existing MXN formatting function into the Activity
  template and added a regression test for rendered simulated entries and
  per-user activity isolation.
- **We decided:** Keep Activity limited to the current simulated history; no real
  money movements or expanded marketplace features were added.
- **Reviewer flags:** The regression test reproduced the missing `format_mxn`
  template variable before the fix. Final test results are recorded after running
  the suite.

## 2026-11-17 - Approved simulated investment marketplace

- **Goal:** Add the requested portfolio catalog and company marketplace while
  staying within a safe classroom simulation.
- **AI did:** Added four illustrative portfolio categories, company search and
  sector filters, detail pages, user-specific favorites, and account/profile/favorite
  events in each user's simulated activity. Current prices, daily changes, market
  capitalization, and historical returns are explicitly unavailable; no external
  market API or financial transaction was added.
- **We decided:** Both partners approved the simulated-only scope. The exclusions
  and assumptions are recorded in `SPEC.md`.
- **Reviewer flags:** Automated coverage added for authentication, filtering,
  detail pages, favorite privacy, CSRF, and activity history. All 10 automated
  tests passed, including the existing core-flow and cross-user privacy tests.

## 2026-11-17 - Premium value-proposition page

- **Goal:** Present the proposed MXN 129/month Premium value proposition without
  changing VALORA into a live advisory or payment service.
- **AI did:** Added a public Premium concept page describing possible educational
  analysis and a future advisor component, with clear notices that no subscription,
  advisor, personalized advice, or payment is currently available.
- **We decided:** Both partners approved only this informational page. No payment
  data or additional sensitive personal information is collected.
- **Reviewer flags:** A test verifies public access, the proposed price, and the
  no-advice/no-payment disclosures. Final test results are recorded after running
  the suite.
