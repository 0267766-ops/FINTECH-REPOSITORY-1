# VALORA

VALORA is a FIN506 WealthTech MVP prototype for young professionals in Mexico. It
demonstrates the core account-to-dashboard flow and the approved simulated
investment marketplace described in `SPEC.md`.

## Run locally

From this folder, install the approved dependencies and start the app:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). If you use another Python
environment, install `requirements.txt` there instead. The app creates `valora.db` in
this folder the first time it runs; that file contains local demo data.

## Demo

Create a fictional account on the welcome page, then complete the financial profile
using invented answers. No shared or seeded password is stored in this repository.
For a Growth-profile demo, select a horizon of at least 7 years and “I might consider
adding more.” The dashboard shows an illustrative portfolio and invented example
history. Use a fictional email/password and share any instructor test credentials
separately through the course submission process—not in this repository.

## What the prototype does—and does not do

- Uses SQLite and invented, local-only demo data.
- Applies transparent classroom rules: Conservative for a horizon under 3 years or
  choosing to sell after a hypothetical decline; Growth for a horizon of at least 7
  years and choosing to consider adding; Balanced otherwise.
- Shows only broad illustrative asset categories, not named financial products.
- Labels all sample balances, activity and performance as simulated.
- Uses a forest-green page background with ivory cards and high-contrast text.
- Includes an authenticated investment catalog with Conservative, Moderate,
  Aggressive, and International illustrative portfolio categories, plus a searchable
  and filterable example company directory, detail pages, and private favorites.
- Includes a public Premium value-proposition concept page proposing MXN 129/month.
  It is informational only: no Premium service, advisor, personalized advice, or
  payment/subscription enrollment is available.
- Shows no live or fabricated stock prices, daily changes, market capitalization, or
  historical returns. These data are marked unavailable because no market-data API
  is connected.
- Records fictional account/profile setup and favorite changes in per-user
  simulated activity. These are not money movements or trades.
- Does not perform real KYC/AML, connect to a brokerage, execute investments, transfer
  money, custody assets, use live market data, or guarantee returns.
- Does not make claims about Mexican financial regulation.

The allocations and performance factors are prototype assumptions approved for this
classroom demo, not financial advice or forecasts. The app is the working-product
deliverable only; the final pitch, market-validation evidence, five-year financial
model and valuation remain separate project deliverables.

## Deploy on Render

Create a **Python Web Service** connected to the repository containing these files
(do not select Docker). Set:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn --bind 0.0.0.0:$PORT "app:create_app()"`
- Environment variable: `SECRET_KEY` set to a long, random value

The free service's local SQLite file is ephemeral and may be lost when the service
restarts or is redeployed. Use fictional demo data only; this prototype is not
configured for persistent or real financial data.

The marketplace's allocations, minimum amounts, and investment horizons are
classroom assumptions, not offers or financial advice. No bank, brokerage, or
market-data provider is connected.

The Premium page is a business-pitch concept only. Its proposed price and benefits
do not represent an active product or service.

## Check

Run the end-to-end, marketplace, activity-history, profile-rule, cross-user access,
and CSRF tests:

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_app.py
```

## Project records

- [Approved scope addendum](./SPEC.md)
- [Decision log](./DECISIONS.md)
- [AI work log](./BITACORA.md)
