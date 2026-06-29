"""
Import finance_data.json into Neon PostgreSQL — Each field gets its own table.
Har field ka alag table: normalized schema with 20 separate tables.

Run: python -m scripts.import_finance_data_normalized
"""

import json
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean,
    Text, DateTime, ForeignKey
)
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# ──────────────────────────────────────────────
# Database Setup — Neon PostgreSQL
# ──────────────────────────────────────────────
from backend.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

# ──────────────────────────────────────────────
# Define separate tables for each field
# Har field ka alag table — 20 tables total
# ──────────────────────────────────────────────

class FinanceCustomerId(Base):
    """Central customer identity table — all other tables reference this."""
    __tablename__ = "finance_customer_ids"
    customer_id = Column(Integer, primary_key=True, autoincrement=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class FinanceAccountNumber(Base):
    __tablename__ = "finance_account_numbers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("finance_customer_ids.customer_id"), nullable=False, unique=True)
    account_number = Column(String(50), nullable=True)


class FinanceFullName(Base):
    __tablename__ = "finance_full_names"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("finance_customer_ids.customer_id"), nullable=False, unique=True)
    full_name = Column(String(200), nullable=True)


class FinanceFatherName(Base):
    __tablename__ = "finance_father_names"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("finance_customer_ids.customer_id"), nullable=False, unique=True)
    father_name = Column(String(200), nullable=True)


class FinanceMotherName(Base):
    __tablename__ = "finance_mother_names"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("finance_customer_ids.customer_id"), nullable=False, unique=True)
    mother_name = Column(String(200), nullable=True)


class FinanceDateOfBirth(Base):
    __tablename__ = "finance_dates_of_birth"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("finance_customer_ids.customer_id"), nullable=False, unique=True)
    date_of_birth = Column(String(20), nullable=True)


class FinanceCnicDummy(Base):
    __tablename__ = "finance_cnic_dummies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("finance_customer_ids.customer_id"), nullable=False, unique=True)
    cnic_dummy = Column(String(20), nullable=True)

class FinancePhone(Base):
    __tablename__ = "finance_phones"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("finance_customer_ids.customer_id"), nullable=False, unique=True)
    phone = Column(String(20), nullable=True)


class FinanceEmail(Base):
    __tablename__ = "finance_emails"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("finance_customer_ids.customer_id"), nullable=False, unique=True)
    email = Column(String(200), nullable=True)


class FinanceAddress(Base):
    __tablename__ = "finance_addresses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("finance_customer_ids.customer_id"), nullable=False, unique=True)
    address = Column(Text, nullable=True)


class FinanceCity(Base):
    __tablename__ = "finance_cities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("finance_customer_ids.customer_id"), nullable=False, unique=True)
    city = Column(String(100), nullable=True)


class FinanceProfession(Base):
    __tablename__ = "finance_professions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("finance_customer_ids.customer_id"), nullable=False, unique=True)
    profession = Column(String(200), nullable=True)


class FinanceAccountBalance(Base):
    __tablename__ = "finance_account_balances"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("finance_customer_ids.customer_id"), nullable=False, unique=True)
    account_balance = Column(Float, default=0.0)


class FinanceCreditScore(Base):
    __tablename__ = "finance_credit_scores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("finance_customer_ids.customer_id"), nullable=False, unique=True)
    credit_score = Column(Integer, default=0)


class FinanceExistingLoan(Base):
    __tablename__ = "finance_existing_loans"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("finance_customer_ids.customer_id"), nullable=False, unique=True)
    existing_loan = Column(Boolean, default=False)


class FinanceLoanLimit(Base):
    __tablename__ = "finance_loan_limits"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("finance_customer_ids.customer_id"), nullable=False, unique=True)
    loan_limits = Column(Float, default=0.0)


class FinanceBankRoutingNumber(Base):
    __tablename__ = "finance_bank_routing_numbers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("finance_customer_ids.customer_id"), nullable=False, unique=True)
    bank_routing_number = Column(String(20), nullable=True)

