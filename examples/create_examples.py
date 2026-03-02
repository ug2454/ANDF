"""
Generate the four ANDF example documents.

Run from the project root:
    python examples/create_examples.py
"""
from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from andf import ANDFDocument


# ─────────────────────────────────────────────────────────
# 1. Research Paper
# ─────────────────────────────────────────────────────────

def make_research_paper() -> ANDFDocument:
    doc = ANDFDocument()
    doc.set_metadata(
        title="Attention Is All You Need: A Retrospective Analysis",
        subtitle="Re-examining the transformer architecture five years later",
        authors=["Dr. Alice Chen", "Prof. Bob Martinez", "Dr. Carol Liu"],
        keywords=["transformers", "attention", "deep learning", "NLP", "LLM"],
        language="en",
        category="Computer Science",
        status="published",
        version="2.1",
        license="CC BY 4.0",
    )
    doc.set_theme("academic")
    doc.set_layout(footer="page_number")

    r1 = doc.add_reference(
        ref_type="conference",
        label="Vaswani2017",
        title="Attention Is All You Need",
        authors=["Vaswani, A.", "Shazeer, N.", "Parmar, N.", "Uszkoreit, J."],
        year=2017,
        doi="10.48550/arXiv.1706.03762",
    )
    r2 = doc.add_reference(
        ref_type="article",
        label="Brown2020",
        title="Language Models are Few-Shot Learners",
        authors=["Brown, T.", "Mann, B.", "Ryder, N."],
        year=2020,
        doi="10.48550/arXiv.2005.14165",
    )
    r3 = doc.add_reference(
        ref_type="article",
        label="Wei2022",
        title="Emergent Abilities of Large Language Models",
        authors=["Wei, J.", "Tay, Y.", "Bommasani, R."],
        year=2022,
        doi="10.48550/arXiv.2206.07682",
    )

    doc.set_ai(
        summary=(
            "This paper provides a retrospective analysis of the Transformer architecture "
            "introduced by Vaswani et al. (2017), examining its impact on NLP, the emergence "
            "of large language models, and open research questions five years after publication."
        ),
        key_points=[
            "The Transformer replaced recurrence with self-attention, enabling massive parallelism.",
            "Scaling laws predict that performance improves predictably with compute and data.",
            "Emergent capabilities arise at scale, many of which were not anticipated in 2017.",
            "Open problems remain in interpretability, efficiency, and alignment.",
        ],
        topics=[
            {"label": "Natural Language Processing", "confidence": 0.98},
            {"label": "Deep Learning", "confidence": 0.97},
            {"label": "Large Language Models", "confidence": 0.95},
            {"label": "Attention Mechanisms", "confidence": 0.93},
        ],
        reading_time_minutes=12,
        complexity="expert",
        questions_answered=[
            "What is the transformer architecture?",
            "Why did attention replace recurrence?",
            "What are emergent capabilities in LLMs?",
        ],
        entities={
            "people": ["Vaswani", "Brown", "Wei"],
            "organizations": ["Google Brain", "OpenAI", "DeepMind"],
            "technologies": ["Transformer", "BERT", "GPT", "T5"],
            "concepts": ["self-attention", "scaling laws", "emergent abilities", "few-shot learning"],
        },
    )

    # ── Abstract ──
    abstract = doc.add_section("abstract", "Abstract", role="abstract")
    abstract.paragraph(
        "The Transformer architecture [Vaswani2017], introduced in 2017, fundamentally changed "
        "the landscape of natural language processing and, more broadly, machine learning. "
        "In this retrospective, we revisit the original design decisions, trace the architectural "
        "evolution through GPT, BERT, and T5, and examine the emergent capabilities [Wei2022] "
        "that large-scale transformers have displayed. We find that the original paper's core "
        "insight — that attention mechanisms alone suffice for sequence modelling — has proven "
        "remarkably durable, while many practical details have evolved significantly.",
        role="abstract", importance=5,
    )

    # ── Introduction ──
    intro = doc.add_section("introduction", "1. Introduction", role="introduction")
    intro.paragraph(
        "Prior to 2017, the dominant paradigm for sequence-to-sequence tasks was the recurrent "
        "neural network (RNN) with LSTM cells. RNNs process tokens sequentially, making them "
        "difficult to parallelise and prone to vanishing gradients over long sequences. The "
        "Transformer replaced this with a purely attention-based architecture, enabling full "
        "parallelism during training and dramatically reducing wall-clock time.",
        importance=4,
    )
    intro.paragraph(
        "The impact was immediate: within two years BERT and GPT demonstrated that pre-training "
        "on large text corpora produced powerful representations that could be fine-tuned for "
        "virtually any downstream task [Brown2020]. This paper examines what made that transition "
        "possible and what questions remain open.",
        importance=4,
    )

    # ── Background ──
    bg = doc.add_section("background", "2. Background", role="body")
    bg.heading("2.1 Self-Attention", level=3)
    bg.paragraph(
        "Self-attention computes a weighted sum of values, where the weight for each value is "
        "determined by the compatibility of a query with the corresponding key. Formally, given "
        "queries **Q**, keys **K**, and values **V**:"
    )
    bg.code(
        code=(
            "Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V\n\n"
            "# Multi-head variant\n"
            "MultiHead(Q, K, V) = Concat(head_1, ..., head_h) * W_O\n"
            "head_i = Attention(Q * W_Q_i, K * W_K_i, V * W_V_i)"
        ),
        language="python",
        caption="Scaled dot-product and multi-head attention",
        line_numbers=False,
    )
    bg.heading("2.2 Positional Encoding", level=3)
    bg.paragraph(
        "Since attention is permutation-invariant, position information must be injected. The "
        "original Transformer used sinusoidal encodings, while later models learned positional "
        "embeddings or adopted rotary position embeddings (RoPE)."
    )

    # ── Scaling Laws ──
    scaling = doc.add_section("scaling", "3. Scaling Laws", role="body")
    scaling.paragraph(
        "One of the most significant findings of the post-2017 era is the existence of smooth "
        "power-law relationships between model size, dataset size, compute budget, and test loss. "
        "Empirically, cross-entropy loss L scales as:"
    )
    scaling.table(
        caption="Table 1: Scaling law exponents (approximate)",
        headers=["Factor", "Exponent (α)", "Description"],
        rows=[
            ["Parameters (N)", "0.076", "Holding data and compute fixed"],
            ["Tokens (D)", "0.095", "Holding parameters and compute fixed"],
            ["FLOPs (C)", "0.050", "Optimal allocation of compute budget"],
        ],
        align=["left", "center", "left"],
    )
    scaling.callout(
        variant="tip",
        title="Practical Implication",
        text=(
            "For a fixed compute budget, it is better to train a smaller model on more data "
            "than a larger model on less data. This insight led to the Chinchilla family of models."
        ),
    )

    # ── Emergent Capabilities ──
    emerge = doc.add_section("emergence", "4. Emergent Capabilities", role="body")
    emerge.paragraph(
        "Wei et al. [Wei2022] documented capabilities that appear suddenly as models scale, "
        "including multi-step arithmetic, chain-of-thought reasoning, and few-shot in-context "
        "learning. These emergent abilities were not predicted by scaling laws and remain an "
        "active area of theoretical investigation.",
        importance=5,
        role="result",
    )
    emerge.list(
        items=[
            {"text": "Multi-step arithmetic (>100B parameters)", "level": 0},
            {"text": "Chain-of-thought reasoning", "level": 0},
            {"text": "BIG-Bench Hard tasks", "level": 0},
            {"text": "Instruction following without fine-tuning", "level": 0},
            {"text": "Code synthesis from natural language", "level": 0},
        ],
        ordered=False,
    )
    emerge.callout(
        variant="warning",
        title="Measurement Artefact?",
        text=(
            "Some researchers argue that apparent emergence is a metric artefact: using "
            "calibrated probability metrics instead of discrete accuracy reveals smooth scaling. "
            "The debate is ongoing."
        ),
    )

    # ── Open Problems ──
    open_p = doc.add_section("open", "5. Open Problems", role="conclusion")
    open_p.paragraph(
        "Despite remarkable progress, several fundamental questions remain unanswered:",
        importance=3,
    )
    open_p.list(
        items=[
            {"text": "**Interpretability**: Why do specific heads and layers encode specific knowledge?", "level": 0},
            {"text": "**Efficiency**: Can we achieve similar performance with fewer parameters or less compute?", "level": 0},
            {"text": "**Alignment**: How do we ensure models behave safely as capabilities scale?", "level": 0},
            {"text": "**Compositionality**: Do transformers truly reason or do they pattern-match?", "level": 0},
        ],
        ordered=False,
    )
    open_p.quote(
        text=(
            "The history of science is not the history of a discipline gradually uncovering truth; "
            "it is a sequence of dominant paradigms, each eventually displaced by a better one."
        ),
        attribution="Thomas Kuhn (paraphrased)",
    )

    # ── Conclusion ──
    conc = doc.add_section("conclusion", "6. Conclusion", role="conclusion")
    conc.paragraph(
        "The Transformer has proven to be one of the most consequential architectural innovations "
        "in the history of machine learning. Its core mechanisms — multi-head self-attention and "
        "feed-forward sublayers — have remained remarkably stable even as scale has increased by "
        "six orders of magnitude. The next decade will likely bring further surprises.",
        importance=4,
    )

    return doc


