import os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_NAME = "Luis Gustavo Bonfim Ciaramicoli - AI Engineer – Full-Stack para Aplicações com IA Generativa"
HTML_PATH = BASE_DIR / f"{OUTPUT_NAME}.html"
PDF_PATH = BASE_DIR / f"{OUTPUT_NAME}.pdf"

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Technical Case Solution — AI Engineer — Artefact</title>
<style>
  @page {
    size: A4;
    margin: 20mm;
    @bottom-right {
      content: counter(page);
    }
  }
  body {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    color: #1a1a1a;
    line-height: 1.6;
    font-size: 11pt;
    margin: 0;
    padding: 0;
  }
  .header-cover {
    border-bottom: 3px solid #d97706;
    padding-bottom: 25px;
    margin-bottom: 30px;
  }
  .badge {
    display: inline-block;
    background-color: #fef3c7;
    color: #92400e;
    font-size: 9pt;
    font-weight: bold;
    padding: 4px 10px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
  }
  h1 {
    font-size: 24pt;
    color: #111827;
    margin: 0 0 10px 0;
    line-height: 1.2;
  }
  .subtitle {
    font-size: 13pt;
    color: #4b5563;
    margin: 0 0 15px 0;
  }
  .meta-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    font-size: 10pt;
    color: #374151;
    background: #f9fafb;
    padding: 12px 16px;
    border-radius: 6px;
    border: 1px solid #e5e7eb;
  }
  h2 {
    font-size: 15pt;
    color: #1f2937;
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 6px;
    margin-top: 30px;
    margin-bottom: 12px;
  }
  h3 {
    font-size: 12pt;
    color: #374151;
    margin-top: 18px;
    margin-bottom: 8px;
  }
  p {
    margin: 0 0 12px 0;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    font-size: 10pt;
  }
  th, td {
    border: 1px solid #d1d5db;
    padding: 8px 10px;
    text-align: left;
  }
  th {
    background-color: #f3f4f6;
    font-weight: 600;
    color: #1f2937;
  }
  tr:nth-child(even) {
    background-color: #f9fafb;
  }
  pre {
    background-color: #1e293b;
    color: #f8fafc;
    padding: 12px;
    border-radius: 6px;
    font-size: 9pt;
    overflow-x: auto;
    font-family: 'Courier New', Courier, monospace;
    margin: 12px 0;
  }
  code {
    background-color: #f3f4f6;
    color: #b45309;
    padding: 2px 5px;
    border-radius: 4px;
    font-size: 9.5pt;
    font-family: 'Courier New', Courier, monospace;
  }
  pre code {
    background-color: transparent;
    color: inherit;
    padding: 0;
  }
  .callout {
    background-color: #eff6ff;
    border-left: 4px solid #3b82f6;
    padding: 12px 16px;
    margin: 16px 0;
    border-radius: 0 6px 6px 0;
    font-size: 10pt;
  }
  .callout-warning {
    background-color: #fffbeb;
    border-left: 4px solid #f59e0b;
  }
  ul, ol {
    margin: 0 0 12px 0;
    padding-left: 20px;
  }
  li {
    margin-bottom: 4px;
  }
  .page-break {
    page-break-before: always;
  }
</style>
</head>
<body>

<div class="header-cover">
  <div class="badge">Artefact Selection Process — Stage 1 Technical Case</div>
  <h1>Empório da Música — AI Customer Support Agent</h1>
  <div class="subtitle">A Production-Grade, Full-Stack ReAct & Vector RAG Architecture</div>
  
  <div class="meta-grid">
    <div><strong>Candidate:</strong> Luis Gustavo Bonfim Ciaramicoli</div>
    <div><strong>Position:</strong> AI Engineer – Full-Stack para Aplicações com IA Generativa</div>
    <div><strong>Location:</strong> Artefact Brasil (Home Office)</div>
    <div><strong>Repository:</strong> <a href="https://github.com/luisciaramicoli/Artefact">github.com/luisciaramicoli/Artefact</a></div>
  </div>
</div>

<h2>1. Executive Summary & Problem Formulation</h2>
<p>
  <strong>Empório da Música</strong> is a premier musical instruments store established in 2008 in Campo Grande/MS.
  The human customer service team was overburdened with high-volume repetitive queries regarding product pricing,
  inventory availability, order status tracking, and store policies (returns, warranties, operating hours).
