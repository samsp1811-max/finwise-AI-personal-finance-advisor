# FinWise AI – Personal Finance Advisor

A polished full-stack AI personal finance dashboard built with React + TypeScript + Tailwind CSS + Recharts and a Python Flask backend with Gemini integration.

## Features

- Landing page with Demo Mode
- Financial input form
- Professional fintech dashboard
- Budget planning with Needs / Wants / Savings
- Expense donut chart
- Income vs expenses chart
- Savings goal progress
- What-If simulator
- AI Saving Suggestions
- AI Monthly Summary
- Ask FinWise AI chat
- Gemini API integration through Flask only
- Realistic fallback AI responses when `GEMINI_API_KEY` is not configured
- Responsive mobile navigation
- No permanent storage of financial data

## Project Structure

```text
finwise-ai/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── charts/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── postcss.config.js
├── backend/
│   ├── app.py
│   ├── gemini_service.py
│   ├── requirements.txt
│   └── .env.example
└── README.md
```

## Requirements

- Node.js 18+
- Python 3.10+
- Optional: Google Gemini API key

## 1. Configure backend

```bash
cd backend
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install packages:

```bash
pip install -r requirements.txt
```

Create `.env` from `.env.example`:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
FRONTEND_ORIGIN=http://localhost:5173
```

The API key is used only by Flask and is never sent to the React application.

## 2. Start Flask

From `backend/`:

```bash
python app.py
```

Flask runs at:

`http://localhost:5000`

## 3. Start frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the URL Vite prints, normally:

`http://localhost:5173`

## 4. Demo Mode

Click **Try Demo** on the landing page.

The application automatically loads:

- Income: ₹50,000
- Other income: ₹5,000
- Housing: ₹15,000
- Food: ₹7,000
- Transportation: ₹4,000
- Utilities: ₹3,000
- Entertainment: ₹3,000
- Shopping: ₹4,000
- Healthcare: ₹2,000
- Other: ₹2,000
- Current savings: ₹40,000
- Goal: Emergency fund
- Target: ₹1,50,000

If `GEMINI_API_KEY` is missing, the backend automatically returns realistic demo AI insights. This keeps the project fully demonstrable.

## API

### POST `/api/financial-advice`

Request:

```json
{
  "income": 50000,
  "otherIncome": 5000,
  "expenses": {
    "housing": 15000,
    "food": 7000
  },
  "financialGoal": "Build an emergency fund",
  "targetAmount": 150000,
  "targetDate": "2027-06-30",
  "currentSavings": 40000,
  "riskPreference": "Balanced",
  "notes": ""
}
```

### POST `/api/ask`

Accepts a question plus the same financial context and returns an AI answer.

### GET `/api/health`

Backend health check.

## GitHub

Do not commit `.env`. The `.gitignore` file excludes it.

```bash
git init
git add .
git commit -m "Initial FinWise AI MVP"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

## Disclaimer

> FinWise AI provides estimates and educational financial insights. It does not provide professional financial, investment, tax, or legal advice, and its recommendations do not guarantee financial outcomes.


## Demo presentation flow

**Landing → Try Demo → Dashboard → Budget Plan → Saving Suggestions → Monthly Summary → What If? → Ask FinWise AI**

For a live demo, you do not need a Gemini key. The Flask backend detects a missing `GEMINI_API_KEY` and uses deterministic demo responses. Add a real key later to activate Gemini-generated responses.

### Currency

The form supports INR (default), USD, EUR and GBP. Currency is kept as user-entered context and the dashboard formats the displayed amounts accordingly.

### Security note

Never commit `.env` or paste API keys into React files. The included `.gitignore` excludes `backend/.env`.
