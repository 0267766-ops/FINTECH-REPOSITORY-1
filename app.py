from __future__ import annotations

import hmac
import os
import secrets
import sqlite3
from decimal import Decimal, InvalidOperation
from functools import wraps
from pathlib import Path
from typing import Any, Callable

from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template_string,
    request,
    session,
    url_for,
)
from markupsafe import Markup
from werkzeug.security import check_password_hash, generate_password_hash


ROOT = Path(__file__).resolve().parent
DEFAULT_DATABASE = ROOT / "valora.db"

PROFILES = {
    "Conservative": {
        "title": "A steadier starting point",
        "summary": "Emphasizes stability for a nearer goal or a lower comfort with declines.",
        "allocation": [
            ("Fixed-income category", 70, "A larger illustrative share for stability."),
            ("Diversified equity category", 20, "A smaller illustrative share for long-term growth."),
            ("Liquidity category", 10, "An illustrative share kept accessible."),
        ],
    },
    "Balanced": {
        "title": "A balanced starting point",
        "summary": "Balances stability and growth for a middle horizon and a measured response to declines.",
        "allocation": [
            ("Fixed-income category", 50, "An illustrative foundation for stability."),
            ("Diversified equity category", 40, "An illustrative share for long-term growth."),
            ("Liquidity category", 10, "An illustrative share kept accessible."),
        ],
    },
    "Growth": {
        "title": "A long-term growth starting point",
        "summary": "Uses a longer horizon and willingness to accept simulated declines as profile signals.",
        "allocation": [
            ("Fixed-income category", 30, "An illustrative share for stability."),
            ("Diversified equity category", 60, "A larger illustrative share for long-term growth."),
            ("Liquidity category", 10, "An illustrative share kept accessible."),
        ],
    },
}