# ─────────────────────────────────────────────────────────
# 2. Business Report
# ─────────────────────────────────────────────────────────

def make_business_report() -> ANDFDocument:
    doc = ANDFDocument()
    doc.set_metadata(
        title="Q4 2025 Business Performance Report",
        subtitle="Executive Summary & Strategic Outlook",
        authors=["Finance Team", "Strategy Office"],
        keywords=["quarterly report", "revenue", "KPIs", "2025"],
        category="Business",
        status="final",
        version="1.0",
        license="Confidential",
    )
    doc.set_theme("corporate")

    doc.set_ai(
        summary=(
            "Q4 2025 showed 23% revenue growth YoY to $4.2B, with operating margin expanding "
            "to 31%. SaaS ARR crossed $1B. Headcount grew to 8,400. Key risks include regulatory "
            "uncertainty in EU markets and supply chain constraints for hardware division."
        ),
        key_points=[
            "Revenue: $4.2B (+23% YoY)",
            "Operating margin: 31% (up from 28%)",
            "SaaS ARR: $1.02B (first $1B quarter)",
            "Net Promoter Score: 72 (industry best)",
        ],
        topics=[
            {"label": "Financial Performance", "confidence": 0.99},
            {"label": "SaaS Metrics", "confidence": 0.95},
            {"label": "Strategic Planning", "confidence": 0.88},
        ],
        reading_time_minutes=8,
        complexity="medium",
    )

    # ── Executive Summary ──
    exec_sum = doc.add_section("exec-summary", "Executive Summary", role="abstract")
    exec_sum.paragraph(
        "Acme Corporation delivered its strongest quarter on record in Q4 2025, with revenue "
        "of **$4.2 billion**, a 23% increase year-over-year. Operating income grew to **$1.3B** "
        "as efficiency initiatives offset headcount growth. Our SaaS Annual Recurring Revenue "
        "crossed the **$1 billion milestone** for the first time."
    )
    exec_sum.callout(
        variant="success",
        title="Record Quarter",
        text="Q4 2025 marks our highest-ever quarterly revenue, operating income, and NPS score.",
    )

    # ── KPIs ──
    kpi = doc.add_section("kpis", "Key Performance Indicators", role="body")
    kpi.table(
        caption="Table 1: Q4 2025 KPI Dashboard",
        headers=["Metric", "Q4 2025", "Q4 2024", "Change", "Target"],
        rows=[
            ["Revenue", "$4.20B", "$3.41B", "+23%", "$4.10B ✓"],
            ["Operating Income", "$1.30B", "$0.95B", "+37%", "$1.20B ✓"],
            ["Operating Margin", "31%", "28%", "+3pp", "30% ✓"],
            ["SaaS ARR", "$1.02B", "$0.74B", "+38%", "$1.00B ✓"],
            ["Gross Margin", "68%", "65%", "+3pp", "67% ✓"],
            ["Net Promoter Score", "72", "65", "+7", "70 ✓"],
            ["Headcount", "8,400", "7,100", "+18%", "8,500 ✓"],
            ["Customer Churn (SaaS)", "1.8%", "2.4%", "-0.6pp", "<2.0% ✓"],
        ],
        align=["left", "right", "right", "center", "center"],
    )

    # ── Revenue Breakdown ──
    rev = doc.add_section("revenue", "Revenue Analysis", role="body")
    rev.heading("By Segment", level=3)
    rev.table(
        caption="Table 2: Revenue by Business Segment",
        headers=["Segment", "Q4 2025 ($M)", "Q4 2024 ($M)", "Growth"],
        rows=[
            ["Cloud SaaS", "1,850", "1,330", "+39%"],
            ["Enterprise Licences", "1,100", "980", "+12%"],
            ["Professional Services", "680", "620", "+10%"],
            ["Hardware & Devices", "570", "480", "+19%"],
            ["**Total**", "**4,200**", "**3,410**", "**+23%**"],
        ],
        align=["left", "right", "right", "center"],
    )
    rev.callout(
        variant="info",
        title="SaaS Acceleration",
        text=(
            "Cloud SaaS grew 39% — significantly above our 30% target — driven by the enterprise "
            "AI platform launch in October and strong renewal rates in the financial services vertical."
        ),
    )

    # ── Costs ──
    costs = doc.add_section("costs", "Cost Structure", role="body")
    costs.paragraph(
        "Total operating expenses were $2.9B (69% of revenue), down from 72% in Q4 2024. "
        "The improvement reflects automation in customer support (−$42M), real estate "
        "rationalisation (−$18M), and vendor contract renegotiations (−$27M)."
    )
    costs.table(
        caption="Table 3: Operating Expense Breakdown",
        headers=["Category", "Q4 2025 ($M)", "% of Revenue"],
        rows=[
            ["R&D", "840", "20%"],
            ["Sales & Marketing", "630", "15%"],
            ["General & Administrative", "252", "6%"],
            ["Cost of Revenue", "1,176", "28%"],
            ["**Total OpEx**", "**2,898**", "**69%**"],
        ],
        align=["left", "right", "right"],
    )

    # ── Risks ──
    risks = doc.add_section("risks", "Risk Register", role="body")
    risks.callout(
        variant="warning",
        title="EU Regulatory Risk",
        text=(
            "The European AI Act compliance deadline falls in Q2 2026. Our legal team estimates "
            "$40–60M in compliance costs and potential delays to three product lines."
        ),
    )
    risks.callout(
        variant="warning",
        title="Hardware Supply Chain",
        text=(
            "GPU availability remains constrained. Delivery lead times for the H200 cluster "
            "expansion have extended to 22 weeks, potentially delaying the AI platform scale-up."
        ),
    )

    # ── Outlook ──
    outlook = doc.add_section("outlook", "Q1 2026 Outlook", role="conclusion")
    outlook.paragraph(
        "We guide Q1 2026 revenue in the range of **$4.3B – $4.5B** (+22%–32% YoY), with "
        "operating margin of **30%–32%**. SaaS ARR is expected to reach **$1.15B** by end of Q1."
    )
    outlook.list(
        items=[
            {"text": "Launch AI Copilot v3 across all SaaS products (January 15)", "level": 0},
            {"text": "Complete EMEA data-centre expansion (February)", "level": 0},
            {"text": "Submit EU AI Act compliance documentation (March 31)", "level": 0},
            {"text": "Close hardware supply chain alternative (H100 backup)", "level": 0},
        ],
        ordered=True,
    )

    return doc


