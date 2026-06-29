"""Demo seed data for the SmartFinance Dummy Banking API.

Sample Scenarios:
1. C001 - Ahmed Khan: Premium customer, normal transactions, suspicious foreign txn
2. C002 - Fatima Ali: Standard customer, failed payment needing refund
3. C003 - Usman Malik: Student, low balance before bill payment
4. C004 - Sana Tariq: Salaried professional, needs financial coaching
5. C005 - Bilal Hassan: Business account, high-volume transactions
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from banking_api.models import (
    Customer, Account, Transaction, Card, KYCStatus, RiskLevel,
    AccountStatus, TransactionStatus, TransactionType, CardStatus, CardType,
)

logger = logging.getLogger("banking_api.seed_data")


def seed_database(db: Session):
    if db.query(Customer).count() > 0:
        logger.info("Database already has data, skipping seed")
        return

    now = datetime.now(timezone.utc)

    # =========================================================================
    # CUSTOMERS
    # =========================================================================
    customers = [
        Customer(
            customer_id="C001", name="Ahmed Khan", email="ahmed.khan@email.com",
            phone="+923001234567", account_type="Premium", monthly_income=150000,
            monthly_expense=85000, kyc_status=KYCStatus.VERIFIED, risk_level=RiskLevel.LOW,
            saving_score=65,
        ),
        Customer(
            customer_id="C002", name="Fatima Ali", email="fatima.ali@email.com",
            phone="+923007654321", account_type="Standard", monthly_income=60000,
            monthly_expense=55000, kyc_status=KYCStatus.VERIFIED, risk_level=RiskLevel.LOW,
            saving_score=30,
        ),
        Customer(
            customer_id="C003", name="Usman Malik", email="usman.malik@email.com",
            phone="+923009876543", account_type="Student", monthly_income=30000,
            monthly_expense=28000, kyc_status=KYCStatus.VERIFIED, risk_level=RiskLevel.LOW,
            saving_score=20,
        ),
        Customer(
            customer_id="C004", name="Sana Tariq", email="sana.tariq@email.com",
            phone="+923005555555", account_type="Salaried", monthly_income=95000,
            monthly_expense=82000, kyc_status=KYCStatus.VERIFIED, risk_level=RiskLevel.MEDIUM,
            saving_score=45,
        ),
        Customer(
            customer_id="C005", name="Bilal Hassan", email="bilal.hassan@email.com",
            phone="+923001112233", account_type="Business", monthly_income=500000,
            monthly_expense=350000, kyc_status=KYCStatus.VERIFIED, risk_level=RiskLevel.LOW,
            saving_score=80,
        ),
    ]
    db.add_all(customers)

    # =========================================================================
    # ACCOUNTS
    # =========================================================================
    accounts = [
        Account(account_id="ACC001", customer_id="C001", balance=45000.0, currency="PKR", account_type="Current"),
        Account(account_id="ACC002", customer_id="C001", balance=200000.0, currency="PKR", account_type="Savings"),
        Account(account_id="ACC003", customer_id="C002", balance=8500.0, currency="PKR", account_type="Current"),
        Account(account_id="ACC004", customer_id="C003", balance=2500.0, currency="PKR", account_type="Current"),
        Account(account_id="ACC005", customer_id="C004", balance=32000.0, currency="PKR", account_type="Current"),
        Account(account_id="ACC006", customer_id="C004", balance=15000.0, currency="PKR", account_type="Savings"),
        Account(account_id="ACC007", customer_id="C005", balance=450000.0, currency="PKR", account_type="Current"),
        Account(account_id="ACC008", customer_id="C005", balance=1200000.0, currency="PKR", account_type="Business"),
    ]
    db.add_all(accounts)

    # =========================================================================
    # TRANSACTIONS
    # =========================================================================
    transactions = [
        # --- C001: Ahmed Khan - Normal transactions ---
        Transaction(transaction_id="TX001", customer_id="C001", account_id="ACC001",
            amount=3500, merchant="Carrefour Hypermarket", location="Karachi", category="Groceries",
            transaction_type=TransactionType.DEBIT, status=TransactionStatus.COMPLETED,
            created_at=now - timedelta(hours=2)),
        Transaction(transaction_id="TX002", customer_id="C001", account_id="ACC001",
            amount=1200, merchant="Shell Petrol Station", location="Karachi", category="Transport",
            transaction_type=TransactionType.DEBIT, status=TransactionStatus.COMPLETED,
            created_at=now - timedelta(hours=5)),
        Transaction(transaction_id="TX003", customer_id="C001", account_id="ACC001",
            amount=8000, merchant="K-Electric", location="Karachi", category="Utilities",
            transaction_type=TransactionType.DEBIT, status=TransactionStatus.COMPLETED,
            created_at=now - timedelta(days=1)),
        Transaction(transaction_id="TX004", customer_id="C001", account_id="ACC001",
            amount=15000, merchant="SSGC", location="Karachi", category="Utilities",
            transaction_type=TransactionType.DEBIT, status=TransactionStatus.COMPLETED,
            created_at=now - timedelta(days=2)),
        Transaction(transaction_id="TX005", customer_id="C001", account_id="ACC001",
            amount=2500, merchant="Daraz.pk", location="Online", category="Shopping",
            transaction_type=TransactionType.DEBIT, status=TransactionStatus.COMPLETED,
            created_at=now - timedelta(days=3)),
        # --- C001: Suspicious foreign transaction ---
        Transaction(transaction_id="TX006", customer_id="C001", account_id="ACC001",
            amount=90000, merchant="Luxury Retail Dubai", location="Dubai", category="Shopping",
            transaction_type=TransactionType.DEBIT, status=TransactionStatus.PENDING,
            is_international=True, is_online=False,
            created_at=now - timedelta(minutes=30)),
        # --- C001: Another suspicious - rapid small txn ---
        Transaction(transaction_id="TX007", customer_id="C001", account_id="ACC001",
            amount=45000, merchant="Electronics Store", location="Karachi", category="Shopping",
            transaction_type=TransactionType.DEBIT, status=TransactionStatus.PENDING,
            created_at=now - timedelta(minutes=15)),

        # --- C002: Fatima Ali - Failed payment needing refund ---
        Transaction(transaction_id="TX008", customer_id="C002", account_id="ACC003",
            amount=12000, merchant="JazzCash Mobile Load", location="Online", category="Mobile",
            transaction_type=TransactionType.DEBIT, status=TransactionStatus.FAILED,
            failure_reason="Insufficient balance after processing",
            is_online=True, created_at=now - timedelta(days=1)),
        Transaction(transaction_id="TX009", customer_id="C002", account_id="ACC003",
            amount=3000, merchant="Foodpanda", location="Lahore", category="Food",
            transaction_type=TransactionType.DEBIT, status=TransactionStatus.COMPLETED,
            created_at=now - timedelta(days=2)),
        Transaction(transaction_id="TX010", customer_id="C002", account_id="ACC003",
            amount=500, merchant="Google Play", location="Online", category="Subscriptions",
            transaction_type=TransactionType.DEBIT, status=TransactionStatus.COMPLETED,
            is_online=True, created_at=now - timedelta(days=5)),

        # --- C003: Usman Malik - Low balance before bill payment ---
        Transaction(transaction_id="TX011", customer_id="C003", account_id="ACC004",
            amount=1500, merchant="Jazz Internet Package", location="Online", category="Mobile",
            transaction_type=TransactionType.DEBIT, status=TransactionStatus.COMPLETED,
            is_online=True, created_at=now - timedelta(days=1)),
        Transaction(transaction_id="TX012", customer_id="C003", account_id="ACC004",
            amount=800, merchant="University Canteen", location="Lahore", category="Food",
            transaction_type=TransactionType.DEBIT, status=TransactionStatus.COMPLETED,
            created_at=now - timedelta(days=1)),
        Transaction(transaction_id="TX013", customer_id="C003", account_id="ACC004",
            amount=3500, merchant="K-Electric", location="Lahore", category="Utilities",
            transaction_type=TransactionType.DEBIT, status=TransactionStatus.PENDING,
            created_at=now - timedelta(hours=1)),

        # --- C004: Sana Tariq - Needs financial coaching ---
        Transaction(transaction_id="TX014", customer_id="C004", account_id="ACC005",
            amount=15000, merchant="Al-Fatah Mall", location="Islamabad", category="Shopping",
            transaction_type=TransactionType.DEBIT, status=TransactionStatus.COMPLETED,
            created_at=now - timedelta(hours=6)),
        Transaction(transaction_id="TX015", customer_id="C004", account_id="ACC005",
            amount=8500, merchant="Pizza Hut", location="Islamabad", category="Food",
            transaction_type=TransactionType.DEBIT, status=TransactionStatus.COMPLETED,
            created_at=now - timedelta(days=1)),
        Transaction(transaction_id="TX016", customer_id="C004", account_id="ACC005",
            amount=22000, merchant="Fashion Store", location="Islamabad", category="Shopping",
            transaction_type=TransactionType.DEBIT, status=TransactionStatus.COMPLETED,
            created_at=now - timedelta(days=2)),
        Transaction(transaction_id="TX017", customer_id="C004", account_id="ACC005",
            amount=6000, merchant="Netflix", location="Online", category="Subscriptions",
            transaction_type=TransactionType.DEBIT, status=TransactionStatus.COMPLETED,
            is_online=True, created_at=now - timedelta(days=3)),
        Transaction(transaction_id="TX018", customer_id="C004", account_id="ACC005",
            amount=3500, merchant="Spotify + YouTube Premium", location="Online", category="Subscriptions",
            transaction_type=TransactionType.DEBIT, status=TransactionStatus.COMPLETED,
            is_online=True, created_at=now - timedelta(days=3)),

        # --- C005: Bilal Hassan - Business account ---
        Transaction(transaction_id="TX019", customer_id="C005", account_id="ACC007",
            amount=75000, merchant="Supplier - Traders Corp", location="Karachi", category="Business",
            transaction_type=TransactionType.DEBIT, status=TransactionStatus.COMPLETED,
            created_at=now - timedelta(days=1)),
        Transaction(transaction_id="TX020", customer_id="C005", account_id="ACC007",
            amount=120000, merchant="Supplier - Al-Rajhi Trading", location="Karachi", category="Business",
            transaction_type=TransactionType.DEBIT, status=TransactionStatus.COMPLETED,
            created_at=now - timedelta(days=3)),
        Transaction(transaction_id="TX021", customer_id="C005", account_id="ACC008",
            amount=500000, merchant="Client Payment - Tech Solutions", location="Karachi", category="Income",
            transaction_type=TransactionType.CREDIT, status=TransactionStatus.COMPLETED,
            created_at=now - timedelta(days=2)),
    ]
    db.add_all(transactions)

    # =========================================================================
    # CARDS
    # =========================================================================
    cards = [
        Card(card_id="CRD001", customer_id="C001", card_number="4532015112890365",
            card_type=CardType.DEBIT, status=CardStatus.ACTIVE, expiry_date="12/28"),
        Card(card_id="CRD002", customer_id="C001", card_number="4916123456789012",
            card_type=CardType.CREDIT, status=CardStatus.ACTIVE, expiry_date="08/27"),
        Card(card_id="CRD003", customer_id="C002", card_number="4539785123456789",
            card_type=CardType.DEBIT, status=CardStatus.ACTIVE, expiry_date="03/29"),
        Card(card_id="CRD004", customer_id="C003", card_number="4532015678901234",
            card_type=CardType.DEBIT, status=CardStatus.ACTIVE, expiry_date="06/28"),
        Card(card_id="CRD005", customer_id="C004", card_number="4916345678901234",
            card_type=CardType.DEBIT, status=CardStatus.ACTIVE, expiry_date="10/27"),
        Card(card_id="CRD006", customer_id="C004", card_number="4532017890123456",
            card_type=CardType.CREDIT, status=CardStatus.ACTIVE, expiry_date="01/29"),
        Card(card_id="CRD007", customer_id="C005", card_number="4532019012345678",
            card_type=CardType.DEBIT, status=CardStatus.ACTIVE, expiry_date="05/28"),
    ]
    db.add_all(cards)

    db.commit()
    logger.info(f"Seeded {len(customers)} customers, {len(accounts)} accounts, {len(transactions)} transactions, {len(cards)} cards")