# These fixed, invented factors provide a visual demo series; they are not market data,
# a forecast, or a claim about what any investment may earn.
SIMULATED_MONTHLY_FACTORS = (
    Decimal("1.000"),
    Decimal("0.997"),
    Decimal("1.004"),
    Decimal("1.002"),
    Decimal("1.009"),
    Decimal("1.006"),
    Decimal("1.012"),
)


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS financial_profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    monthly_income_cents INTEGER NOT NULL,
    starting_balance_cents INTEGER NOT NULL,
    objective TEXT NOT NULL,
    horizon_years INTEGER NOT NULL,
    decline_response TEXT NOT NULL,
    experience TEXT NOT NULL,
    investor_profile TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS portfolios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    investor_profile TEXT NOT NULL,
    starting_balance_cents INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    allocation_percent INTEGER NOT NULL,
    rationale TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    is_simulated INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    month_index INTEGER NOT NULL,
    value_cents INTEGER NOT NULL,
    is_simulated INTEGER NOT NULL DEFAULT 1,
    UNIQUE (portfolio_id, month_index)
);
"""


BASE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#173b32">
  <title>{{ page_title }} | VALORA</title>
  <style>
    :root {
      color-scheme: light;
      --forest: #173b32;
      --ivory: #f3f0e7;
      --champagne: #c7b58a;
      --sage: #a7b5a2;
      --charcoal: #252a27;
      --white: #fff;
      --muted: #65716a;
      --line: #dedfd6;
      --danger: #8d392f;
      --radius: 16px;
      font-family: Inter, "Segoe UI", Arial, sans-serif;
      color: var(--ivory);
      background: var(--forest);
    }
    * { box-sizing: border-box; }
    body { margin: 0; min-width: 320px; background: var(--forest); color: var(--ivory); }
    a { color: inherit; }
    button, input, select { font: inherit; }
    .shell { width: min(1120px, calc(100% - 40px)); margin: 0 auto; }
    .topbar { background: var(--forest); border-bottom: 1px solid #456157; }
    .nav { min-height: 76px; display: flex; align-items: center; justify-content: space-between; gap: 24px; }
    .wordmark { color: var(--ivory); font-weight: 750; letter-spacing: .19em; text-decoration: none; }
    .nav-links { display: flex; align-items: center; flex-wrap: wrap; gap: 22px; }
    .nav-links a, .nav-links button { color: var(--ivory); background: none; border: 0; padding: 8px 0; text-decoration: none; font-size: .9rem; cursor: pointer; }
    .nav-links a:hover, .nav-links button:hover { color: var(--champagne); text-decoration: underline; text-underline-offset: 5px; }
    .nav-links .nav-cta { padding: 11px 16px; border-radius: 999px; background: var(--ivory); color: var(--forest); text-decoration: none; }
    main { min-height: calc(100vh - 150px); padding: 42px 0 64px; }
    .hero { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(240px, .8fr); gap: 50px; align-items: center; padding: 68px 0 78px; }
    .eyebrow { color: #d6c69d; text-transform: uppercase; letter-spacing: .14em; font-size: .72rem; font-weight: 700; }
    h1, .editorial { font-family: "DM Serif Display", Georgia, serif; font-weight: 400; }
    h1 { font-size: clamp(2.65rem, 5vw, 4.65rem); line-height: 1.04; letter-spacing: -.035em; margin: 14px 0 20px; color: var(--ivory); }
    h2 { font-size: clamp(1.35rem, 2.8vw, 2rem); color: var(--ivory); margin: 0 0 14px; }
    h3 { color: var(--forest); margin: 0 0 10px; }
    p { line-height: 1.7; }
    .lead { max-width: 600px; color: #d6dfd8; font-size: 1.05rem; }
    .hero-panel, .card, .form-card { background: var(--ivory); color: var(--charcoal); }
    .hero-panel { border: 1px solid var(--line); border-radius: 22px; padding: 26px; box-shadow: 0 18px 55px #00000020; }
    .hero-panel h2, .card h2, .form-card h2 { color: var(--forest); }
    .hero-mark { width: 52px; height: 52px; display: grid; place-items: center; border: 1px solid var(--champagne); border-radius: 50%; color: var(--forest); font-family: Georgia, serif; font-size: 1.6rem; }
    .hero-panel blockquote { margin: 22px 0 8px; color: var(--forest); font: 1.55rem/1.35 Georgia, serif; }
    .muted, .small { color: #c6d1c9; }
    .hero-panel .muted, .hero-panel .small, .card .muted, .card .small, .form-card .muted, .form-card .small { color: var(--muted); }
    .small { font-size: .84rem; line-height: 1.6; }
    .section { padding: 34px 0; }
    .three-grid, .metric-grid, .allocation-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
    .card { border: 1px solid var(--line); border-radius: var(--radius); padding: 22px; }
    .step-number { color: #746342; font-size: .78rem; font-weight: 700; letter-spacing: .12em; }
    .button { display: inline-flex; align-items: center; justify-content: center; border: 0; border-radius: 999px; padding: 13px 20px; background: var(--ivory); color: var(--forest); font-weight: 650; text-decoration: none; cursor: pointer; }
    .button:hover { background: #ded8c9; }
    .button.secondary { background: transparent; color: var(--ivory); border: 1px solid var(--ivory); }
    .button-row { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 24px; }
    .form-wrap { width: min(650px, 100%); margin: 14px auto; }
    .form-card { border: 1px solid var(--line); border-radius: 20px; padding: clamp(22px, 5vw, 38px); }
    .form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
    .field { display: grid; gap: 7px; margin-bottom: 17px; }
    .field.full { grid-column: 1 / -1; }
    label { color: var(--charcoal); font-weight: 650; font-size: .91rem; }
    input, select { width: 100%; min-height: 46px; border: 1px solid #b9c0b7; border-radius: 9px; background: var(--white); color: var(--charcoal); padding: 10px 12px; }
    input:focus, select:focus, button:focus-visible, a:focus-visible { outline: 3px solid #c7b58a; outline-offset: 2px; }
    .hint { margin: 0; color: var(--muted); font-size: .81rem; line-height: 1.5; }
    .alert { padding: 13px 16px; margin: 16px 0; border-radius: 10px; background: #f8e9e6; border: 1px solid #d5aaa2; color: var(--danger); }
    .alert.success { background: #e8eee6; border-color: var(--sage); color: var(--forest); }
    .dashboard-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 20px; margin-bottom: 28px; }
    .metric { min-height: 125px; }
    .metric-label { color: var(--muted); font-size: .85rem; }
    .metric-value { margin: 10px 0 6px; color: var(--forest); font-size: clamp(1.45rem, 2.5vw, 2rem); font-weight: 650; }
    .chart { display: flex; align-items: end; gap: 9px; height: 180px; margin: 26px 0 8px; padding: 12px 6px 0; border-bottom: 1px solid var(--line); }
    .chart-column { display: flex; flex: 1; height: 100%; flex-direction: column; justify-content: end; align-items: center; gap: 8px; }
    .chart-bar { width: min(38px, 68%); min-height: 4px; background: var(--forest); border-radius: 5px 5px 0 0; }
    .chart-label { color: var(--muted); font-size: .72rem; }
    .allocation-row { display: grid; grid-template-columns: 1fr auto; gap: 6px 12px; margin: 16px 0; }
    .allocation-track { grid-column: 1 / -1; height: 8px; overflow: hidden; border-radius: 99px; background: #e8e9e2; }
    .allocation-track span { display: block; height: 100%; background: var(--forest); }
    .allocation-row:nth-of-type(2) .allocation-track span { background: #738774; }
    .allocation-row:nth-of-type(3) .allocation-track span { background: #b19d70; }
    .badge { display: inline-flex; padding: 7px 10px; border-radius: 99px; background: #e8eee6; color: var(--forest); font-size: .78rem; font-weight: 700; }
    .notice { border-left: 3px solid var(--champagne); background: #f8f6f0; padding: 13px 16px; color: #47544c; }
    .table-wrap { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 13px 12px; border-bottom: 1px solid var(--line); text-align: left; }
    th { color: var(--muted); font-size: .8rem; font-weight: 650; }
    footer { border-top: 1px solid #456157; padding: 24px 0; color: #c6d1c9; font-size: .82rem; }
    .footer-row { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px 24px; }
    @media (max-width: 760px) {
      .hero { grid-template-columns: 1fr; gap: 26px; padding: 38px 0; }
      .nav { align-items: flex-start; flex-direction: column; padding: 16px 0; gap: 10px; }
      .nav-links { gap: 12px 18px; }
      .three-grid, .metric-grid, .allocation-grid { grid-template-columns: 1fr; }
      .dashboard-head { flex-direction: column; }
    }
    @media (max-width: 500px) { .shell { width: min(100% - 28px, 1120px); } .form-grid { grid-template-columns: 1fr; } .field.full { grid-column: auto; } main { padding-top: 26px; } }
  </style>
</head>
<body>
  <header class="topbar">
    <div class="shell nav">
      <a class="wordmark" href="{{ url_for('home') }}" aria-label="VALORA home">VALORA</a>
      <nav class="nav-links" aria-label="Main navigation">
        {% if current_user %}
          <a href="{{ url_for('dashboard') }}">Overview</a>
          <a href="{{ url_for('dashboard') }}">My portfolio</a>
          <a href="{{ url_for('activity') }}">Activity</a>
          <a href="{{ url_for('profile') }}">My profile</a>
          <form method="post" action="{{ url_for('logout') }}" style="margin:0">
            <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
            <button type="submit">Sign out</button>
          </form>
        {% else %}
          <a href="{{ url_for('home') }}#how-it-works">How it works</a>
          <a href="{{ url_for('login') }}">Sign in</a>
          <a class="nav-cta" href="{{ url_for('signup') }}">Get started</a>
        {% endif %}
      </nav>
    </div>
  </header>
  <main class="shell">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <div aria-live="polite">
          {% for category, message in messages %}
            <div class="alert {{ 'success' if category == 'success' else '' }}" role="status">{{ message }}</div>
          {% endfor %}
        </div>
      {% endif %}
    {% endwith %}
    {{ content }}
  </main>
  <footer>
    <div class="shell footer-row">
      <span class="wordmark">VALORA</span>
      <span>Illustrative student prototype | Invented data only | No real investing or money movement</span>
    </div>
  </footer>
</body>
</html>"""