# ──────────────────────────────────────────────
# Utility Functions
# ──────────────────────────────────────────────

ALL_TABLES = [
    FinanceCustomerId,
    FinanceAccountNumber,
    FinanceFullName,
    FinanceFatherName,
    FinanceMotherName,
    FinanceDateOfBirth,
    FinanceCnicDummy,
    FinancePhone,
    FinanceEmail,
    FinanceAddress,
    FinanceCity,
    FinanceProfession,
    FinanceEmploymentType,
    FinanceMonthlyIncome,
    FinanceAccountBalance,
    FinanceCreditScore,
    FinanceExistingLoan,
    FinanceLoanLimit,
    FinanceBankRoutingNumber,
    FinancePassword,
]

def create_tables():
    """Create all 20 tables in the Neon database."""
    print("Creating tables in Neon PostgreSQL...")
    Base.metadata.create_all(bind=engine)
    print(f"✅ {len(ALL_TABLES)} tables created successfully.")

def drop_tables():
    """Drop all 20 tables (for reset)."""
    print("Dropping all finance_* tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ All tables dropped.")

def table_row_counts(db: Session) -> dict:
    """Return row counts for all tables."""
    counts = {}
    for tbl_cls in ALL_TABLES:
        try:
            count = db.query(tbl_cls).count()
            counts[tbl_cls.__tablename__] = count
        except Exception:
            counts[tbl_cls.__tablename__] = "ERROR"
    return counts


def import_data(json_path: Optional[str] = None):
    """Import finance_data.json into the normalized Neon schema."""
    if not json_path:
        json_path = Path(__file__).resolve().parent.parent / "finance_data.json"

    if not os.path.exists(json_path):
        print(f"❌ File not found: {json_path}")
        return

    print(f"📖 Reading data from {json_path}...")
    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)
    print(f"📦 Found {len(records)} records in JSON file.")

    # Create tables
    create_tables()
    db = SessionLocal()

    try:
        # Check if already imported
        existing = db.query(FinanceCustomerId).count()
        if existing > 0:
            print(f"⚠️  Database already has {existing} customer records.")
            print("   Run with '--reset' to re-import, or skipping.")
            counts = table_row_counts(db)
            print("\n📊 Current table row counts:")
            for tbl, cnt in counts.items():
                print(f"   {tbl}: {cnt}")
            return

        imported = 0
        skipped = 0

        for rec in records:
            try:
                cid = rec.get("customer_id")
                if cid is None:
                    skipped += 1
                    continue

                # Insert into central customer_ids table
                customer = FinanceCustomerId(customer_id=int(cid))

                imported += 1

            except Exception as e:
                print(f"  ⚠️  Skipping record (customer_id={rec.get('customer_id')}): {e}")
                skipped += 1

            if imported % 100 == 0 and imported > 0:
                db.commit()
                print(f"  ✅ Imported {imported} records...")

        db.commit()
        print(f"\n{'='*60}")
        print(f"🎉 Import complete!")
        print(f"   ✅ {imported} records imported")
        print(f"   ⚠️  {skipped} records skipped")

        print(f"\n📊 Table row counts in Neon PostgreSQL:")
        counts = table_row_counts(db)
        for tbl, cnt in counts.items():
            print(f"   🗂️  {tbl}: {cnt} rows")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Import failed: {e}")
        raise
    finally:

def show_tables_info():
    """Show all tables and their columns in the Neon database."""
    from sqlalchemy import inspect

    inspector = inspect(engine)
    all_table_names = inspector.get_table_names()
    finance_tables = [t for t in all_table_names if t.startswith("finance_")]

    print(f"\n📋 Finance tables in Neon PostgreSQL ({len(finance_tables)}):")
    print("=" * 60)
    for tbl in sorted(finance_tables):
        columns = inspector.get_columns(tbl)
        col_info = ", ".join([f"{col['name']} ({col['type']})" for col in columns])
        print(f"   🗂️  {tbl}")
        print(f"      Columns: {col_info}")
        print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Import finance_data.json — each field gets its own table in Neon PostgreSQL."
    )
    parser.add_argument("--json", help="Path to finance_data.json (default: ../finance_data.json)")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate all tables before import")
    parser.add_argument("--show", action="store_true", help="Show current tables and columns")
    parser.add_argument("--counts", action="store_true", help="Show row counts only")

    args = parser.parse_args()

    if args.show:
        show_tables_info()
        sys.exit(0)

    if args.counts:
        db = SessionLocal()
        try:
            counts = table_row_counts(db)
            print("📊 Row counts:")
            for tbl, cnt in counts.items():
                print(f"   {tbl}: {cnt}")
        finally:
            db.close()
        sys.exit(0)

    if args.reset:
        print("🔄 Resetting tables...")
        drop_tables()

    import_data(json_path=args.json)

        db.close()

                db.add(customer)

                # Each field → its own table
                field_data = [
                    (FinanceAccountNumber,      "account_number",     str(rec.get("account_number", "")) if rec.get("account_number") else None),
                    (FinanceFullName,           "full_name",          str(rec.get("full_name", "")) if rec.get("full_name") else None),
                    (FinanceFatherName,         "father_name",        str(rec.get("father_name", "")) if rec.get("father_name") else None),
                    (FinanceMotherName,         "mother_name",        str(rec.get("mother_name", "")) if rec.get("mother_name") else None),
                    (FinanceDateOfBirth,        "date_of_birth",      str(rec.get("date_of_birth", "")) if rec.get("date_of_birth") else None),
                    (FinanceCnicDummy,          "cnic_dummy",         str(rec.get("cnic_dummy", "")) if rec.get("cnic_dummy") else None),
                    (FinancePhone,              "phone",              str(rec.get("phone", "")) if rec.get("phone") else None),
                    (FinanceEmail,              "email",              str(rec.get("email", "")) if rec.get("email") else None),
                    (FinanceAddress,            "address",            str(rec.get("address", "")) if rec.get("address") else None),
                    (FinanceCity,               "city",               str(rec.get("city", "")) if rec.get("city") else None),
                    (FinanceProfession,         "profession",         str(rec.get("profession", "")) if rec.get("profession") else None),
                    (FinanceEmploymentType,     "employment_type",    str(rec.get("employment_type", "")) if rec.get("employment_type") else None),
                    (FinanceMonthlyIncome,      "monthly_income",     float(rec.get("monthly_income", 0) or 0)),
                    (FinanceAccountBalance,     "account_balance",    float(rec.get("account_balance", 0) or 0)),
                    (FinanceCreditScore,        "credit_score",       int(rec.get("credit_score", 0) or 0)),
                    (FinanceExistingLoan,       "existing_loan",      bool(rec.get("existing_loan", False))),
                    (FinanceLoanLimit,          "loan_limits",        float(rec.get("loan_limits", 0) or 0)),
                    (FinanceBankRoutingNumber,  "bank_routing_number", str(rec.get("bank_routing_number", "")) if rec.get("bank_routing_number") else None),
                    (FinancePassword,           "password",           str(rec.get("password", "")) if rec.get("password") else None),
                ]

                for cls, field_name, value in field_data:
                    row = cls(customer_id=int(cid))
                    setattr(row, field_name, value)
                    db.add(row)



class FinancePassword(Base):
    __tablename__ = "finance_passwords"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("finance_customer_ids.customer_id"), nullable=False, unique=True)
    password = Column(String(200), nullable=True)


class FinanceEmploymentType(Base):
    __tablename__ = "finance_employment_types"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("finance_customer_ids.customer_id"), nullable=False, unique=True)
    employment_type = Column(String(50), nullable=True)


class FinanceMonthlyIncome(Base):
    __tablename__ = "finance_monthly_incomes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("finance_customer_ids.customer_id"), nullable=False, unique=True)
    monthly_income = Column(Float, default=0.0)


    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