</p>
<p>
  To solve this challenge, I designed and developed a <strong>full-stack, autonomous AI agent in Python</strong>
  featuring an interactive <strong>React 19 web application</strong>, a <strong>Rich terminal CLI</strong>, and a robust
  hybrid orchestration engine combining <strong>Google Gemini (Tool Calling)</strong>, <strong>Qdrant (Vector RAG)</strong>,
  and <strong>SQLite / SQLAlchemy (Deterministic Relational Queries)</strong>.
</p>

<div class="callout">
  <strong>Key Mandatory Technical Constraint:</strong> Python as the primary language.<br>
  <strong>Architecture Delivered:</strong> 100% Python backend & AI engine (FastAPI + SQLAlchemy + Qdrant + Google GenAI SDK)
  paired with a modern, responsive React frontend demonstrating end-to-end Full-Stack AI engineering excellence.
</div>

<h2>2. Architectural Decisions & Technical Justifications</h2>

<table>
  <thead>
    <tr>
      <th>Component</th>
      <th>Technology Selected</th>
      <th>Technical Justification</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Agent Paradigm</strong></td>
      <td><strong>Hybrid Tool Calling (ReAct) + RAG</strong></td>
      <td>
        <strong>Pure RAG fails on math & inventory:</strong> LLMs hallucinate stock counts and promotional calculations.
        <strong>Pure SQL fails on company policies:</strong> Cannot interpret unstructured legal clauses and returns.
        The hybrid architecture allows the LLM to deterministically query SQL for numbers and semantically query Qdrant for policies.
      </td>
    </tr>
    <tr>
      <td><strong>LLM Provider</strong></td>
      <td><strong>Google Gemini (Gemini 3.1 Flash Lite / 2.5 Flash)</strong></td>
      <td>
        Fast inference latency (&lt; 1.5s), native schema-based function calling, excellent adherence to system prompts and Portuguese Brazilian nuances, and robust rate-limit resilience.
      </td>
    </tr>
    <tr>
      <td><strong>Vector Store</strong></td>
      <td><strong>Qdrant (Embedded Mode + Docker Server)</strong></td>
      <td>
        Qdrant provides state-of-the-art HNSW vector indexing. Using Qdrant's embedded client allows any reviewer to run the application with <strong>zero external dependencies</strong>, while maintaining 100% cloud/server parity.
      </td>
    </tr>
    <tr>
      <td><strong>Embeddings</strong></td>
      <td><strong>Google <code>gemini-embedding-001</code></strong></td>
      <td>
        Generates dense 3072-dimensional vector embeddings, delivering outstanding semantic retrieval accuracy for Portuguese legal and operational texts.
      </td>
    </tr>
    <tr>
      <td><strong>Database & Storage</strong></td>
      <td><strong>SQLite + SQLAlchemy</strong></td>
      <td>
        Zero configuration required for local evaluation. Persists relational tables (Categories, Products, Customers, Orders, Promotions) and conversation memory (Sessions and Messages). Easily swappable to PostgreSQL.
      </td>
    </tr>
    <tr>
      <td><strong>Frontend UI</strong></td>
      <td><strong>React 19 + Vite + Tailwind CSS</strong></td>
      <td>
        Highlights full-stack capabilities with real-time tool inspection badges (showing evaluators exactly when and why tools are triggered), quick suggestion chips, and responsive UX.
      </td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<h2>3. Deterministic Tools & Ingestion Pipeline</h2>