HOME_TEMPLATE = """
<section class="hero">
  <div>
    <div class="eyebrow">Digital wealth management | Mexico</div>
    <h1>Your future,<br>thoughtfully invested.</h1>
    <p class="lead">A clearer way to understand your money and explore an investment approach connected to your goals, time horizon and comfort with risk.</p>
    <div class="button-row">
      <a class="button" href="{{ url_for('signup') }}">Start with your goals</a>
      <a class="button secondary" href="#how-it-works">How VALORA works</a>
    </div>
    <p class="small">A class prototype using invented, illustrative data - not a real investment service.</p>
  </div>
  <aside class="hero-panel">
    <div class="hero-mark" aria-hidden="true">V</div>
    <blockquote>"Clarity that compounds."</blockquote>
    <p class="small">Understand your profile first. Then explore why an illustrative portfolio matches the answers you shared.</p>
  </aside>
</section>
<section id="how-it-works" class="section">
  <div class="eyebrow">A considered first step</div>
  <h2>Understand before you invest.</h2>
  <div class="three-grid">
    <article class="card"><span class="step-number">01 | YOUR PROFILE</span><h3>Start with what matters</h3><p class="small">Share an objective, an investment horizon and how you might react to a temporary decline.</p></article>
    <article class="card"><span class="step-number">02 | YOUR APPROACH</span><h3>See the reasoning</h3><p class="small">Explore a transparent, rules-based investor profile and category-level illustrative allocation.</p></article>
    <article class="card"><span class="step-number">03 | YOUR DASHBOARD</span><h3>Follow a simulation</h3><p class="small">See an invented performance example and sample activity - never a live balance or a promised return.</p></article>
  </div>
</section>
<div class="notice small">This academic prototype does not open brokerage accounts, execute trades, conduct real KYC, hold assets, or transfer money. Do not enter real personal or financial information.</div>
"""


