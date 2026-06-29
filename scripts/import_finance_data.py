"""
Import finance_data.json into Neon PostgreSQL via the main backend database.
Run: python -m scripts.import_finance_data
"""
import json
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.database import SessionLocal, init_db
from backend.models import FinanceCustomer


def import_data(json_path: str = None):
    if not json_path:
        json_path = Path(__file__).resolve().parent.parent / "finance_data.json"

    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return

    print(f"Reading data from {json_path}...")
    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    print(f"Found {len(records)} records.")

    init_db()
    db = SessionLocal()

    try:
        existing = db.query(FinanceCustomer).count()
        if existing > 0:
            print(f"Database already has {existing} records. Skipping import.")
            return

        imported = 0
        skipped = 0

        for rec in records:
            try:
                customer = FinanceCustomer(
                    customer_id=rec.get("customer_id"),
                    full_name=str(rec.get("full_name", "")),
                    father_name=str(rec.get("father_name", "")),
                    mother_name=str(rec.get("mother_name", "")),
                    date_of_birth=str(rec.get("date_of_birth", "")),
                    cnic_dummy=str(rec.get("cnic_dummy", "")),
                    phone=str(rec.get("phone", "")),
                    email=str(rec.get("email", "")),
                    address=str(rec.get("address", "")),
                    city=str(rec.get("city", "")),
                    profession=str(rec.get("profession", "")),
                    employment_type=str(rec.get("employment_type", "")),
                    monthly_income=float(rec.get("monthly_income", 0) or 0),
                    account_number=str(rec.get("account_number", "")),
                    account_balance=float(rec.get("account_balance", 0) or 0),
                    credit_score=int(rec.get("credit_score", 0) or 0),
                    existing_loan=bool(rec.get("existing_loan", False)),
                    loan_limits=float(rec.get("loan_limits", 0) or 0),
                    bank_routing_number=str(rec.get("bank_routing_number", "")),
                    password=str(rec.get("password", "")),
                )
                db.add(customer)
                imported += 1
            except Exception as e:
                print(f"Skipping record {rec.get('customer_id')}: {e}")
                skipped += 1

            if imported % 200 == 0 and imported > 0:
                db.commit()
                print(f"Imported {imported} records...")

        db.commit()
        print(f"\nImport complete: {imported} imported, {skipped} skipped.")
    except Exception as e:
        db.rollback()
        print(f"Import failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import_data()
