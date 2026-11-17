from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

OUTPUT = r"c:\Users\vikip\OneDrive\Desktop\Nueva carpeta\fintech\job_statement_document.pdf"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleCentered', parent=styles['Title'], alignment=1, fontSize=22, leading=26, spaceAfter=18, textColor=colors.HexColor('#1f1f1f')))
styles.add(ParagraphStyle(name='Section', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor('#1d3557'), spaceBefore=18, spaceAfter=8))
styles.add(ParagraphStyle(name='Body', parent=styles['BodyText'], fontSize=10.5, leading=15, spaceAfter=8, textColor=colors.HexColor('#1f1f1f')))
styles.add(ParagraphStyle(name='BoldBody', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=10.5, leading=15, spaceAfter=8, textColor=colors.HexColor('#1f1f1f')))
styles.add(ParagraphStyle(name='ListItem', parent=styles['BodyText'], fontSize=10.5, leading=14, leftIndent=18, bulletIndent=12, spaceAfter=4))

text = []
text.append(Paragraph("Financial Goal-to-Investment Decision Problem", styles['TitleCentered']))
text.append(Spacer(1, 10))

text.append(Paragraph("1. Problem context", styles['Section']))
text.append(Paragraph(
    "Many individuals have clear financial objectives, such as buying a home, building an emergency fund, or saving for a major future expense, but they do not know which investment approach best fits those objectives. In practice, there is often a disconnect between the personal goal and the decision-making process required to translate that goal into an investment strategy.",
    styles['Body']
))
text.append(Paragraph(
    "This creates two relevant problems:",
    styles['Body']
))
text.append(Paragraph("- High complexity when starting to invest: financial markets offer many options, including stocks, ETFs, bonds, mutual funds, treasury instruments, and other products, yet many people do not have a simple process that connects a personal goal to an investment path.", styles['ListItem']))
text.append(Paragraph("- Low accessibility of professional-style investment tools: portfolio analysis, diversification, risk assessment, and planning tools are often difficult for beginning investors to understand and use.", styles['ListItem']))
text.append(Paragraph("The opportunity is to reduce this gap by helping users move from a vague financial objective to a practical investment approach, using a clear and accessible decision framework.", styles['Body']))
text.append(PageBreak())

text.append(Paragraph("2. Job statements", styles['Section']))
job_statements = [
    "When I have a financial goal, such as buying a house in 10 years or saving for a major life event, I want a simple way to translate that goal into an investment approach, so I can choose a strategy that matches my time horizon, risk tolerance, and financial reality.",
    "When I am starting to invest and I feel overwhelmed by the number of options available, I want a clear decision process that connects my objective to practical investment choices, so I can move from uncertainty to a first informed decision.",
    "When I need to decide how to allocate my money, I want to understand the trade-offs between risk, time horizon, and expected outcome, so I can make investment decisions that align with my real goals instead of reacting to market noise or external pressure."
]
for i, js in enumerate(job_statements, start=1):
    text.append(Paragraph(f"Job statement {i}", styles['BoldBody']))
    text.append(Paragraph(js, styles['Body']))
    text.append(Spacer(1, 6))

text.append(PageBreak())

text.append(Paragraph("3. Interview guide", styles['Section']))
text.append(Paragraph("The purpose of this interview guide is to understand how users currently connect financial goals to investment decisions, where they get stuck, and what they do when they cannot decide.", styles['Body']))
questions = [
    ("Warm-up", [
        "Tell me about the last time you thought seriously about your financial goals.",
        "What were you trying to accomplish at that moment?",
        "What made you start thinking about it then?"
    ]),
    ("First thought", [
        "What did you do first when you began trying to understand how to invest or save?",
        "What options did you consider, and why were they relevant or not relevant to your situation?"
    ]),
    ("Timeline", [
        "Tell me about the last time you felt uncertain about which investment option to choose.",
        "Walk me through how you made that decision, step by step.",
        "How much did this process cost you in time, stress, money, or missed opportunities?"
    ]),
    ("Forces", [
        "Who was involved in that decision, if anyone?",
        "What happened if you did not decide or if you delayed the decision?"
    ])
]
for section_title, items in questions:
    text.append(Paragraph(f"{section_title}", styles['BoldBody']))
    for idx, item in enumerate(items, start=1):
        text.append(Paragraph(f"{idx}. {item}", styles['Body']))
    text.append(Spacer(1, 8))

text.append(Paragraph("These questions are designed to capture real experiences, not hypothetical situations. They focus on meaningful past events, decision-making behavior, and the practical consequences of uncertainty.", styles['Body']))
text.append(PageBreak())

text.append(Paragraph("4. Competitor map", styles['Section']))
text.append(Paragraph("The map below uses the two dimensions that users care about most:", styles['Body']))
text.append(Paragraph("- X axis: Ease of decision-making", styles['Body']))
text.append(Paragraph("- Y axis: Fit between the user’s goal and the recommended investment approach", styles['Body']))

