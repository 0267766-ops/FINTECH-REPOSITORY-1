# VALORA Decision Log

This file records the product and implementation decisions for the FIN506
classroom prototype. It is not a substitute for partner or instructor approval.

## D-001: Keep the MVP within the four-step VALORA flow

- **Status:** Implemented
- **Decision:** Focus on account creation, a basic financial profile, an explainable
  investor profile and category-level portfolio, and a dashboard with simulated
  performance.
- **Reason:** This is the agreed working-product scope. New product features are
  deferred rather than added during deployment or visual cleanup.

## D-002: Use Flask, server-rendered pages, and SQLite

- **Status:** Implemented
- **Decision:** Build the prototype as a Flask application, render its HTML pages
  with Flask/Jinja, and store demo accounts and portfolio data in SQLite.
- **Reason:** This keeps the student MVP small and runnable without a separate
  frontend service or an external financial-data integration.
- **Limitation:** The deployed Render instance uses local SQLite storage, which is
  ephemeral. The deployment is for demonstration with fictional data, not persistent
  or real user records.

## D-003: Use transparent classroom rules for investor profiles

- **Status:** Implemented
- **Decision:** Classify a profile as Conservative when the horizon is under three
  years or the user says they would sell after a hypothetical decline; classify it
  as Growth when the horizon is at least seven years and the user might add more;
  otherwise classify it as Balanced.
- **Reason:** The rules make the prototype's result explainable and testable.
- **Limitation:** These are illustrative classroom rules, not a validated financial
  suitability assessment or a recommendation to invest.

## D-004: Keep all portfolio and performance data simulated

- **Status:** Implemented
- **Decision:** Show broad asset categories and invented sample performance only.
  Do not connect to a brokerage, execute transactions, transfer or custody money,
  run real KYC/AML, or use live market data.
- **Reason:** Real financial activity and external financial integrations are
  outside the semester MVP scope.
- **Communication:** The interface and README identify sample balances, activity,
  allocations, and performance as illustrative or simulated.

## D-005: Require authentication and isolate each user's records

- **Status:** Implemented
- **Decision:** Require sign-in for profile, portfolio, dashboard, and activity
  pages; hash passwords; use CSRF tokens for forms; and scope portfolio queries to
  the signed-in user.
- **Verification:** Automated tests cover the end-to-end flow, profile-rule
  boundaries, cross-user portfolio access, login/logout, and CSRF validation.

## D-006: Deploy the prototype on Render as a Python web service

- **Status:** Implemented
- **Decision:** Run the Flask application with Gunicorn on Render and read the
  service port and secret key from environment variables.
- **Approval:** The project owner confirmed that both partners approved adding
  Gunicorn and recording the dependency in the project log.
- **Limitation:** A successful deployment is a shareable classroom demo, not
  production readiness. Use fictional information only.

## D-007: Use forest green and ivory with readable contrast

- **Status:** Implemented
- **Decision:** Use a forest-green page background, ivory cards, and contrasting
  text and controls.
- **Reason:** The change reflects the requested reversed light/dark contrast while
  retaining readable content on cards and forms.

## Open item: Public repository database file

The public deployment repository was observed to contain `valora.db`. Its single
user record and related rows have not been verified as wholly fictional. Treat the
database as potentially exposed until the repository owner confirms its contents.
If it contains any real personal information, remove access to the repository and
follow the course team's process for removing the file from repository history.