# ─────────────────────────────────────────────────────────
# 3. Legal Contract
# ─────────────────────────────────────────────────────────

def make_legal_contract() -> ANDFDocument:
    doc = ANDFDocument()
    doc.set_metadata(
        title="Software Licence and Services Agreement",
        subtitle="Enterprise SaaS Agreement — Confidential",
        authors=["Legal Department"],
        keywords=["contract", "licence", "SaaS", "enterprise"],
        category="Legal",
        status="final",
        version="3.2",
        license="Proprietary",
    )
    doc.set_theme("minimal")

    doc.set_ai(
        summary=(
            "Enterprise SaaS licence agreement between Acme Corp (Provider) and Beta Ltd (Customer). "
            "Covers a 3-year term, $2.4M total licence fee, SLA of 99.9% uptime, data processing "
            "terms under GDPR, and limitation of liability to 12 months of fees."
        ),
        key_points=[
            "Term: 3 years, auto-renews annually unless 90 days' notice given.",
            "Licence fee: $800,000/year payable annually in advance.",
            "SLA: 99.9% monthly uptime; service credits for breaches.",
            "Limitation of liability: 12 months of fees paid.",
            "Governing law: English law; courts of England and Wales.",
        ],
        topics=[
            {"label": "Contract Law", "confidence": 0.99},
            {"label": "SaaS Licensing", "confidence": 0.97},
            {"label": "Data Protection", "confidence": 0.88},
        ],
        reading_time_minutes=15,
        complexity="high",
    )

    # ── Parties ──
    parties = doc.add_section("parties", "Parties", role="body")
    parties.paragraph(
        "This Software Licence and Services Agreement (the **\"Agreement\"**) is entered into "
        "as of **1 March 2026** (the **\"Effective Date\"**) by and between:"
    )
    parties.table(
        caption="",
        headers=["", "Provider", "Customer"],
        rows=[
            ["Legal name", "Acme Corporation Ltd", "Beta Technologies Ltd"],
            ["Company no.", "12345678", "87654321"],
            ["Registered address", "1 Tech Lane, London, EC1A 1AA", "50 High Street, Manchester, M1 1AD"],
            ["Contact email", "legal@acme.example.com", "legal@beta.example.com"],
        ],
        align=["left", "left", "left"],
    )

    # ── Definitions ──
    defs = doc.add_section("definitions", "1. Definitions", role="body")
    defs.paragraph(
        "In this Agreement the following terms have the meanings set out below:"
    )
    defs.list(
        items=[
            {"text": "**\"Software\"** means Acme's cloud-based platform known as AcmeSuite.", "level": 0},
            {"text": "**\"Services\"** means implementation, support, and maintenance services.", "level": 0},
            {"text": "**\"Authorised Users\"** means the Customer's employees and contractors.", "level": 0},
            {"text": "**\"Confidential Information\"** means any non-public information disclosed.", "level": 0},
            {"text": "**\"Personal Data\"** has the meaning given in the UK GDPR.", "level": 0},
        ],
        ordered=False,
    )

    # ── Licence Grant ──
    licence = doc.add_section("licence", "2. Licence Grant", role="body")
    licence.paragraph(
        "Subject to the terms of this Agreement and payment of all fees, Acme grants to the "
        "Customer a **non-exclusive, non-transferable, revocable licence** to access and use "
        "the Software during the Term solely for the Customer's internal business purposes."
    )
    licence.callout(
        variant="error",
        title="Restrictions",
        text=(
            "The Customer must not: (a) sublicence or resell the Software; "
            "(b) reverse-engineer or decompile any part; (c) use the Software to develop a "
            "competing product; or (d) exceed the Authorised User limit specified in Schedule 1."
        ),
    )

    # ── Fees ──
    fees = doc.add_section("fees", "3. Fees and Payment", role="body")
    fees.table(
        caption="Schedule 1: Fee Schedule",
        headers=["Item", "Year 1", "Year 2", "Year 3"],
        rows=[
            ["Licence fee", "$800,000", "$800,000", "$800,000"],
            ["Implementation", "$150,000", "—", "—"],
            ["Training", "$30,000", "$15,000", "$15,000"],
            ["Support (24/7 Tier 1)", "Included", "Included", "Included"],
            ["**Annual total**", "**$980,000**", "**$815,000**", "**$815,000**"],
        ],
        align=["left", "right", "right", "right"],
    )
    fees.paragraph(
        "All fees are payable within **30 days** of invoice date. Late payments accrue interest "
        "at 4% per annum above the Bank of England base rate."
    )

    # ── SLA ──
    sla = doc.add_section("sla", "4. Service Level Agreement", role="body")
    sla.paragraph(
        "Acme shall use commercially reasonable efforts to ensure the Software is available "
        "**99.9% of each calendar month** (\"Uptime SLA\"), excluding scheduled maintenance "
        "windows notified at least 48 hours in advance."
    )
    sla.table(
        caption="Table 4: Service Credits",
        headers=["Monthly Uptime", "Credit (% of Monthly Fee)"],
        rows=[
            ["99.0% – 99.9%", "5%"],
            ["98.0% – 98.9%", "10%"],
            ["95.0% – 97.9%", "25%"],
            ["< 95.0%", "50%"],
        ],
        align=["left", "center"],
    )
    sla.callout(
        variant="info",
        title="Service Credit Cap",
        text="Service credits are the Customer's sole and exclusive remedy for uptime failures.",
    )

    # ── Data Protection ──
    data = doc.add_section("data", "5. Data Protection", role="body")
    data.paragraph(
        "Where Acme processes Personal Data on behalf of the Customer, it does so as a "
        "**data processor** (as defined in the UK GDPR). The Data Processing Addendum "
        "attached as Annex A forms part of this Agreement."
    )

    # ── Liability ──
    liability = doc.add_section("liability", "6. Limitation of Liability", role="body")
    liability.paragraph(
        "To the maximum extent permitted by law, each party's total aggregate liability "
        "to the other under or in connection with this Agreement shall not exceed the "
        "**fees paid or payable in the 12 months preceding the event giving rise to the claim**."
    )
    liability.callout(
        variant="warning",
        title="Exclusions",
        text=(
            "Neither party excludes liability for: death or personal injury caused by negligence; "
            "fraud or fraudulent misrepresentation; or any other liability that cannot be limited "
            "by applicable law."
        ),
    )

    # ── Term & Termination ──
    term = doc.add_section("term", "7. Term and Termination", role="body")
    term.paragraph(
        "This Agreement commences on the Effective Date and continues for **three (3) years** "
        "(the \"Initial Term\"). It then auto-renews for successive 12-month periods unless "
        "either party gives **90 days' written notice** of non-renewal."
    )

    # ── Governing Law ──
    gov = doc.add_section("governing-law", "8. Governing Law", role="body")
    gov.paragraph(
        "This Agreement and any disputes arising from it shall be governed by the laws of "
        "**England and Wales**. Each party irrevocably submits to the exclusive jurisdiction "
        "of the courts of England and Wales."
    )

    # ── Signatures ──
    sig = doc.add_section("signatures", "Signatures", role="body")
    sig.separator()
    sig.paragraph(
        "By signing below, the parties agree to be bound by the terms of this Agreement."
    )
    sig.table(
        caption="",
        headers=["", "Provider", "Customer"],
        rows=[
            ["Signature", "___________________", "___________________"],
            ["Print name", "___________________", "___________________"],
            ["Title", "___________________", "___________________"],
            ["Date", "___________________", "___________________"],
        ],
        align=["left", "left", "left"],
    )

    return doc