SIGNUP_TEMPLATE = """
<section class="form-wrap">
  <div class="form-card">
    <div class="eyebrow">Create your VALORA profile</div>
    <h1 style="font-size:2.55rem">A thoughtful beginning.</h1>
    <p class="muted">Use fictional details for this classroom demonstration.</p>
    {% if error %}<div class="alert" role="alert">{{ error }}</div>{% endif %}
    <form method="post" action="{{ url_for('signup') }}">
      <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
      <div class="field"><label for="name">Name</label><input id="name" name="name" autocomplete="name" maxlength="80" required value="{{ values.name }}"></div>
      <div class="field"><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" maxlength="254" required value="{{ values.email }}"></div>
      <div class="field"><label for="password">Password</label><input id="password" name="password" type="password" autocomplete="new-password" minlength="8" required><p class="hint">Use at least 8 characters. Do not reuse a real password.</p></div>
      <button class="button" type="submit">Continue to financial profile</button>
    </form>
    <p class="small">Already have an account? <a href="{{ url_for('login') }}">Sign in</a></p>
  </div>
</section>
"""


LOGIN_TEMPLATE = """
<section class="form-wrap">
  <div class="form-card">
    <div class="eyebrow">Welcome back</div>
    <h1 style="font-size:2.55rem">Sign in to VALORA.</h1>
    {% if error %}<div class="alert" role="alert">{{ error }}</div>{% endif %}
    <form method="post" action="{{ url_for('login') }}">
      <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
      <div class="field"><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" required value="{{ values.email }}"></div>
      <div class="field"><label for="password">Password</label><input id="password" name="password" type="password" autocomplete="current-password" required></div>
      <button class="button" type="submit">Sign in</button>
    </form>
    <p class="small">New to VALORA? <a href="{{ url_for('signup') }}">Create an account</a></p>
  </div>
</section>
"""


PROFILE_TEMPLATE = """
<section class="form-wrap">
  <div class="form-card">
    <div class="eyebrow">Step 1 of 2 | Your financial profile</div>
    <h1 style="font-size:2.55rem">What are you working toward?</h1>
    <p class="muted">Your answers shape an illustrative profile and category-level allocation. All amounts stay in this local demo.</p>
    {% if error %}<div class="alert" role="alert">{{ error }}</div>{% endif %}
    <form method="post" action="{{ url_for('profile') }}">
      <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
      <div class="form-grid">
        <div class="field"><label for="monthly_income">Approximate monthly income (MXN)</label><input id="monthly_income" name="monthly_income" type="number" min="0" step="0.01" required value="{{ values.monthly_income }}"><p class="hint">Enter an invented amount for this prototype.</p></div>
        <div class="field"><label for="starting_balance">Illustrative starting amount (MXN)</label><input id="starting_balance" name="starting_balance" type="number" min="0" step="0.01" required value="{{ values.starting_balance }}"><p class="hint">For the simulation only. This is not a deposit or transfer.</p></div>
        <div class="field full"><label for="objective">What is your main financial objective?</label><select id="objective" name="objective" required>
          {% for value, label in objectives %}<option value="{{ value }}" {{ 'selected' if values.objective == value else '' }}>{{ label }}</option>{% endfor %}
        </select></div>
        <div class="field"><label for="horizon_years">When might you need this money?</label><select id="horizon_years" name="horizon_years" required>
          {% for years in horizons %}<option value="{{ years }}" {{ 'selected' if values.horizon_years|string == years|string else '' }}>{{ years }} years</option>{% endfor %}
        </select></div>
        <div class="field"><label for="experience">How familiar are you with investing?</label><select id="experience" name="experience" required>
          {% for value, label in experiences %}<option value="{{ value }}" {{ 'selected' if values.experience == value else '' }}>{{ label }}</option>{% endfor %}
        </select></div>
        <div class="field full"><label for="decline_response">In a hypothetical simulation, if the portfolio value fell by 10%, what would you most likely do?</label><select id="decline_response" name="decline_response" required>
          {% for value, label in decline_responses %}<option value="{{ value }}" {{ 'selected' if values.decline_response == value else '' }}>{{ label }}</option>{% endfor %}
        </select><p class="hint">This is a fictional questionnaire scenario, not an actual investment event.</p></div>
      </div>
      <button class="button" type="submit">See my illustrative profile</button>
    </form>
  </div>
</section>
"""