competitor_data = [
    [Paragraph("Quadrant", styles['BoldBody']), Paragraph("Competitor", styles['BoldBody']), Paragraph("Customer problem", styles['BoldBody']), Paragraph("Value offered", styles['BoldBody']), Paragraph("Success signal", styles['BoldBody']), Paragraph("Risky assumption", styles['BoldBody'])],
    [Paragraph("Low ease, low fit", styles['Body']), Paragraph("Status quo: manual research, spreadsheets, informal advice, and inaction", styles['Body']), Paragraph("Users struggle to connect personal goals to investment choices and often delay decisions.", styles['Body']), Paragraph("No structured support; outcomes depend on effort and luck.", styles['Body']), Paragraph("Users continue to delay, rely on fragmented information, or make decisions without confidence.", styles['Body']), Paragraph("Users will keep using the status quo without more guidance.", styles['Body'])],
    [Paragraph("High ease, low fit", styles['Body']), Paragraph("Generic investment information platforms", styles['Body']), Paragraph("Users can access information, but still cannot map their goal to a suitable strategy.", styles['Body']), Paragraph("Educational content, market updates, and basic explanations.", styles['Body']), Paragraph("Users consume advice but still hesitate before acting.", styles['Body']), Paragraph("Information alone is enough to guide investment decisions.", styles['Body'])],
    [Paragraph("Low ease, high fit", styles['Body']), Paragraph("Human financial advisors and premium planning services", styles['Body']), Paragraph("Users want a strategy tailored to their life goals and constraints, but this support is hard to access.", styles['Body']), Paragraph("Personalized recommendations and professional guidance.", styles['Body']), Paragraph("Users seek or retain professional help.", styles['Body']), Paragraph("Users are willing and able to pay for personalized planning.", styles['Body'])],
    [Paragraph("High ease, high fit", styles['Body']), Paragraph("Guided planning and decision-support tools", styles['Body']), Paragraph("Users want a clear process that translates goals into an investment path without complexity.", styles['Body']), Paragraph("Structured decision support, personalization, and reduced uncertainty.", styles['Body']), Paragraph("Users complete a plan, choose a strategy, or take an initial investment action.", styles['Body']), Paragraph("Guided structure meaningfully improves decision quality and adoption.", styles['Body'])],
]

table = Table(competitor_data, colWidths=[58, 120, 120, 110, 120, 110])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dfeaf4')),
    ('GRID', (0, 0), (-1, -1), 0.6, colors.grey),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7f7f7')]),
    ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))
text.append(table)
text.append(Spacer(1, 12))
text.append(Paragraph("Competitor list", styles['BoldBody']))
text.append(Paragraph("1. Status quo: manual research and inaction", styles['Body']))
text.append(Paragraph("2. Human financial advisor", styles['Body']))
text.append(Paragraph("3. Generic investment information platform", styles['Body']))
text.append(Paragraph("4. Self-directed brokerage platform", styles['Body']))
text.append(Paragraph("5. Guided planning or decision-support product", styles['Body']))
text.append(PageBreak())

text.append(Paragraph("5. Hypothesis list", styles['Section']))
text.append(Paragraph("Hypothesis 1: Customer hypothesis", styles['BoldBody']))
text.append(Paragraph("We believe users with clear financial goals but limited investing experience are the segment most likely to struggle with choosing an investment approach.", styles['Body']))
text.append(Paragraph("Hypothesis 2: Problem hypothesis", styles['BoldBody']))
text.append(Paragraph("We believe the core problem is frequent and costly: users delay or make poor decisions because they cannot easily translate a financial goal into a suitable strategy.", styles['Body']))
text.append(Paragraph("Hypothesis 3: Value hypothesis", styles['BoldBody']))
text.append(Paragraph("We believe users will adopt a guided solution if it helps them understand which investment approach best matches their goal, time horizon, and risk tolerance without requiring advanced financial expertise.", styles['Body']))
text.append(Paragraph("Hypothesis 4: Adoption hypothesis", styles['BoldBody']))
text.append(Paragraph("We believe users are more likely to engage with a product that reduces uncertainty and provides a clear next step, rather than a product that simply presents more investment information.", styles['Body']))
text.append(Paragraph("Hypothesis 5: Risk hypothesis", styles['BoldBody']))
text.append(Paragraph("We believe the riskiest assumption is that users value a guided planning experience more than a list of investment products or market data.", styles['Body']))
text.append(Paragraph("Ranked hypotheses", styles['BoldBody']))
text.append(Paragraph("1. Users struggle most with translating a financial goal into a suitable investment strategy.", styles['Body']))
text.append(Paragraph("2. Users value clarity and structure more than product breadth.", styles['Body']))
text.append(Paragraph("3. Users are more likely to act when they can see a clear first step.", styles['Body']))
text.append(Paragraph("4. A simplified decision process may outperform educational content alone.", styles['Body']))
text.append(Paragraph("5. The strongest differentiator is goal-to-strategy clarity, not advanced analytics or product variety.", styles['Body']))
text.append(Spacer(1, 8))

text.append(Paragraph("6. Final synthesis", styles['Section']))
text.append(Paragraph("The key opportunity is not to offer a larger number of financial products, but to reduce the gap between the user’s financial objective and the investment approach that best fits that objective. In other words, many users need a translation layer: a simple, reliable way to move from “I want to buy a home in 10 years” to “this is the investment approach that makes sense for my situation.”", styles['Body']))
text.append(Paragraph("This framing suggests a product opportunity grounded in decision support, accessibility, and clarity rather than product complexity or market depth.", styles['Body']))


pdf = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=36,
    rightMargin=36,
    topMargin=36,
    bottomMargin=36,
)
pdf.build(text)
print(f"PDF generated successfully: {OUTPUT}")
