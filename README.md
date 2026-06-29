# HappyMan POS

A local-first, bilingual point-of-sale system in development for HappyMan Sweets, a family-run sweet shop business operating two locations in Tamil Nadu, India. Designed to work entirely offline on a Raspberry Pi + tablet setup, with optional cloud sync planned for multi-shop deployments.

This is both a real product (being built for my family's two shops) and a portfolio project demonstrating end-to-end web development, relational database design, and small-scale hardware deployment.

---

## Why this project exists

My father runs two traditional sweet shops in India. Like most small Indian retailers, daily sales are tracked on paper, prices are memorized by staff, and reporting at month-end means manually flipping through ledger books.

Off-the-shelf POS solutions (Vyapar, Marg, PetPooja) didn't fit because:

- Staff speak Tamil; most software is English-only
- Products are sold by weight, pieces, AND packets simultaneously
- Shop has unreliable internet — cloud-only POS would block sales during outages
- Subscription fees over multiple years exceed a custom-build cost

So I'm building one. Offline-first, bilingual, tuned to the shop's actual workflow.

---

## Current state

### Working today

- Touch-friendly cart organized by category, with Tamil + English labels on every product
- Flexible quantities — sells products by weight, pieces, or packets in one cart
- Cash + GPay payments with denomination shortcut buttons (₹100, ₹200, ₹500 for fast tender)
- Server-side bill numbering with shop prefix (HM1-1, HM1-2, etc.) — designed for GST compliance
- Persistent sales storage in SQLite; survives reboots and tablet swaps
- Database-backed product catalog and category structure (28 products, 6 categories, bilingual)
- Pydantic-validated API for all incoming sale data
- iPad tested over WiFi hotspot, confirmed end-to-end round-trip from browser to SQLite

### In progress

- Excel export endpoint with multi-sheet reports (Summary, Sales List, Items Detail)
- Daily / weekly / monthly report generation
- Backend status indicator in UI (to prevent silent failures)

### Planned for v1 launch

- Login / shop identification flow
- Raspberry Pi deployment + systemd service
- Home testing phase with my parents before any shop deployment

### Planned for v1.5 and beyond

- Stock entry module (tracking what's sent from manufacturing to each shop)
- Expense tracking module (utility bills, salaries, supplies)
- Cloud product sync via Supabase
- Multi-shop consolidated dashboard (Streamlit + Power BI for portfolio)
- Thermal printer integration (USB ESC/POS)
- Refund / void UI (schema already supports this)

---

## Architecture

```
┌─────────────────────────────────────────┐
│                                          │
│   Tablet  ◄─── WiFi ───►  Raspberry Pi  │
│   Browser                  ├─ Python    │
│   HTML/JS                  ├─ FastAPI   │
│                            ├─ SQLite    │
│                            └─ Printer*  │
│                                          │
│   (Same WiFi · No internet required)    │
│                                          │
└─────────────────────────────────────────┘

* Printer planned for v1.5
```

**Tablet** runs only a browser. All business logic lives on the Pi. Sales are written to a SQLite file on the Pi's SD card — durable across reboots and tablet swaps.

Each shop has its own independent Pi + database. Cloud sync (planned for v1.5) will unify product data and enable consolidated reporting, while preserving offline operation between syncs.

---

## Tech stack

**Frontend:** Vanilla HTML, CSS, and JavaScript. No framework. Intentional choice — the UI is simple enough that React/Vue would have been overkill, and vanilla JS forced me to learn the fundamentals properly.

**Backend:** Python 3.11, FastAPI for routing and async support, Pydantic for runtime validation of incoming sale data, uvicorn as the ASGI server.

**Database:** SQLite. One file per shop. Schema designed for analytical queries (proper foreign keys, normalized sales/sale_items tables, REAL for money, refund/void columns built in from the start).

**Reporting:** openpyxl for Excel export (in progress). Power BI for portfolio dashboards reading from the same SQLite layer.

**Deployment (planned):** Raspberry Pi 5 (or 4) running Raspberry Pi OS. uvicorn served as a systemd service for auto-start on boot. WiFi router at the shop creates the local network; no ISP plan required for the POS itself.

**Future infrastructure (v1.5+):** Supabase as cloud master for product data and sales sync. Each shop continues to operate offline-first.

---

## Project structure

```
HappyManPos/
├── app/
│   ├── db/
│   │   ├── database.py       # SQLite connection + queries
│   │   ├── schema.sql        # Table definitions
│   │   ├── seed_data.json    # Initial categories and products
│   │   └── setup_db.py       # Initial DB creation + seeding
│   ├── frontend/             # HTML/CSS/JS — served by uvicorn in production
│   ├── config.py             # DB path, shop ID, etc.
│   ├── main.py               # FastAPI app + routes
│   ├── models.py             # Pydantic models (Transaction, CategorySeed, ProductSeed)
│   └── sales_report.py       # Excel report generation (in progress)
├── data/                     # SQLite database lives here (gitignored)
├── requirements.txt
└── README.md
```

---

## Running locally

### Prerequisites

- Python 3.11 (recommended via Conda)
- Git
- A modern browser

### Setup

```bash
# Clone
git clone https://github.com/devayani24/HappyMan.git
cd HappyMan

# Create conda environment
conda create -n happyman python=3.11
conda activate happyman

# Install dependencies
pip install -r requirements.txt

# Initialize database (creates SQLite file, seeds products and categories)
python -m app.db.setup_db

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend serves the API at `http://localhost:8000`. Interactive API docs are available at `http://localhost:8000/docs`.

For frontend development, use VS Code's Live Server extension on `app/frontend/main.html` (typically `http://localhost:5500` or `:5502`). This gives auto-reload on frontend changes.

### Testing on a tablet (same WiFi)

The frontend auto-detects the API base URL from `window.location.hostname`, so the tablet just needs to reach the laptop on the same network:

1. Find your laptop's local IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. Make sure the laptop's firewall allows inbound on ports 5500/5502 and 8000
3. On the tablet's browser, navigate to `http://YOUR_LAPTOP_IP:5502/...`

Some home WiFi networks (especially ISP-managed routers in apartments) enable client isolation, preventing devices from talking to each other. If the tablet can't reach the laptop, use a phone hotspot for testing — connect both devices to the same hotspot.

---

## Deploying to Raspberry Pi

Planned deployment flow (not yet executed):

1. Flash Raspberry Pi OS to SD card using Raspberry Pi Imager (configure WiFi + SSH in the imager's settings)
2. Boot the Pi, SSH in
3. Clone this repo, set up Python, install dependencies
4. Configure uvicorn to serve both API and frontend
5. Create a systemd service so uvicorn auto-starts on boot
6. Note the Pi's IP address; staff tablet connects to it via local WiFi

Hardware cost estimate (Australian retailers):

- Raspberry Pi 5 (8GB): ~$135 AUD
- Power supply, case, SD card, cooler: ~$75 AUD
- Tablet: family-owned or budget Android (~$200 AUD if buying new)

Total under $250 AUD per shop, versus $500+ AUD for a Windows touch POS system.

---

## Engineering decisions worth explaining

A few design choices that took thought, in case you're curious (or interviewing me).

### Local-first, not cloud-first

The shop's internet is unreliable. A cloud-only POS would block sales whenever the connection drops. Local SQLite on the Pi keeps the system running offline; cloud sync is layered on top (v1.5) for product updates and consolidated reporting, but is never on the critical path for a sale.

### localStorage as cache, not source of truth

The browser uses localStorage to render the cart and persist temporary state during a sale. The Pi's SQLite is the durable source of truth for completed sales. This separation prevents lost data when a tablet is replaced and avoids browser storage quirks (Safari aggressively clears localStorage).

### Pydantic models as the API contract

Every `/save-sale` request is validated against a Pydantic `Transaction` model before any business logic runs. Type errors, missing fields, and invalid enum values are rejected with detailed 422 responses, never reaching the SQL layer. The same pattern is used for seed data loading: JSON is validated against a `SeedData` model before any database inserts.

### Server-side bill number generation

Bill numbers are assigned by the server at the moment of save, not computed on the client. This prevents collisions when multiple devices submit sales (a real bug I hit during iPad testing) and ensures the database is the single source of truth for bill sequencing. Numbers are continuous per shop (HM1-1, HM1-2, etc.) which is required for GST compliance in India.

### Two-table sales schema with refund/void support built in

Sales and sale_items are separated (not stored as nested JSON in one row), making analytical queries straightforward: top products by month, average ticket size, peak hours — all expressible as standard SQL joins. Refund and void columns (`is_void`, `transaction_type`, `refund_for_bill`) were added to the schema early, even though the UI for them is deferred to v1.5. The schema is GST-compliant from day one.

### Pi + tablet over a touch PC

A tablet alone can't run Python. A Windows touch PC + monitor would be substantially more expensive than a Raspberry Pi + family-owned tablet. The cheaper setup validates the workflow before committing to expensive hardware. Same software architecture either way.

### Phased rollout: home then shop trial then full production

The plan is to test at home first (my parents enter previous day's sales from paper records), then move to shop shadow testing (staff uses POS while keeping paper records as backup), then full production once reliability is proven. This manages adoption risk and gives me real user feedback before committing to renovation costs.

---

## What I've learned building this

This project has been my entry point to full-stack web development. Things I learned the hard way:

- **HTTP is the protocol, not the internet.** Browser-to-localhost talks HTTP just like browser-to-Amazon does.
- **REST is a convention, not a technology.** Once you see why `POST /sales` reads naturally and `GET /getAllSales` reads awkwardly, you can't unsee it.
- **CORS is a server-side opt-in.** It can't be bypassed in the browser. The fix is always on the backend.
- **Pydantic catches at the door.** Most "the data is weird" bugs go away when the API has a strict contract.
- **localStorage is per-device.** It looks like persistence but doesn't survive a device swap. Real data lives on a real backend.
- **Async bugs hide in pairs.** When you fix one missing `await`, search the codebase for the same pattern elsewhere.
- **Floating-point math isn't exact.** For money, round to 2 decimal places (or store as integer paise/cents in serious systems).
- **Silent failures are the worst kind.** UI success does not equal data saved. Always verify the data reached the database.
- **One commit per logical change.** Bundling refactor + new feature in one commit makes reverts painful.
- **Design before you code.** 30 minutes of sketching the Excel file structure beats 4 hours of refactoring.

---

## Author

**Devayani Senthilvelan**

Master of Data Science, RMIT University, Melbourne. Background in biomedical engineering and data analytics. Building this POS for my family's business while preparing for a career in data analytics.

Currently seeking data analyst roles in Melbourne, with a focus on retail and commercial analytics.

- LinkedIn: [https://www.linkedin.com/in/devayani-senthilvelan-113138198/](https://www.linkedin.com/in/devayani-senthilvelan-113138198/)
- GitHub: [github.com/devayani24](https://github.com/devayani24)
- Email: devayanisenvel@gmail.com