DASHBOARD_TEMPLATE = """
<section class="dashboard-head">
  <div>
    <div class="eyebrow">Your VALORA overview</div>
    <h1 style="font-size:2.65rem">A clearer view, {{ user_name }}.</h1>
    <p class="muted">An illustrative simulation based only on the fictional profile you entered.</p>
  </div>
  <span class="badge">{{ investor_profile }} profile</span>
</section>
<section class="metric-grid" aria-label="Simulated portfolio summary">
  <article class="card metric"><div class="metric-label">Example portfolio value</div><div class="metric-value">{{ format_mxn(current_value) }}</div><p class="small">Simulated | not an account balance</p></article>
  <article class="card metric"><div class="metric-label">Example period change</div><div class="metric-value">{{ performance_label }}</div><p class="small">Invented sample series | not a forecast</p></article>
  <article class="card metric"><div class="metric-label">Your objective</div><div class="metric-value" style="font-size:1.25rem">{{ objective_label }}</div><p class="small">{{ horizon_years }}-year horizon</p></article>
</section>
<section class="section">
  <div class="three-grid" style="grid-template-columns:minmax(0,1.35fr) minmax(260px,.85fr)">
    <article class="card">
      <div class="eyebrow">Illustrative performance</div><h2>Progress, made clear.</h2>
      <p class="small">Every point below is invented for demonstration. It does not use market data and does not predict future results.</p>
      <div class="chart" role="img" aria-label="Invented simulated portfolio values over seven example periods">
        {% for point in chart_points %}
          <div class="chart-column"><span class="chart-bar" style="height:{{ point.height }}%" title="{{ format_mxn(point.value) }}"></span><span class="chart-label">{{ point.label }}</span></div>
        {% endfor %}
      </div>
      <p class="small">Start | then six fictional monthly points</p>
    </article>
    <article class="card">
      <div class="eyebrow">Why this profile</div><h2>{{ recommendation.title }}</h2>
      <p>{{ recommendation.summary }}</p>
      <p class="small">Based on your selected horizon and response to a hypothetical decline. This simple classroom rule is not a suitability assessment.</p>
      <a class="button secondary" href="{{ url_for('profile') }}">Review my profile</a>
    </article>
  </div>
</section>
<section class="section">
  <div class="eyebrow">Illustrative asset allocation</div>
  <h2>Categories, not specific products.</h2>
  <p class="small">Percentages are example allocations for this prototype - not a personalized recommendation to invest.</p>
  <div class="allocation-grid">
    {% for item in allocation %}
      <article class="card">
        <div class="allocation-row"><strong>{{ item.category }}</strong><strong>{{ item.percent }}%</strong>
          <div class="allocation-track" aria-label="{{ item.percent }} percent"><span style="width:{{ item.percent }}%"></span></div>
        </div>
        <p class="small">{{ item.rationale }}</p>
      </article>
    {% endfor %}
  </div>
</section>
<div class="notice small">No money has been invested, transferred, or held. Values and activity are simulated and should not be treated as expected or guaranteed returns.</div>
"""


ACTIVITY_TEMPLATE = """
<section class="section">
  <div class="eyebrow">Illustrative activity</div>
  <h1 style="font-size:2.8rem">A transparent sample history.</h1>
  <p class="muted">These entries are invented to demonstrate the activity view. They are not real transactions.</p>
  <div class="card table-wrap">
    <table><thead><tr><th>Description</th><th>Amount</th><th>Status</th></tr></thead>
      <tbody>{% for item in activity_items %}<tr><td>{{ item.description }}</td><td>{{ format_mxn(item.amount_cents) }}</td><td><span class="badge">Simulated</span></td></tr>{% else %}<tr><td colspan="3">No simulated activity yet.</td></tr>{% endfor %}</tbody>
    </table>
  </div>
  <p class="small">A simulated starting amount is not a deposit, payment or movement of money.</p>
</section>
"""


