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
