-- 1. Central customer identity table
CREATE TABLE IF NOT EXISTS finance_customer_ids (
  customer_id INTEGER PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Account Number
CREATE TABLE IF NOT EXISTS finance_account_numbers (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL UNIQUE REFERENCES finance_customer_ids(customer_id),
  account_number VARCHAR(50)
);

-- 3. Full Name
CREATE TABLE IF NOT EXISTS finance_full_names (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL UNIQUE REFERENCES finance_customer_ids(customer_id),
  full_name VARCHAR(200)
);

-- 4. Father Name
CREATE TABLE IF NOT EXISTS finance_father_names (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL UNIQUE REFERENCES finance_customer_ids(customer_id),
  father_name VARCHAR(200)
);

-- 5. Mother Name
CREATE TABLE IF NOT EXISTS finance_mother_names (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL UNIQUE REFERENCES finance_customer_ids(customer_id),
  mother_name VARCHAR(200)
);

-- 6. Date of Birth
CREATE TABLE IF NOT EXISTS finance_dates_of_birth (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL UNIQUE REFERENCES finance_customer_ids(customer_id),
  date_of_birth VARCHAR(20)
);

-- 7. CNIC Dummy
CREATE TABLE IF NOT EXISTS finance_cnic_dummies (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL UNIQUE REFERENCES finance_customer_ids(customer_id),
  cnic_dummy VARCHAR(20)
);

-- 8. Phone
CREATE TABLE IF NOT EXISTS finance_phones (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL UNIQUE REFERENCES finance_customer_ids(customer_id),
  phone VARCHAR(20)
);

-- 9. Email
CREATE TABLE IF NOT EXISTS finance_emails (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL UNIQUE REFERENCES finance_customer_ids(customer_id),
  email VARCHAR(200)
);

-- 10. Address
CREATE TABLE IF NOT EXISTS finance_addresses (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL UNIQUE REFERENCES finance_customer_ids(customer_id),
  address TEXT
);

-- 11. City
CREATE TABLE IF NOT EXISTS finance_cities (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL UNIQUE REFERENCES finance_customer_ids(customer_id),
  city VARCHAR(100)
);

-- 12. Profession
CREATE TABLE IF NOT EXISTS finance_professions (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL UNIQUE REFERENCES finance_customer_ids(customer_id),
  profession VARCHAR(200)
);

-- 13. Employment Type
CREATE TABLE IF NOT EXISTS finance_employment_types (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL UNIQUE REFERENCES finance_customer_ids(customer_id),
  employment_type VARCHAR(50)
);

-- 14. Monthly Income
CREATE TABLE IF NOT EXISTS finance_monthly_incomes (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL UNIQUE REFERENCES finance_customer_ids(customer_id),
  monthly_income FLOAT DEFAULT 0
);

-- 15. Account Balance
CREATE TABLE IF NOT EXISTS finance_account_balances (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL UNIQUE REFERENCES finance_customer_ids(customer_id),
  account_balance FLOAT DEFAULT 0
);

-- 16. Credit Score
CREATE TABLE IF NOT EXISTS finance_credit_scores (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL UNIQUE REFERENCES finance_customer_ids(customer_id),
  credit_score INTEGER DEFAULT 0
);

-- 17. Existing Loan
CREATE TABLE IF NOT EXISTS finance_existing_loans (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL UNIQUE REFERENCES finance_customer_ids(customer_id),
  existing_loan BOOLEAN DEFAULT FALSE
);

-- 18. Loan Limits
CREATE TABLE IF NOT EXISTS finance_loan_limits (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL UNIQUE REFERENCES finance_customer_ids(customer_id),
  loan_limits FLOAT DEFAULT 0
);

-- 19. Bank Routing Number
CREATE TABLE IF NOT EXISTS finance_bank_routing_numbers (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL UNIQUE REFERENCES finance_customer_ids(customer_id),
  bank_routing_number VARCHAR(20)
);

-- 20. Password
CREATE TABLE IF NOT EXISTS finance_passwords (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL UNIQUE REFERENCES finance_customer_ids(customer_id),
  password VARCHAR(200)
);