# ─────────────────────────────────────────────────────────
# 4. Technical Manual
# ─────────────────────────────────────────────────────────

def make_technical_manual() -> ANDFDocument:
    doc = ANDFDocument()
    doc.set_metadata(
        title="AcmeSuite API — Developer Reference",
        subtitle="REST API v3.0 Integration Guide",
        authors=["Developer Relations Team"],
        keywords=["API", "REST", "integration", "developer", "reference"],
        category="Technical Documentation",
        status="published",
        version="3.0.1",
        license="Apache 2.0",
    )
    doc.set_theme("default")

    doc.set_ai(
        summary=(
            "Developer reference for the AcmeSuite REST API v3.0. Covers authentication (API keys "
            "and OAuth 2.0), core endpoints, rate limiting, error codes, webhooks, and SDK usage."
        ),
        key_points=[
            "Authentication: API key (header) or OAuth 2.0 client credentials.",
            "Base URL: https://api.acmesuite.example.com/v3",
            "Rate limit: 1000 requests/minute per API key.",
            "All timestamps are UTC ISO 8601.",
            "Pagination uses cursor-based approach.",
        ],
        topics=[
            {"label": "REST APIs", "confidence": 0.99},
            {"label": "Authentication", "confidence": 0.95},
            {"label": "Developer Documentation", "confidence": 0.97},
        ],
        reading_time_minutes=20,
        complexity="high",
        questions_answered=[
            "How do I authenticate with the API?",
            "What are the rate limits?",
            "How do I handle pagination?",
            "How do webhooks work?",
        ],
    )

    # ── Overview ──
    overview = doc.add_section("overview", "1. Overview", role="introduction")
    overview.paragraph(
        "The AcmeSuite REST API provides programmatic access to all platform resources. "
        "It follows REST conventions and returns JSON responses. All API calls must be made "
        "over **HTTPS**; HTTP calls will be rejected with `301 Moved Permanently`."
    )
    overview.callout(
        variant="info",
        title="Base URL",
        text="https://api.acmesuite.example.com/v3",
    )
    overview.table(
        caption="Table 1: API Characteristics",
        headers=["Property", "Value"],
        rows=[
            ["Protocol", "HTTPS only"],
            ["Format", "JSON (UTF-8)"],
            ["Authentication", "API Key or OAuth 2.0"],
            ["Rate limit", "1,000 req/min per key"],
            ["Timestamps", "ISO 8601 UTC"],
            ["Pagination", "Cursor-based"],
            ["Idempotency", "Supported via `Idempotency-Key` header"],
        ],
        align=["left", "left"],
    )

    # ── Authentication ──
    auth = doc.add_section("auth", "2. Authentication", role="body")

    api_key_sec = auth.add_subsection("auth-apikey", "2.1 API Key", role="body")
    api_key_sec.paragraph(
        "Pass your API key in the `Authorization` header as a Bearer token:"
    )
    api_key_sec.code(
        code=(
            "curl -X GET https://api.acmesuite.example.com/v3/users \\\n"
            "  -H 'Authorization: Bearer YOUR_API_KEY' \\\n"
            "  -H 'Content-Type: application/json'"
        ),
        language="bash",
        caption="API Key authentication",
    )
    api_key_sec.callout(
        variant="warning",
        title="Keep Your Key Secret",
        text=(
            "Never expose API keys in client-side code or public repositories. "
            "Rotate keys immediately if they are compromised via the dashboard."
        ),
    )

    oauth_sec = auth.add_subsection("auth-oauth", "2.2 OAuth 2.0 Client Credentials", role="body")
    oauth_sec.paragraph(
        "For server-to-server integrations, use the OAuth 2.0 client credentials flow:"
    )
    oauth_sec.code(
        code=(
            "# Step 1: Exchange credentials for access token\n"
            "curl -X POST https://api.acmesuite.example.com/v3/oauth/token \\\n"
            "  -d 'grant_type=client_credentials' \\\n"
            "  -d 'client_id=YOUR_CLIENT_ID' \\\n"
            "  -d 'client_secret=YOUR_CLIENT_SECRET' \\\n"
            "  -d 'scope=read:users write:documents'\n\n"
            "# Response\n"
            "{\n"
            '  "access_token": "eyJhbGci...",\n'
            '  "token_type": "Bearer",\n'
            '  "expires_in": 3600\n'
            "}"
        ),
        language="bash",
        caption="OAuth 2.0 token exchange",
    )

    # ── Core Endpoints ──
    endpoints = doc.add_section("endpoints", "3. Core Endpoints", role="body")
    endpoints.paragraph(
        "All endpoints return a JSON object with `data`, `meta`, and optionally `errors` keys."
    )

    users_sec = endpoints.add_subsection("ep-users", "3.1 Users", role="body")
    users_sec.table(
        caption="Table 2: User Endpoints",
        headers=["Method", "Path", "Description"],
        rows=[
            ["GET", "/users", "List all users (paginated)"],
            ["POST", "/users", "Create a new user"],
            ["GET", "/users/{id}", "Get user by ID"],
            ["PATCH", "/users/{id}", "Update user fields"],
            ["DELETE", "/users/{id}", "Deactivate a user"],
        ],
        align=["left", "left", "left"],
    )
    users_sec.code(
        code=(
            "# Create user\n"
            "POST /v3/users\n"
            "Content-Type: application/json\n\n"
            "{\n"
            '  "email": "alice@example.com",\n'
            '  "name": "Alice Johnson",\n'
            '  "role": "editor",\n'
            '  "teams": ["team_abc123"]\n'
            "}\n\n"
            "# Response 201 Created\n"
            "{\n"
            '  "data": {\n'
            '    "id": "usr_xyz789",\n'
            '    "email": "alice@example.com",\n'
            '    "name": "Alice Johnson",\n'
            '    "role": "editor",\n'
            '    "created_at": "2026-03-02T10:00:00Z"\n'
            "  }\n"
            "}"
        ),
        language="json",
        caption="Create user request and response",
        line_numbers=False,
    )

    docs_sec = endpoints.add_subsection("ep-docs", "3.2 Documents", role="body")
    docs_sec.table(
        caption="Table 3: Document Endpoints",
        headers=["Method", "Path", "Description"],
        rows=[
            ["GET", "/documents", "List documents"],
            ["POST", "/documents", "Upload a new document"],
            ["GET", "/documents/{id}", "Get document metadata"],
            ["GET", "/documents/{id}/content", "Download document content"],
            ["DELETE", "/documents/{id}", "Delete a document"],
        ],
        align=["left", "left", "left"],
    )

    # ── Rate Limiting ──
    rate = doc.add_section("rate-limits", "4. Rate Limiting", role="body")
    rate.paragraph(
        "API keys are limited to **1,000 requests per minute**. Enterprise plans have "
        "configurable limits up to 10,000 req/min. Rate limit information is returned in "
        "every response via headers:"
    )
    rate.code(
        code=(
            "X-RateLimit-Limit: 1000\n"
            "X-RateLimit-Remaining: 874\n"
            "X-RateLimit-Reset: 1740920460"
        ),
        language="http",
        caption="Rate limit response headers",
    )
    rate.callout(
        variant="warning",
        title="429 Too Many Requests",
        text=(
            "When the rate limit is exceeded the API returns HTTP 429. "
            "Implement exponential back-off: wait 2^n seconds (n = retry attempt, max 60s)."
        ),
    )

    # ── Error Codes ──
    errors = doc.add_section("errors", "5. Error Reference", role="body")
    errors.table(
        caption="Table 4: HTTP Error Codes",
        headers=["Code", "Name", "Description"],
        rows=[
            ["400", "Bad Request", "Malformed request body or missing required field"],
            ["401", "Unauthorised", "Invalid or missing API key / token"],
            ["403", "Forbidden", "Authenticated but insufficient permissions"],
            ["404", "Not Found", "Resource does not exist"],
            ["409", "Conflict", "Duplicate resource (e.g., email already registered)"],
            ["422", "Unprocessable", "Validation error on field values"],
            ["429", "Too Many Requests", "Rate limit exceeded"],
            ["500", "Server Error", "Unexpected server error — contact support"],
            ["503", "Service Unavailable", "Planned maintenance or outage"],
        ],
        align=["center", "left", "left"],
    )
    errors.code(
        code=(
            "# Error response shape\n"
            "{\n"
            '  "errors": [\n'
            "    {\n"
            '      "code": "VALIDATION_ERROR",\n'
            '      "field": "email",\n'
            '      "message": "Must be a valid email address"\n'
            "    }\n"
            "  ]\n"
            "}"
        ),
        language="json",
        caption="Standard error response format",
    )

    # ── Webhooks ──
    webhooks = doc.add_section("webhooks", "6. Webhooks", role="body")
    webhooks.paragraph(
        "Register a webhook endpoint to receive real-time push notifications when events "
        "occur. AcmeSuite signs each request with a secret so you can verify authenticity."
    )
    webhooks.list(
        items=[
            {"text": "`document.created` — new document uploaded", "level": 0},
            {"text": "`document.updated` — document content modified", "level": 0},
            {"text": "`user.invited` — new user invited to workspace", "level": 0},
            {"text": "`user.deactivated` — user account deactivated", "level": 0},
            {"text": "`payment.succeeded` — subscription payment processed", "level": 0},
            {"text": "`payment.failed` — payment attempt failed", "level": 0},
        ],
        ordered=False,
    )
    webhooks.code(
        code=(
            "import hmac, hashlib\n\n"
            "def verify_webhook(payload_bytes: bytes, signature: str, secret: str) -> bool:\n"
            "    \"\"\"Verify Acme webhook signature.\"\"\"\n"
            "    expected = hmac.new(\n"
            "        secret.encode(),\n"
            "        payload_bytes,\n"
            "        hashlib.sha256,\n"
            "    ).hexdigest()\n"
            "    return hmac.compare_digest(f'sha256={expected}', signature)\n\n"
            "# In your request handler:\n"
            "sig = request.headers['X-Acme-Signature']\n"
            "if not verify_webhook(request.body, sig, WEBHOOK_SECRET):\n"
            "    return 401"
        ),
        language="python",
        caption="Webhook signature verification (Python)",
    )

    # ── SDK ──
    sdk = doc.add_section("sdk", "7. Python SDK", role="body")
    sdk.paragraph(
        "The official Python SDK wraps the REST API with a Pythonic interface. "
        "Install via pip:"
    )
    sdk.code(code="pip install acmesuite", language="bash")
    sdk.code(
        code=(
            "from acmesuite import AcmeClient\n\n"
            "client = AcmeClient(api_key='YOUR_API_KEY')\n\n"
            "# List users\n"
            "users = client.users.list(limit=50)\n"
            "for user in users:\n"
            "    print(user.name, user.email)\n\n"
            "# Upload document\n"
            "with open('report.pdf', 'rb') as f:\n"
            "    doc = client.documents.upload(\n"
            "        file=f,\n"
            "        name='Q4 Report',\n"
            "        folder='finance',\n"
            "    )\n"
            "print(f'Uploaded: {doc.id}')"
        ),
        language="python",
        caption="Python SDK quick start",
    )
    sdk.callout(
        variant="tip",
        title="Pagination Helper",
        text=(
            "All list methods return an auto-paginating iterator. "
            "Use `client.users.list_all()` to lazily fetch every page."
        ),
    )

    return doc


# ─────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────

def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))

    examples = [
        ("research_paper.andf", "Research Paper", make_research_paper),
        ("business_report.andf", "Business Report", make_business_report),
        ("legal_contract.andf", "Legal Contract", make_legal_contract),
        ("technical_manual.andf", "Technical Manual", make_technical_manual),
    ]

    for filename, label, factory in examples:
        path = os.path.join(out_dir, filename)
        print(f"Generating {label}...")
        doc = factory()
        doc.save(path)
        size_kb = os.path.getsize(path) // 1024
        print(f"  → {path}  ({size_kb} KB)")

    print("\nAll examples generated successfully!")
    print("Open any .andf file in your browser to see the PDF-like viewer.")


if __name__ == "__main__":
    main()
