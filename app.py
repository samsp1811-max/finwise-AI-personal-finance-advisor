import os, statistics
from collections import defaultdict
from datetime import date
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from sqlalchemy import func
load_dotenv()
from models import db, Income, Expense, Goal, Budget, CATS
import ai_service as ai

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///finwise.db")
db.init_app(app)
with app.app_context(): db.create_all()

def amount(v):
    x = float(v)
    if not 0 < x <= 1e9: raise ValueError("Amount must be greater than 0.")
    return x
def clean(s, n): return str(s or "").replace("<", "").replace(">", "").strip()[:n]
def when(s): return date.fromisoformat(s) if s else date.today()
def mstart(d, k=0):
    y, m = divmod(d.year * 12 + d.month - 1 - k, 12); return date(y, m + 1, 1)
def bounds(m):
    s = date.fromisoformat((m or date.today().strftime("%Y-%m")) + "-01"); return s, mstart(s, -1)

@app.errorhandler(ValueError)
@app.errorhandler(TypeError)
def bad(e): return jsonify(error=str(e) or "Invalid input."), 400

@app.get("/")
def home(): return render_template("index.html", demo=not ai.configured())

def add(model, **kw):
    o = model(**kw); db.session.add(o); db.session.commit(); return jsonify(o.to_dict()), 201

@app.post("/api/incomes")
def add_income(): j = request.json or {}; return add(Income, source=clean(j.get("source"), 60) or "Income", amount=amount(j.get("amount")), date=when(j.get("date")))

@app.post("/api/expenses")
def add_expense():
    j = request.json or {}
    if j.get("category") not in CATS: raise ValueError("Choose a valid category.")
    return add(Expense, category=j["category"], amount=amount(j.get("amount")), date=when(j.get("date")), note=clean(j.get("note"), 120))

@app.get("/api/expenses")
def list_expenses():
    s, e = bounds(request.args.get("month"))
    rows = Expense.query.filter(Expense.date >= s, Expense.date < e).order_by(Expense.date.desc()).all()
    return jsonify([r.to_dict() for r in rows])

@app.delete("/api/expenses/<int:i>")
def del_expense(i): db.session.delete(db.get_or_404(Expense, i)); db.session.commit(); return "", 204

@app.route("/api/goals", methods=["GET", "POST"])
def goals():
    if request.method == "POST":
        j = request.json or {}
        return add(Goal, name=clean(j.get("name"), 80) or "Goal", target=amount(j.get("target")), saved=0,
                   deadline=when(j["deadline"]) if j.get("deadline") else None)
    return jsonify([g.to_dict() for g in Goal.query.all()])

@app.patch("/api/goals/<int:i>")
def fund_goal(i):
    g = db.get_or_404(Goal, i); g.saved += amount((request.json or {}).get("add")); db.session.commit(); return jsonify(g.to_dict())

def report(month):
    s, e = bounds(month)
    inc = db.session.query(func.coalesce(func.sum(Income.amount), 0)).filter(Income.date >= s, Income.date < e).scalar()
    cats = dict(db.session.query(Expense.category, func.sum(Expense.amount)).filter(Expense.date >= s, Expense.date < e).group_by(Expense.category).all())
    exp = sum(cats.values()); lim = {b.category: b.limit for b in Budget.query.all()}
    over = [{"category": c, "spent": v, "limit": lim[c]} for c, v in cats.items() if c in lim and v > lim[c]]
    return {"month": s.strftime("%Y-%m"), "income": inc, "expenses": exp, "net": inc - exp,
            "savings_rate": (inc - exp) / inc * 100 if inc else 0, "by_category": cats, "limits": lim, "overspent": over,
            "goals": [g.to_dict() for g in Goal.query.all()]}

@app.get("/api/report")
def get_report(): return jsonify(report(request.args.get("month")))

@app.post("/api/report/summary")
def summary(): return jsonify(summary=ai.summarize(report((request.json or {}).get("month"))))

@app.post("/api/budget/generate")
def gen_budget():
    today = date.today(); start = mstart(today, 2)
    inc = defaultdict(float); by_cat = defaultdict(float)
    for r in Income.query.filter(Income.date >= start): inc[r.date.strftime("%Y-%m")] += r.amount
    for r in Expense.query.filter(Expense.date >= start): by_cat[r.category] += r.amount
    if not inc: raise ValueError("Log some income first so a budget can be planned.")
    n = len(inc); vals = list(inc.values()); avg = sum(vals) / n
    vol = statistics.pstdev(vals) / avg if n > 1 and avg else 0
    plan = ai.generate_budget({"avg_income": round(avg), "income_volatility": round(vol, 2),
        "avg_by_category": {c: round(v / n) for c, v in by_cat.items()}, "goals": [g.to_dict() for g in Goal.query.all()]})
    Budget.query.delete()
    for c, v in plan["limits"].items(): db.session.add(Budget(category=c, limit=v))
    db.session.commit(); return jsonify(plan)

@app.post("/api/chat")
def chat():
    j = request.json or {}; q = clean(j.get("question"), 500)
    if not q: raise ValueError("Type a question first.")
    return jsonify(answer=ai.chat(q, report(j.get("month"))))

@app.post("/api/demo/seed")
def seed():
    db.drop_all(); db.create_all(); t = date.today()
    exp = {"Housing": 15000, "Food": 7000, "Transport": 4000, "Utilities": 3000, "Entertainment": 3000, "Shopping": 4000, "Healthcare": 2000, "Other": 2000}
    for k, extra in enumerate([12000, 3000, 8000]):
        m = mstart(t, k)
        db.session.add(Income(source="Salary", amount=50000, date=m))
        db.session.add(Income(source="Freelance client", amount=extra, date=m.replace(day=5)))
        for c, v in exp.items(): db.session.add(Expense(category=c, amount=v * (1.1 if c == "Food" and k == 0 else 1), date=m.replace(day=3), note="Monthly"))
    db.session.add(Goal(name="Emergency fund", target=150000, saved=40000)); db.session.commit()
    return jsonify(ok=True)

@app.post("/api/reset")
def reset(): db.drop_all(); db.create_all(); return jsonify(ok=True)

if __name__ == "__main__": app.run(port=5000, debug=True)