<h3>3.1 Relational Data Ingestion (<code>data/*.csv</code>)</h3>
<p>
  All six CSV files were parsed, validated, and normalized into relational tables with foreign-key integrity:
</p>
<ul>
  <li><code>categories</code> (9 music instrument categories)</li>
  <li><code>products</code> (65 items with prices, specifications, and active/discontinued statuses)</li>
  <li><code>promotions</code> (25 seasonal campaigns, with <code>is_active</code> boolean tracking)</li>
  <li><code>orders</code> and <code>order_items</code> (tracking codes, fulfillment dates, delivery estimates, cancellation notes)</li>
  <li><code>customers</code> (identifying contact information and delivery locations)</li>
</ul>

<h3>3.2 Policy Extraction & Semantic Vector Chunking (<code>políticas_da_loja.pdf</code>)</h3>
<p>
  The internal manual was segmented into 10 structured chunks aligned with company chapters (About Us, Scope Limits,
  Operating Hours, Payment & Installment Terms, Returns & Remorse, Shipping & Delivery, Promotions, WhatsApp Tone, Warranty, LGPD).
  These chunks were embedded via <code>gemini-embedding-001</code> and stored in Qdrant with Cosine distance metric.
</p>

<h3>3.3 Agent Tool Definitions</h3>
<p>The Gemini agent has access to five deterministic tools:</p>
<ol>
  <li><code>search_store_policies(query: str)</code>: Semantic search across Qdrant vector database for business rules, returns, and hours.</li>
  <li><code>query_products(category_name, max_price, min_price, search_text, in_stock_only)</code>: Dynamic SQL filtering with automatic 5% PIX discount calculation and active promo detection.</li>
  <li><code>get_product_details(product_name_or_id)</code>: In-depth technical specification lookup, current stock, and detection of past expired promotions.</li>
  <li><code>check_order_status(order_id, tracking_code, customer_identifier)</code>: Real-time query of order status, delivery dates, internal dispatch notes, and item breakdown.</li>
  <li><code>get_store_info()</code>: Instant retrieval of physical store address, WhatsApp contact, and scope rules.</li>
</ol>

<h2>4. Guardrails & Persona Engineering</h2>
<div class="callout callout-warning">
  <strong>Strict Scope Guardrail (The Golden Rule):</strong><br>
  Empório da Música exclusively sells musical instruments. <strong>The store does NOT sell accessories</strong> (strings, picks, cables, straps, cases, pedals, or standalone amplifiers).<br>
  The agent strictly enforces this boundary: inquiries regarding accessories are warmly acknowledged, the scope limit is explained, and the customer is courteously redirected to local music accessory shops in Campo Grande.
</div>

<ul>
  <li><strong>Truthfulness Policy:</strong> The agent never hallucinates pricing, stock availability, or order statuses. It is mandated to query the system before stating numbers.</li>
  <li><strong>Expired Promotion Transparency:</strong> If a customer mentions an old promotion (such as the expired 12% Takamine discount), the agent transparently clarifies that the seasonal campaign concluded, presenting current table pricing and standard payment conditions.</li>
  <li><strong>Consumer Defense Code (CDC):</strong> Accurately enforces the 7-day remorse return window for remote purchases, store-funded reverse logistics, and 10-business-day refund timelines.</li>
</ul>

<div class="page-break"></div>

<h2>5. Evaluated Test Scenarios & Transcripts</h2>
<p>
  Six distinct real-world scenarios were executed and recorded against the live system. Full transcripts are documented in <code>examples/conversations/</code>:
</p>

<h3>Scenario 1: Product Catalog with Price Filter</h3>
<p><em>Prompt:</em> "Quais opções de violões disponíveis custando até R$1000?"</p>
<p>
  <strong>Tool Executed:</strong> <code>query_products(category_name='Violões', max_price=1000)</code><br>
  <strong>Result:</strong> Agent returned a structured markdown comparison of available in-stock guitars (Tagima Memphis AC-39, Rozini RC-104, Shelby SN-100, Giannini GF-1R, Yamaha C40, Giannini GN-15), detailing table prices, 5% PIX discounted prices, string types (nylon vs. steel), and 12x credit card installment terms.
</p>

<h3>Scenario 2: Physical Store Address & Hours</h3>
<p><em>Prompt:</em> "Qual o endereço da loja física e quais os horários de funcionamento no sábado e na semana?"</p>
<p>
  <strong>Result:</strong> Accurately informed: Rua 14 de Maio, 3200 — Centro, Campo Grande - MS; Monday–Friday 09:00 to 18:00; Saturdays 09:00 to 13:00; Sundays and holidays closed.
</p>

<h3>Scenario 3: Specific Product Price & Expired Promotion</h3>
<p><em>Prompt:</em> "Quanto custa o Takamine GD20? Vi em algum lugar que tinha promoção dele, ainda está com desconto?"</p>
<p>
  <strong>Tool Executed:</strong> <code>get_product_details('Takamine GD20')</code><br>
  <strong>Result:</strong> Identified product #95 (Takamine GD20 Dreadnought Natural, R$ 2.199,00; R$ 2.089,05 on PIX; 5 units in stock). Crucially, the agent identified that promotion #4 ("Oferta Especial", 12% off) had <code>is_active=0</code> (expired), explaining with total transparency that the seasonal promotion had ended.
</p>

<h3>Scenario 4: Return Policy (Remorse / CDC)</h3>
<p><em>Prompt:</em> "Comprei um instrumento pelo WhatsApp faz 4 dias e me arrependi da compra. Posso devolver? Como funciona o frete e o reembolso?"</p>
<p>
  <strong>Tool Executed:</strong> <code>search_store_policies('devolução por arrependimento prazo frete reembolso')</code><br>
  <strong>Result:</strong> Applied Section 4.1 of the policy manual: confirmed eligibility (within 7 days of delivery), required original packaging and accessories, confirmed that reverse shipping is 100% covered by the store, and stated the 10-business-day refund timeframe.
</p>

<h3>Scenario 5: Real-time Order Tracking</h3>
<p><em>Prompt:</em> "Olá! Gostaria de acompanhar a entrega do meu pedido número 1. Qual o status e o código de rastreamento dele?"</p>
<p>
  <strong>Tool Executed:</strong> <code>check_order_status(order_id=1)</code><br>
  <strong>Result:</strong> Found Order #1 for customer Maria Silva (Martin D-28 Dreadnought Natural, total R$ 11.499,00 paid via PIX, status "Delivered", tracking code <code>BRAB1234567BR</code>).
</p>

<h3>Scenario 6: Out-of-Scope Accessory Refusal</h3>
<p><em>Prompt:</em> "Vocês vendem encordoamento de aço para violão e palhetas avulsas?"</p>
<p>
  <strong>Result:</strong> Guardrail triggered. The agent warmly explained the store's strict specialization in instruments, declined the accessory sale, and recommended partner stores in Campo Grande.
</p>

<h2>6. AI Coding Assistant Workflow</h2>
<p>
  In full transparency according to Artefact's evaluation criteria, I utilized <strong>Google Antigravity / Gemini</strong>
  as a pair-programming partner. The collaborative division of labor:
</p>
<ul>
  <li><strong>Architectural Strategy:</strong> Formulating the hybrid deterministic SQL + semantic vector RAG architecture to eliminate numerical hallucination.</li>
  <li><strong>Typing & Compatibility Debugging:</strong> Diagnosed a subtle Python 3.14 typing edge case where the Google GenAI SDK type checker rejected integer inputs into <code>Optional[float]</code> parameters, successfully resolving it via <code>Union[int, float, None]</code>.</li>
  <li><strong>Automated Testing & Scaffolding:</strong> Accelerated Pytest fixtures, relational database seeding, and React 19 UI component scaffolding.</li>
</ul>

<h2>7. Known Limitations & Production Roadmap</h2>
<ul>
  <li><strong>Hybrid Lexical Search:</strong> Combine dense Qdrant embeddings with sparse BM25 (Reciprocal Rank Fusion) for alphanumeric product codes.</li>
  <li><strong>Multi-Agent Hierarchy:</strong> Decompose duties into dedicated subagents (Sales, Logistics, Policies) orchestrated via LangGraph.</li>
  <li><strong>Distributed Infrastructure:</strong> Transition SQLite to Managed PostgreSQL with PgBouncer, and local Qdrant to Qdrant Cloud.</li>
</ul>

<div style="margin-top: 40px; border-top: 1px solid #e5e7eb; padding-top: 15px; font-size: 9.5pt; color: #6b7280; text-align: center;">
  Technical Case Submission • Luis Gustavo Bonfim Ciaramicoli • Artefact AI Engineer Selection Process
</div>

</body>
</html>
"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated HTML at {HTML_PATH}")
print("Converting to PDF via LibreOffice...")

cmd = [
    "libreoffice",
    "--headless",
    "--convert-to",
    "pdf:writer_web_pdf_Export",
    str(HTML_PATH),
    "--outdir",
    str(BASE_DIR)
]

res = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)

if PDF_PATH.exists():
    print(f"Successfully generated PDF at: {PDF_PATH}")
    print(f"PDF size: {PDF_PATH.stat().st_size} bytes")
else:
    print("PDF generation failed.")
