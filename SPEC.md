# VALORA Scope Addendum: Simulated Investment Marketplace

This addendum records the marketplace scope approved by both project partners on
2026-11-17. It supplements the original FIN506 project scope; it does not authorize
real financial services or integrations.

## Investment portfolio catalog

- Add Conservative, Moderate, Aggressive, and International illustrative portfolio
  categories.
- Show a plainly labeled classroom risk description, asset allocation, illustrative
  minimum amount in MXN, and illustrative investment horizon for each category.
- Do not invent historical performance or present simulated performance factors as
  historical returns. Display that historical performance is unavailable because
  no market-data provider is connected.
- Provide a detail page for each portfolio with the same assumptions and disclaimers.

## Company directory

- Provide a searchable and sector-filterable directory of example publicly traded
  companies with company name, ticker symbol, and sector.
- Company names and tickers identify examples only. Do not display a current share
  price, daily percentage change, market capitalization, news, or historical price
  without a verified, approved market-data integration. Show those values as
  unavailable instead.
- Provide a company detail page. Do not present the directory as an offer or
  recommendation to buy securities.

## Account features and activity

- Require authentication for the marketplace, details, and favorites.
- Store favorites by the signed-in user and prevent users from viewing or changing
  another user's favorites.
- Record fictional account/profile setup and favorite changes in the user's
  simulated activity history. Label these as simulated actions, not transactions.

## Profile dashboard and navigation

- Keep Overview, My Portfolio, and My Profile as distinct pages; do not render the
  same questionnaire or portfolio view for all three navigation items.
- Preserve the existing questionnaire fields and response logic. After completion,
  My Profile presents the saved answers in a responsive financial dashboard.
- Show the existing monthly-income answer as entered; do not call it net income
  because the questionnaire does not specify net versus gross.
- Allow users to optionally add missing expenses, debt, total assets, age,
  employment status, occupation, income stability, and income sources in a separate
  supplementary form. These optional details do not alter the questionnaire.
- Collect net monthly income, monthly savings, monthly debt payments, liquid savings,
  monthly expenses, total assets, and total liabilities in the optional details
  form for the requested indicators. The questionnaire's approximate monthly income
  is not assumed to be net income.
- Show unavailable values as "Not provided". Calculate monthly savings only when
  provided; calculate the indicators only when all their required values are
  provided. Do not infer missing data.
- Use these exact calculations: Savings Rate = monthly savings / net income × 100;
  Debt-to-Income = monthly debt payments / net income × 100; Expense Ratio =
  monthly expenses / net income × 100; Net Worth = total assets − total liabilities;
  Emergency Fund = liquid savings / monthly expenses (months covered); and
  Disposable Income = net income − expenses − monthly debt payments.
- Visualize income versus expenses, monthly cash flow, income distribution, and
  savings rate using the entered values only. Explain calculations and handle
  expenses above income without depicting a positive savings amount.
- My Portfolio may show profile-specific examples from the Investments catalog,
  including sample stock names and an illustrative government-bond category.
  Percentages are simulated allocations only; do not imply actual positions,
  executed orders, exact bonds, or personalized investment recommendations.

## Premium subscription concept page

- Establish VALORA as a trustworthy financial-education brand, rather than only
  promoting an app.
- Present the free tier as a proposed freemium strategy containing financial
  education, a basic financial-health assessment, an investment calculator,
  goal-setting tools, and a basic portfolio simulation. Do not imply that tools not
  implemented in the prototype are already available.
- Present conversion to a future paid personalized investment-guidance service as
  a business proposal, not a currently available service. Explain that VALORA helps
  customers consider where to invest, but does not receive or custody their money.
- Show proposed pricing as MXN 129 per month. Do not charge or propose an
  assets-under-management (AUM) fee.
- State that VALORA has alliances with Visa and Mastercard for financial operations
  as confirmed by the project owner. Describe the proposed division of roles:
  Visa/Mastercard partners process financial operations and VALORA provides
  investment guidance. Make clear that this model is not integrated into the
  classroom demo and that the app does not currently process transactions or
  provide personalized investment advice.
- Clearly state that VALORA does not currently manage assets, provide a live
  advisor or personalized investment advice, connect a bank or brokerage, accept
  subscription payments, or enroll customers.
- Label the Premium page as a business-model proposal. Any actual asset management,
  advisory service, banking/brokerage integration, or billing requires separate
  operational, legal, regulatory, and partner approval.
- Do not collect payment details, financial documents, or additional sensitive
  personal information on this page.

## Explicit exclusions

- No Alpha Vantage, Finnhub, Financial Modeling Prep, or other external data API.
- No live or fabricated market prices, daily changes, capitalization, or historical
  returns.
- No bank, brokerage, or payment network is technically integrated into the
  classroom prototype; the app does not administer funds.
- No real trades, deposits, withdrawals, payments, transfers, or custody of money.
- No real KYC/AML, credit-bureau checks, or personalized financial advice.
- No active Premium subscription, human-advisor service, or subscription payment.
- The MXN 129/month subscription is a proposed pricing assumption and is not
  currently charged. No AUM fee is proposed.
- All amounts, allocations, minimums, and horizons in the added catalog are
  classroom assumptions. Use fictional user data only.

## Approval record

Both project partners approved this simulated-only scope in the project conversation
on 2026-11-17. The approval is recorded in `DECISIONS.md` and `BITACORA.md`.

The project owner later confirmed that the Visa and Mastercard alliances are
formal and authorized to announce. The proposed model assigns financial-operation
processing to these partners and investment guidance to VALORA. Neither partner
is integrated into the classroom prototype.
