import re
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app import create_app, initialize_database


class ValoraAppTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temporary_directory.name) / "test.sqlite"
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": str(database_path),
                "SECRET_KEY": "test-only-secret",
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_homepage_text_encoding_and_reversed_color_contrast(self):
        response = self.client.get("/")
        self.assertIn("charset=utf-8", response.content_type)
        self.assertIn(b"Clarity that compounds.", response.data)
        self.assertNotIn(b"\xc3\x82", response.data)
        self.assertNotIn(b"\xc3\xa2\xe2\x82\xac", response.data)
        self.assertIn(b"--forest: #173b32", response.data)
        self.assertIn(b"background: var(--ivory); color: var(--charcoal)", response.data)

    def test_premium_freemium_and_partnership_disclosures_are_transparent(self):
        response = self.client.get("/premium")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"financial education", response.data.lower())
        self.assertIn(b"Basic financial-health assessment", response.data)
        self.assertIn(b"Investment calculator", response.data)
        self.assertIn(b"Goal-setting tools", response.data)
        self.assertIn(b"Basic portfolio simulation", response.data)
        self.assertIn(b"$129 MXN per month", response.data)
        self.assertIn(b"No AUM fee.", response.data)
        self.assertNotIn(b"0.75%", response.data)
        self.assertIn(b"alliances with Visa and Mastercard", response.data)
        self.assertIn(b"personalized guidance to help them understand where they could invest", response.data)
        self.assertIn(b"those partners process the financial operations while VALORA provides investment guidance", response.data)
        self.assertIn(b"does not receive or custody customer funds", response.data)
        self.assertIn(b"does not provide personalized investment advice", response.data)
        self.assertIn(b"connect to Visa or Mastercard", response.data)
        self.assertNotIn(b"name=\"card_number\"", response.data)

    @staticmethod
    def csrf_token(response):
        match = re.search(rb'name="csrf_token" value="([^"]+)"', response.data)
        if not match:
            raise AssertionError("Page did not contain a CSRF token")
        return match.group(1).decode()

    def create_account(self, client, name, email):
        page = client.get("/signup")
        return client.post(
            "/signup",
            data={
                "csrf_token": self.csrf_token(page),
                "name": name,
                "email": email,
                "password": "demo-password-123",
            },
            follow_redirects=True,
        )

    def complete_profile(
        self,
        client,
        *,
        horizon="10",
        decline_response="add",
        starting_balance="50000",
    ):
        page = client.get("/profile")
        return client.post(
            "/profile",
            data={
                "csrf_token": self.csrf_token(page),
                "monthly_income": "45000",
                "starting_balance": starting_balance,
                "objective": "home",
                "horizon_years": horizon,
                "decline_response": decline_response,
                "experience": "new",
            },
            follow_redirects=True,
        )

    def test_end_to_end_signup_profile_recommendation_and_dashboard(self):
        response = self.create_account(self.client, "Demo User", "demo@example.test")
        self.assertIn(b"financial profile", response.data.lower())

        response = self.complete_profile(self.client)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your financial picture", response.data)
        self.assertIn(b"Monthly net income", response.data)
        self.assertIn(b"$45,000.00 MXN", response.data)

        response = self.client.get("/my-portfolio")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Growth profile", response.data)
        self.assertIn(b"Simulated", response.data)
        self.assertIn(b"not a forecast", response.data)
        self.assertIn(b"60%", response.data)
        self.assertIn(b"Example stocks and bond category", response.data)

        with self.app.app_context():
            from app import get_db

            user = get_db().execute("SELECT id FROM users").fetchone()
            profile = get_db().execute(
                "SELECT investor_profile FROM financial_profiles WHERE user_id = ?",
                (user["id"],),
            ).fetchone()
            portfolio = get_db().execute(
                "SELECT id FROM portfolios WHERE user_id = ?", (user["id"],)
            ).fetchone()
            products = get_db().execute(
                "SELECT allocation_percent FROM products WHERE portfolio_id = ?",
                (portfolio["id"],),
            ).fetchall()
            activity = get_db().execute(
                "SELECT is_simulated FROM transactions WHERE portfolio_id = ?",
                (portfolio["id"],),
            ).fetchall()
            performance = get_db().execute(
                "SELECT is_simulated FROM performance WHERE portfolio_id = ?",
                (portfolio["id"],),
            ).fetchall()

        self.assertEqual(profile["investor_profile"], "Growth")
        self.assertEqual(sum(row["allocation_percent"] for row in products), 100)
        self.assertTrue(all(row["is_simulated"] for row in activity))
        self.assertEqual(len(performance), 7)
        self.assertTrue(all(row["is_simulated"] for row in performance))

    def test_profile_dashboard_optional_details_and_derived_values(self):
        self.create_account(self.client, "Demo User", "demo@example.test")
        initial = self.complete_profile(self.client)
        self.assertIn(b"Not provided", initial.data)
        self.assertIn(b"Financial situation", initial.data)
        self.assertNotIn(b'name="horizon_years"', initial.data)

        self.client.post(
            "/profile/details",
            data={
                "csrf_token": self.csrf_token(initial),
                "age": "25",
                "employment_status": "Full-time",
                "occupation": "Analyst",
                "income_stability": "Stable",
                "income_sources": "Salary",
                "monthly_net_income": "45000",
                "monthly_savings": "30000",
                "monthly_expenses": "15000",
                "monthly_debt_payments": "2000",
                "liquid_savings": "45000",
                "total_liabilities": "20000",
                "total_assets": "100000",
            },
            follow_redirects=True,
        )
        response = self.client.get("/profile")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"$30,000.00 MXN", response.data)
        self.assertIn(b"$80,000.00 MXN", response.data)
        self.assertIn(b"25", response.data)
        self.assertIn(b"Full-time", response.data)
        self.assertIn(b"Analyst", response.data)
        self.assertIn(b"Salary", response.data)
        self.assertIn(b"66.7%", response.data)
        self.assertIn(b"33.3%", response.data)
        self.assertIn(b"4.4%", response.data)
        self.assertIn(b"3.0 months", response.data)
        self.assertIn(b"$28,000.00 MXN", response.data)
        self.assertIn(b"Income vs. expenses", response.data)
        self.assertIn(b"Financial distribution", response.data)

    def test_overview_profile_and_portfolio_are_distinct_and_user_scoped(self):
        self.create_account(self.client, "First User", "first@example.test")
        self.complete_profile(self.client, horizon="1", decline_response="add")

        overview = self.client.get("/dashboard")
        profile = self.client.get("/profile")
        portfolio = self.client.get("/my-portfolio")
        self.assertIn(b"Welcome back", overview.data)
        self.assertNotIn(b"name=\"monthly_income\"", overview.data)
        self.assertIn(b"Your financial picture", profile.data)
        self.assertNotIn(b'name="horizon_years"', profile.data)
        self.assertIn(b"Example stocks and bond category", portfolio.data)
        self.assertIn(b"Illustrative government bond category", portfolio.data)
        self.assertIn(b"The Coca-Cola Company", portfolio.data)
        self.assertIn(b"not actual holdings", portfolio.data)

        second_client = self.app.test_client()
        self.create_account(second_client, "Second User", "second@example.test")
        self.complete_profile(second_client, horizon="10", decline_response="add")
        second_profile = second_client.get("/profile")
        self.assertIn(b"Not provided", second_profile.data)
        self.assertNotIn(b"Analyst", second_profile.data)
        self.assertIn(b"NVIDIA Corporation", second_client.get("/my-portfolio").data)

    def test_profile_dashboard_shows_deficit_without_fabricating_net_worth(self):
        self.create_account(self.client, "Demo User", "demo@example.test")
        initial = self.complete_profile(self.client)
        self.client.post(
            "/profile/details",
            data={
                "csrf_token": self.csrf_token(initial),
                "monthly_net_income": "45000",
                "monthly_savings": "0",
                "monthly_expenses": "60000",
                "monthly_debt_payments": "0",
                "total_assets": "100000",
            },
        )

        response = self.client.get("/profile")
        self.assertIn(b"$-15,000.00 MXN", response.data)
        self.assertIn(b"Shortfall", response.data)
        self.assertIn(b"Enter net income, expenses, debt payments, and savings", response.data)
        self.assertIn(b"Net worth</div><div class=\"metric-value\">Not provided", response.data)

    def test_financial_indicator_formulas_and_missing_value_handling(self):
        self.create_account(self.client, "Demo User", "demo@example.test")
        initial = self.complete_profile(self.client)
        response = self.client.post(
            "/profile/details",
            data={
                "csrf_token": self.csrf_token(initial),
                "monthly_net_income": "50000",
                "monthly_savings": "10000",
                "monthly_expenses": "25000",
                "monthly_debt_payments": "5000",
                "liquid_savings": "75000",
                "total_assets": "200000",
                "total_liabilities": "60000",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"20.0%", response.data)  # Savings rate
        self.assertIn(b"10.0%", response.data)  # Debt-to-income
        self.assertIn(b"50.0%", response.data)  # Expense ratio
        self.assertIn(b"$140,000.00 MXN", response.data)  # Net worth
        self.assertIn(b"3.0 months", response.data)  # Emergency fund
        self.assertIn(b"$20,000.00 MXN", response.data)  # Disposable income
        self.assertIn(b"Unallocated: 20.0%", response.data)

        update_page = self.client.get("/profile")
        response = self.client.post(
            "/profile/details",
            data={
                "csrf_token": self.csrf_token(update_page),
                "monthly_net_income": "50000",
                "monthly_expenses": "25000",
            },
            follow_redirects=True,
        )
        self.assertIn(b"Savings Rate</div><div class=\"metric-value\">Not provided", response.data)
        self.assertIn(b"Debt-to-Income</div><div class=\"metric-value\">Not provided", response.data)
        self.assertIn(b"Net Worth</div><div class=\"metric-value\">Not provided", response.data)
        self.assertIn(b"Emergency Fund</div><div class=\"metric-value\">Not provided", response.data)
        self.assertIn(b"Disposable Income</div><div class=\"metric-value\">Not provided", response.data)

    def test_existing_database_is_migrated_for_new_financial_inputs(self):
        database_path = Path(self.temporary_directory.name) / "legacy.sqlite"
        connection = sqlite3.connect(database_path)
        connection.executescript(
            """
            CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
            CREATE TABLE financial_details (
                user_id INTEGER PRIMARY KEY,
                monthly_expenses_cents INTEGER,
                total_debt_cents INTEGER,
                total_assets_cents INTEGER,
                age INTEGER,
                employment_status TEXT,
                occupation TEXT,
                income_stability TEXT,
                income_sources TEXT,
                updated_at TEXT
            );
            INSERT INTO users (id, name) VALUES (1, 'Demo');
            INSERT INTO financial_details (user_id, total_debt_cents)
                VALUES (1, 2000000);
            """
        )
        connection.close()

        initialize_database(str(database_path))

        connection = sqlite3.connect(database_path)
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(financial_details)")
        }
        legacy_debt = connection.execute(
            "SELECT total_debt_cents FROM financial_details WHERE user_id = 1"
        ).fetchone()[0]
        connection.close()
        self.assertIn("monthly_net_income_cents", columns)
        self.assertIn("monthly_debt_payments_cents", columns)
        self.assertIn("liquid_savings_cents", columns)
        self.assertIn("total_liabilities_cents", columns)
        self.assertEqual(legacy_debt, 2000000)

    def test_profile_rule_boundaries(self):
        cases = (
            ("1", "add", b"Conservative profile"),
            ("5", "wait", b"Balanced profile"),
            ("7", "add", b"Growth profile"),
            ("10", "sell", b"Conservative profile"),
        )
        for index, (horizon, response, expected) in enumerate(cases):
            with self.subTest(horizon=horizon, response=response):
                client = self.app.test_client()
                self.create_account(client, f"User {index}", f"user{index}@example.test")
                result = self.complete_profile(
                    client, horizon=horizon, decline_response=response
                )
                self.assertIn(expected, result.data)

    def test_users_cannot_access_another_users_portfolio(self):
        self.create_account(self.client, "First User", "first@example.test")
        self.complete_profile(self.client)
        with self.app.app_context():
            from app import get_db

            first_portfolio_id = get_db().execute(
                "SELECT id FROM portfolios"
            ).fetchone()["id"]

        second_client = self.app.test_client()
        self.create_account(second_client, "Second User", "second@example.test")
        response = second_client.get(f"/portfolio/{first_portfolio_id}")
        self.assertEqual(response.status_code, 404)

    def test_activity_page_renders_and_shows_only_current_users_entries(self):
        first_client = self.client
        self.create_account(first_client, "First User", "first@example.test")
        self.complete_profile(first_client, starting_balance="50000")

        first_activity = first_client.get("/activity")
        self.assertEqual(first_activity.status_code, 200)
        self.assertIn(b"Illustrative starting amount", first_activity.data)
        self.assertIn(b"$50,000.00 MXN", first_activity.data)
        self.assertIn(b"Simulated", first_activity.data)

        second_client = self.app.test_client()
        self.create_account(second_client, "Second User", "second@example.test")
        self.complete_profile(second_client, starting_balance="12345")
        second_activity = second_client.get("/activity")
        self.assertEqual(second_activity.status_code, 200)
        self.assertIn(b"$12,345.00 MXN", second_activity.data)
        self.assertNotIn(b"$50,000.00 MXN", second_activity.data)

    def test_marketplace_requires_login_and_displays_only_non_live_market_data(self):
        response = self.client.get("/marketplace")
        self.assertEqual(response.status_code, 302)

        self.create_account(self.client, "Demo User", "demo@example.test")
        self.complete_profile(self.client)
        response = self.client.get("/marketplace")
        self.assertEqual(response.status_code, 200)
        for portfolio_name in (b"Conservative", b"Moderate", b"Aggressive", b"International"):
            self.assertIn(portfolio_name, response.data)
        self.assertIn(b"Current price:</strong> Not available", response.data)
        self.assertIn(b"Historical performance</strong><br>Not available", response.data)
        self.assertIn(b"Apple Inc.", response.data)

        response = self.client.get("/marketplace?q=NVDA&sector=Semiconductors")
        self.assertIn(b"NVIDIA Corporation", response.data)
        self.assertNotIn(b"Apple Inc.", response.data)
        response = self.client.get("/marketplace?q=NVDA&sector=Financials")
        self.assertIn(b"No companies match those filters.", response.data)

    def test_portfolio_and_company_detail_pages(self):
        self.create_account(self.client, "Demo User", "demo@example.test")
        self.complete_profile(self.client)

        portfolio = self.client.get("/portfolios/moderate")
        self.assertEqual(portfolio.status_code, 200)
        self.assertIn(b"Asset allocation", portfolio.data)
        self.assertIn(b"Historical performance is not available", portfolio.data)
        self.assertEqual(self.client.get("/portfolios/not-a-portfolio").status_code, 404)

        company = self.client.get("/companies/AAPL")
        self.assertEqual(company.status_code, 200)
        self.assertIn(b"Apple Inc.", company.data)
        self.assertIn(b"Market data</div><h3>Not connected</h3>", company.data)
        self.assertEqual(self.client.get("/companies/UNKNOWN").status_code, 404)

    def test_favorites_are_private_and_logged_as_simulated_activity(self):
        first_client = self.client
        self.create_account(first_client, "First User", "first@example.test")
        self.complete_profile(first_client)

        marketplace = first_client.get("/marketplace")
        first_client.post(
            "/favorites/AAPL",
            data={
                "csrf_token": self.csrf_token(marketplace),
                "next": "/favorites",
            },
            follow_redirects=True,
        )
        first_favorites = first_client.get("/favorites")
        self.assertIn(b"Apple Inc.", first_favorites.data)
        first_activity = first_client.get("/activity")
        self.assertIn(b"Added AAPL to saved favorites (simulated)", first_activity.data)

        second_client = self.app.test_client()
        self.create_account(second_client, "Second User", "second@example.test")
        self.complete_profile(second_client)
        self.assertNotIn(b"Apple Inc.", second_client.get("/favorites").data)
        self.assertNotIn(
            b"Added AAPL to saved favorites",
            second_client.get("/activity").data,
        )

        detail = first_client.get("/companies/AAPL")
        remove = first_client.post(
            "/favorites/AAPL",
            data={
                "csrf_token": self.csrf_token(detail),
                "next": "/favorites",
            },
            follow_redirects=True,
        )
        self.assertIn(b"You have no saved companies yet.", remove.data)
        self.assertIn(
            b"Removed AAPL from saved favorites (simulated)",
            first_client.get("/activity").data,
        )

    def test_favorite_changes_require_valid_csrf(self):
        self.create_account(self.client, "Demo User", "demo@example.test")
        self.complete_profile(self.client)
        response = self.client.post("/favorites/AAPL", data={"csrf_token": "invalid"})
        self.assertEqual(response.status_code, 400)

    def test_login_logout_and_csrf_protection(self):
        self.create_account(self.client, "Demo User", "demo@example.test")
        self.complete_profile(self.client)
        logout_page = self.client.get("/dashboard")
        token = self.csrf_token(logout_page)
        response = self.client.post("/logout", data={"csrf_token": "invalid"})
        self.assertEqual(response.status_code, 400)
        response = self.client.post("/logout", data={"csrf_token": token})
        self.assertEqual(response.status_code, 302)

        login_page = self.client.get("/login")
        response = self.client.post(
            "/login",
            data={
                "csrf_token": self.csrf_token(login_page),
                "email": "demo@example.test",
                "password": "demo-password-123",
            },
            follow_redirects=True,
        )
        self.assertIn(b"Welcome back", response.data)


if __name__ == "__main__":
    unittest.main()
