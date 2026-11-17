import re
import tempfile
import unittest
from pathlib import Path

from app import create_app


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
        self.assertIn(b"Growth profile", response.data)
        self.assertIn(b"Simulated", response.data)
        self.assertIn(b"not a forecast", response.data)
        self.assertIn(b"60%", response.data)

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
        self.assertIn(b"Your VALORA overview", response.data)


if __name__ == "__main__":
    unittest.main()
