from datetime import date
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
CATS = ["Housing", "Food", "Transport", "Utilities", "Education", "Healthcare", "Entertainment", "Shopping", "Other"]
NEEDS = {"Housing", "Food", "Transport", "Utilities", "Education", "Healthcare"}

class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    def to_dict(self):
        out = {}
        for c in self.__table__.columns:
            v = getattr(self, c.name)
            out[c.name] = v.isoformat() if isinstance(v, date) else v
        return out

class Income(Base):
    source = db.Column(db.String(60), nullable=False)      # salary, client name, allowance...
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)

class Expense(Base):
    category = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    note = db.Column(db.String(120), default="")

class Goal(Base):
    name = db.Column(db.String(80), nullable=False)
    target = db.Column(db.Float, nullable=False)
    saved = db.Column(db.Float, nullable=False, default=0)
    deadline = db.Column(db.Date)

class Budget(Base):
    category = db.Column(db.String(30), unique=True, nullable=False)
    limit = db.Column(db.Float, nullable=False)