OBJECTIVES = (
    ("home", "Save toward a home"),
    ("retirement", "Plan for the long term"),
    ("wealth", "Build long-term savings"),
    ("flexible", "Keep my options open"),
)
EXPERIENCES = (
    ("new", "I have not invested before"),
    ("some", "I have tried a few investments"),
    ("active", "I have some investment experience"),
)
DECLINE_RESPONSES = (
    ("sell", "I would sell most or all of it"),
    ("wait", "I would wait and review my goal"),
    ("add", "I might consider adding more"),
)
HORIZONS = (1, 3, 5, 7, 10, 15)
OBJECTIVE_LABELS = dict(OBJECTIVES)


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=str(DEFAULT_DATABASE),
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_urlsafe(32),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        MAX_CONTENT_LENGTH=64 * 1024,
    )
    if test_config:
        app.config.update(test_config)

    initialize_database(app.config["DATABASE"])

    @app.before_request
    def load_request_state() -> None:
        session.setdefault("_csrf_token", secrets.token_urlsafe(32))
        user_id = session.get("user_id")
        g.current_user = None
        if user_id is not None:
            g.current_user = get_db().execute(
                "SELECT id, name, email FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            if g.current_user is None:
                session.clear()
                session["_csrf_token"] = secrets.token_urlsafe(32)

    @app.teardown_appcontext
    def close_database(_error: BaseException | None = None) -> None:
        connection = g.pop("database", None)
        if connection is not None:
            connection.close()

    @app.get("/")
    def home():
        if g.current_user:
            profile = get_profile(g.current_user["id"])
            if profile:
                return redirect(url_for("dashboard"))
            return redirect(url_for("profile"))
        return render_page(HOME_TEMPLATE, "Thoughtfully invested")

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if g.current_user:
            return redirect(url_for("dashboard"))
        values = {"name": "", "email": ""}
        error = None
        if request.method == "POST":
            validate_csrf()
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            values = {"name": name, "email": email}
            if not name or len(name) > 80:
                error = "Enter a name of 1 to 80 characters."
            elif "@" not in email or len(email) > 254:
                error = "Enter a valid email address."
            elif len(password) < 8:
                error = "Use a password with at least 8 characters."
            else:
                try:
                    cursor = get_db().execute(
                        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                        (name, email, generate_password_hash(password)),
                    )
                    get_db().commit()
                except sqlite3.IntegrityError:
                    error = "An account with that email already exists. Try signing in."
                else:
                    session.clear()
                    session["user_id"] = cursor.lastrowid
                    flash("Account created. Next, complete your illustrative financial profile.", "success")
                    return redirect(url_for("profile"))
        return render_page(SIGNUP_TEMPLATE, "Create account", error=error, values=values)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if g.current_user:
            return redirect(url_for("dashboard"))
        values = {"email": ""}
        error = None
        if request.method == "POST":
            validate_csrf()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            values = {"email": email}
            user = get_db().execute(
                "SELECT id, password_hash FROM users WHERE email = ?", (email,)
            ).fetchone()
            if user is None or not check_password_hash(user["password_hash"], password):
                error = "Email or password not recognized."
            else:
                session.clear()
                session["user_id"] = user["id"]
                flash("You are signed in.", "success")
                return redirect(url_for("dashboard"))
        return render_page(LOGIN_TEMPLATE, "Sign in", error=error, values=values)

    @app.post("/logout")
    def logout():
        validate_csrf()
        session.clear()
        flash("You have signed out.", "success")
        return redirect(url_for("home"))

    @app.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile():
        existing = get_profile(g.current_user["id"])
        values = profile_form_values(existing)
        error = None
        if request.method == "POST":
            validate_csrf()
            values = {key: request.form.get(key, "").strip() for key in values}
            try:
                monthly_income_cents = parse_money_to_cents(values["monthly_income"])
                starting_balance_cents = parse_money_to_cents(values["starting_balance"])
                horizon_years = int(values["horizon_years"])
            except (InvalidOperation, ValueError):
                error = "Enter valid amounts and select an available time horizon."
            else:
                objective = values["objective"]
                decline_response = values["decline_response"]
                experience = values["experience"]
                if horizon_years not in HORIZONS:
                    error = "Choose one of the listed investment horizons."
                elif objective not in OBJECTIVE_LABELS:
                    error = "Choose one of the listed objectives."
                elif decline_response not in dict(DECLINE_RESPONSES):
                    error = "Choose one of the listed responses."
                elif experience not in dict(EXPERIENCES):
                    error = "Choose one of the listed experience levels."
                else:
                    investor_profile = classify_profile(horizon_years, decline_response)
                    save_financial_profile(
                        get_db(),
                        user_id=g.current_user["id"],
                        monthly_income_cents=monthly_income_cents,
                        starting_balance_cents=starting_balance_cents,
                        objective=objective,
                        horizon_years=horizon_years,
                        decline_response=decline_response,
                        experience=experience,
                        investor_profile=investor_profile,
                    )
                    flash("Your illustrative profile and portfolio are ready.", "success")
                    return redirect(url_for("dashboard"))
        return render_page(
            PROFILE_TEMPLATE,
            "Financial profile",
            error=error,
            values=values,
            objectives=OBJECTIVES,
            horizons=HORIZONS,
            experiences=EXPERIENCES,
            decline_responses=DECLINE_RESPONSES,
        )

    @app.get("/dashboard")
    @login_required
    def dashboard():
        profile_row = get_profile(g.current_user["id"])
        if profile_row is None:
            return redirect(url_for("profile"))
        portfolio = get_db().execute(
            "SELECT id FROM portfolios WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (g.current_user["id"],),
        ).fetchone()
        if portfolio is None:
            abort(404)
        return render_portfolio(portfolio["id"])

    @app.get("/portfolio/<int:portfolio_id>")
    @login_required
    def portfolio_detail(portfolio_id: int):
        return render_portfolio(portfolio_id)

    @app.get("/activity")
    @login_required
    def activity():
        items = get_db().execute(
            """
            SELECT t.description, t.amount_cents
            FROM transactions AS t
            JOIN portfolios AS p ON p.id = t.portfolio_id
            WHERE p.user_id = ? AND t.is_simulated = 1
            ORDER BY t.id DESC
            """,
            (g.current_user["id"],),
        ).fetchall()
        return render_page(
            ACTIVITY_TEMPLATE,
            "Illustrative activity",
            activity_items=items,
            format_mxn=format_mxn,
        )

    def render_portfolio(portfolio_id: int):
        portfolio = get_db().execute(
            """
            SELECT p.id, p.user_id, p.investor_profile, p.starting_balance_cents,
                   f.objective, f.horizon_years
            FROM portfolios AS p
            JOIN financial_profiles AS f ON f.user_id = p.user_id
            WHERE p.id = ? AND p.user_id = ?
            """,
            (portfolio_id, g.current_user["id"]),
        ).fetchone()
        if portfolio is None:
            abort(404)
        points = get_db().execute(
            """
            SELECT month_index, value_cents
            FROM performance
            WHERE portfolio_id = ? AND is_simulated = 1
            ORDER BY month_index
            """,
            (portfolio_id,),
        ).fetchall()
        if not points:
            abort(404)

        starting_value = portfolio["starting_balance_cents"]
        current_value = points[-1]["value_cents"]
        # This computes the simulated change from the starting value; dividing by that
        # starting value makes the displayed percentage comparable to the example base.
        performance_pct = (
            (Decimal(current_value - starting_value) / Decimal(starting_value) * 100)
            if starting_value > 0
            else None
        )
        performance_label = (
            f"{performance_pct:+.1f}%"
            if performance_pct is not None
            else "Not shown"
        )
        chart_max = max(point["value_cents"] for point in points)
        chart_points = [
            {
                "label": "Start" if point["month_index"] == 0 else f"M{point['month_index']}",
                "value": point["value_cents"],
                "height": max(4, round(point["value_cents"] / chart_max * 100))
                if chart_max > 0
                else 4,
            }
            for point in points
        ]
        recommendation = PROFILES[portfolio["investor_profile"]]
        products = get_db().execute(
            """
            SELECT category, allocation_percent, rationale
            FROM products WHERE portfolio_id = ? ORDER BY id
            """,
            (portfolio_id,),
        ).fetchall()
        allocation = [
            {
                "category": item["category"],
                "percent": item["allocation_percent"],
                "rationale": item["rationale"],
            }
            for item in products
        ]
        return render_page(
            DASHBOARD_TEMPLATE,
            "Your overview",
            user_name=g.current_user["name"].split()[0],
            investor_profile=portfolio["investor_profile"],
            current_value=current_value,
            performance_label=performance_label,
            objective_label=OBJECTIVE_LABELS[portfolio["objective"]],
            horizon_years=portfolio["horizon_years"],
            chart_points=chart_points,
            recommendation=recommendation,
            allocation=allocation,
            format_mxn=format_mxn,
        )

    return app


def login_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any):
        if g.current_user is None:
            flash("Sign in to continue.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def validate_csrf() -> None:
    submitted = request.form.get("csrf_token", "")
    expected = session.get("_csrf_token", "")
    if not expected or not hmac.compare_digest(submitted, expected):
        abort(400, description="The form expired. Reload the page and try again.")


def get_db() -> sqlite3.Connection:
    if "database" not in g:
        connection = sqlite3.connect(current_app_database())
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        g.database = connection
    return g.database


def current_app_database() -> str:
    from flask import current_app

    return current_app.config["DATABASE"]


def initialize_database(path: str) -> None:
    database_path = Path(path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    try:
        connection.executescript(SCHEMA)
        connection.commit()
    finally:
        connection.close()


def get_profile(user_id: int) -> sqlite3.Row | None:
    return get_db().execute(
        "SELECT * FROM financial_profiles WHERE user_id = ?", (user_id,)
    ).fetchone()


def profile_form_values(profile: sqlite3.Row | None) -> dict[str, str]:
    if profile is None:
        return {
            "monthly_income": "",
            "starting_balance": "",
            "objective": "home",
            "horizon_years": "5",
            "decline_response": "wait",
            "experience": "new",
        }
    return {
        "monthly_income": format_input_mxn(profile["monthly_income_cents"]),
        "starting_balance": format_input_mxn(profile["starting_balance_cents"]),
        "objective": profile["objective"],
        "horizon_years": str(profile["horizon_years"]),
        "decline_response": profile["decline_response"],
        "experience": profile["experience"],
    }


def classify_profile(horizon_years: int, decline_response: str) -> str:
    if horizon_years < 3 or decline_response == "sell":
        return "Conservative"
    if horizon_years >= 7 and decline_response == "add":
        return "Growth"
    return "Balanced"


def parse_money_to_cents(raw: str) -> int:
    value = Decimal(raw)
    if not value.is_finite() or value < 0:
        raise InvalidOperation
    return int((value * 100).quantize(Decimal("1")))


def format_mxn(amount_cents: int) -> str:
    amount = Decimal(amount_cents) / Decimal(100)
    return f"${amount:,.2f} MXN"


def format_input_mxn(amount_cents: int) -> str:
    amount = Decimal(amount_cents) / Decimal(100)
    return f"{amount:.2f}"


def save_financial_profile(
    connection: sqlite3.Connection,
    *,
    user_id: int,
    monthly_income_cents: int,
    starting_balance_cents: int,
    objective: str,
    horizon_years: int,
    decline_response: str,
    experience: str,
    investor_profile: str,
) -> None:
    with connection:
        connection.execute(
            """
            INSERT INTO financial_profiles (
                user_id, monthly_income_cents, starting_balance_cents, objective,
                horizon_years, decline_response, experience, investor_profile
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                monthly_income_cents = excluded.monthly_income_cents,
                starting_balance_cents = excluded.starting_balance_cents,
                objective = excluded.objective,
                horizon_years = excluded.horizon_years,
                decline_response = excluded.decline_response,
                experience = excluded.experience,
                investor_profile = excluded.investor_profile,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                user_id,
                monthly_income_cents,
                starting_balance_cents,
                objective,
                horizon_years,
                decline_response,
                experience,
                investor_profile,
            ),
        )
        previous = connection.execute(
            "SELECT id FROM portfolios WHERE user_id = ?", (user_id,)
        ).fetchall()
        for item in previous:
            connection.execute("DELETE FROM portfolios WHERE id = ?", (item["id"],))
        cursor = connection.execute(
            """
            INSERT INTO portfolios (user_id, investor_profile, starting_balance_cents)
            VALUES (?, ?, ?)
            """,
            (user_id, investor_profile, starting_balance_cents),
        )
        portfolio_id = cursor.lastrowid
        for category, allocation_percent, rationale in PROFILES[investor_profile]["allocation"]:
            connection.execute(
                """
                INSERT INTO products (portfolio_id, category, allocation_percent, rationale)
                VALUES (?, ?, ?, ?)
                """,
                (portfolio_id, category, allocation_percent, rationale),
            )
        connection.execute(
            """
            INSERT INTO transactions (portfolio_id, description, amount_cents, is_simulated)
            VALUES (?, ?, ?, 1)
            """,
            (
                portfolio_id,
                "Illustrative starting amount | no deposit or transfer",
                starting_balance_cents,
            ),
        )
        for month_index, factor in enumerate(SIMULATED_MONTHLY_FACTORS):
            # This scales the fictional starting amount by a fixed demo factor to create
            # sample values; it is not an interest, fee, expected return, or live price.
            simulated_value = int(
                (Decimal(starting_balance_cents) * factor).quantize(Decimal("1"))
            )
            connection.execute(
                """
                INSERT INTO performance (portfolio_id, month_index, value_cents, is_simulated)
                VALUES (?, ?, ?, 1)
                """,
                (portfolio_id, month_index, simulated_value),
            )


def render_page(template: str, page_title: str, **context: Any):
    csrf_token = session.get("_csrf_token", "")
    content = Markup(
        render_template_string(
            template,
            csrf_token=csrf_token,
            **context,
        )
    )
    return render_template_string(
        BASE_TEMPLATE,
        page_title=page_title,
        content=content,
        csrf_token=csrf_token,
        current_user=g.current_user,
        url_for=url_for,
    )


if __name__ == "__main__":
    application = create_app()
    application.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=False,
    )
