#!/usr/bin/env node
/**
 * import_neon_normalized.cjs
 * 
 * Import finance_data.json into Neon PostgreSQL — Har field ka alag table!
 * 
 * Creates 20 separate tables, one for each field in finance_data.json,
 * all linked by customer_id.
 * 
 * Usage:
 *   node scripts/import_neon_normalized.cjs
 *   node scripts/import_neon_normalized.cjs --reset
 *   node scripts/import_neon_normalized.cjs --show
 *   node scripts/import_neon_normalized.cjs --counts
 */

const { Pool } = require('pg');
const path = require('path');
const fs = require('fs');

// Load .env manually
const envPath = path.join(__dirname, '..', '.env');
if (fs.existsSync(envPath)) {
  const lines = fs.readFileSync(envPath, 'utf8').split('\n');
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#') || !trimmed.includes('=')) continue;
    const eqIdx = trimmed.indexOf('=');
    const key = trimmed.slice(0, eqIdx).trim();
    const val = trimmed.slice(eqIdx + 1).trim().replace(/^["']|["']$/g, '');
    if (!process.env[key]) process.env[key] = val;
  }
}

const DATABASE_URL = process.env.DATABASE_URL;
if (!DATABASE_URL) {
  console.error('❌ DATABASE_URL not found in .env file');
  process.exit(1);
}

console.log(`🔌 Connecting to Neon PostgreSQL...`);
const pool = new Pool({
  connectionString: DATABASE_URL,
  ssl: { rejectUnauthorized: false },
});


// ──────────────────────────────────────────────
// Table Definitions — 20 tables, one per field
// ──────────────────────────────────────────────

const CREATE_SQL = `

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
`;


const DROP_SQL = `
DROP TABLE IF EXISTS finance_passwords CASCADE;
DROP TABLE IF EXISTS finance_bank_routing_numbers CASCADE;
DROP TABLE IF EXISTS finance_loan_limits CASCADE;
DROP TABLE IF EXISTS finance_existing_loans CASCADE;
DROP TABLE IF EXISTS finance_credit_scores CASCADE;
DROP TABLE IF EXISTS finance_account_balances CASCADE;
DROP TABLE IF EXISTS finance_monthly_incomes CASCADE;
DROP TABLE IF EXISTS finance_employment_types CASCADE;
DROP TABLE IF EXISTS finance_professions CASCADE;
DROP TABLE IF EXISTS finance_cities CASCADE;
DROP TABLE IF EXISTS finance_addresses CASCADE;
DROP TABLE IF EXISTS finance_emails CASCADE;
DROP TABLE IF EXISTS finance_phones CASCADE;
DROP TABLE IF EXISTS finance_cnic_dummies CASCADE;
DROP TABLE IF EXISTS finance_dates_of_birth CASCADE;
DROP TABLE IF EXISTS finance_mother_names CASCADE;
DROP TABLE IF EXISTS finance_father_names CASCADE;
DROP TABLE IF EXISTS finance_full_names CASCADE;
DROP TABLE IF EXISTS finance_account_numbers CASCADE;
DROP TABLE IF EXISTS finance_customer_ids CASCADE;
`;

const ALL_TABLES = [
  'finance_customer_ids', 'finance_account_numbers', 'finance_full_names',
  'finance_father_names', 'finance_mother_names', 'finance_dates_of_birth',
  'finance_cnic_dummies', 'finance_phones', 'finance_emails', 'finance_addresses',
  'finance_cities', 'finance_professions', 'finance_employment_types',
  'finance_monthly_incomes', 'finance_account_balances', 'finance_credit_scores',
  'finance_existing_loans', 'finance_loan_limits', 'finance_bank_routing_numbers',
  'finance_passwords',
];


// ──────────────────────────────────────────────
// Helper Functions
// ──────────────────────────────────────────────

async function query(sql, params = []) {
  const result = await pool.query(sql, params);
  return result.rows;
}

async function showTables() {
  const tables = await query(`
    SELECT table_name
    FROM information_schema.tables t
    WHERE table_schema = 'public' AND table_name LIKE 'finance_%'
    ORDER BY table_name
  `);
  
  console.log(`\n📋 Finance tables in Neon PostgreSQL (${tables.length}):`);
  console.log('='.repeat(60));
  
  for (const t of tables) {
    const cols = await query(`
      SELECT column_name, data_type, character_maximum_length
      FROM information_schema.columns
      WHERE table_schema = 'public' AND table_name = $1
      ORDER BY ordinal_position
    `, [t.table_name]);
    
    const colInfo = cols.map(c => {
      let s = `${c.column_name} (${c.data_type}`;
      if (c.character_maximum_length) s += `(${c.character_maximum_length})`;
      s += ')';
      return s;
    }).join(', ');
    
    const count = await query(`SELECT COUNT(*)::int as c FROM ${t.table_name}`);
    console.log(`   🗂️  ${t.table_name}  [${count[0].c} rows]`);
    console.log(`      Columns: ${colInfo}`);
    console.log();
  }
}

async function showCounts() {
  console.log('📊 Row counts:');
  for (const tbl of ALL_TABLES) {
    try {
      const result = await query(`SELECT COUNT(*)::int as c FROM ${tbl}`);
      console.log(`   🗂️  ${tbl}: ${result[0].c} rows`);
    } catch (e) {
      console.log(`   ❌ ${tbl}: ERROR (${e.message})`);
    }
  }
}

async function createAllTables() {
  console.log('🏗️  Creating 20 tables in Neon PostgreSQL...');
  await pool.query(CREATE_SQL);
  console.log('✅ All 20 tables created successfully!');
}

async function dropAllTables() {
  console.log('🗑️  Dropping all finance_* tables...');
  try {
    await pool.query(DROP_SQL);
    console.log('✅ All tables dropped.');
  } catch (e) {
    console.log('⚠️  Drop warning:', e.message);
  }
}

function strVal(val) {
  if (val === null || val === undefined) return null;
  return String(val);
}


// ──────────────────────────────────────────────
// Main Import Logic
// ──────────────────────────────────────────────

async function importData(jsonPath) {
  if (!jsonPath) {
    jsonPath = path.join(__dirname, '..', 'finance_data.json');
  }
  
  if (!fs.existsSync(jsonPath)) {
    console.error(`❌ File not found: ${jsonPath}`);
    return;
  }
  
  console.log(`📖 Reading data from ${jsonPath}...`);
  const raw = fs.readFileSync(jsonPath, 'utf8');
  const records = JSON.parse(raw);
  console.log(`📦 Found ${records.length} records in JSON file.`);
  
  await createAllTables();
  
  const existing = await query('SELECT COUNT(*)::int as c FROM finance_customer_ids');
  if (existing[0].c > 0) {
    console.log(`⚠️  Database already has ${existing[0].c} customer records.`);
    console.log("   Run with '--reset' flag to re-import.");
    await showCounts();
    return;
  }
  
  let imported = 0;
  let skipped = 0;
  const BATCH = 50;
  
  for (let i = 0; i < records.length; i += BATCH) {
    const batch = records.slice(i, i + BATCH);
    const client = await pool.connect();
    
    try {
      await client.query('BEGIN');
      
      for (const rec of batch) {
        try {
          const cid = rec.customer_id;
          if (cid === null || cid === undefined) { skipped++; continue; }
          
          // 1. Central customer identity
          await client.query('INSERT INTO finance_customer_ids (customer_id) VALUES ($1) ON CONFLICT DO NOTHING', [cid]);
          
          // 2-20. Each field -> its own table
          await client.query('INSERT INTO finance_account_numbers (customer_id, account_number) VALUES ($1,$2) ON CONFLICT DO NOTHING', [cid, strVal(rec.account_number)]);
          await client.query('INSERT INTO finance_full_names (customer_id, full_name) VALUES ($1,$2) ON CONFLICT DO NOTHING', [cid, strVal(rec.full_name)]);
          await client.query('INSERT INTO finance_father_names (customer_id, father_name) VALUES ($1,$2) ON CONFLICT DO NOTHING', [cid, strVal(rec.father_name)]);
          await client.query('INSERT INTO finance_mother_names (customer_id, mother_name) VALUES ($1,$2) ON CONFLICT DO NOTHING', [cid, strVal(rec.mother_name)]);
          await client.query('INSERT INTO finance_dates_of_birth (customer_id, date_of_birth) VALUES ($1,$2) ON CONFLICT DO NOTHING', [cid, strVal(rec.date_of_birth)]);
          await client.query('INSERT INTO finance_cnic_dummies (customer_id, cnic_dummy) VALUES ($1,$2) ON CONFLICT DO NOTHING', [cid, strVal(rec.cnic_dummy)]);
          await client.query('INSERT INTO finance_phones (customer_id, phone) VALUES ($1,$2) ON CONFLICT DO NOTHING', [cid, strVal(rec.phone)]);
          await client.query('INSERT INTO finance_emails (customer_id, email) VALUES ($1,$2) ON CONFLICT DO NOTHING', [cid, strVal(rec.email)]);
          await client.query('INSERT INTO finance_addresses (customer_id, address) VALUES ($1,$2) ON CONFLICT DO NOTHING', [cid, strVal(rec.address)]);
          await client.query('INSERT INTO finance_cities (customer_id, city) VALUES ($1,$2) ON CONFLICT DO NOTHING', [cid, strVal(rec.city)]);
          await client.query('INSERT INTO finance_professions (customer_id, profession) VALUES ($1,$2) ON CONFLICT DO NOTHING', [cid, strVal(rec.profession)]);
          await client.query('INSERT INTO finance_employment_types (customer_id, employment_type) VALUES ($1,$2) ON CONFLICT DO NOTHING', [cid, strVal(rec.employment_type)]);
          await client.query('INSERT INTO finance_monthly_incomes (customer_id, monthly_income) VALUES ($1,$2) ON CONFLICT DO NOTHING', [cid, Number(rec.monthly_income) || 0]);
          await client.query('INSERT INTO finance_account_balances (customer_id, account_balance) VALUES ($1,$2) ON CONFLICT DO NOTHING', [cid, Number(rec.account_balance) || 0]);
          await client.query('INSERT INTO finance_credit_scores (customer_id, credit_score) VALUES ($1,$2) ON CONFLICT DO NOTHING', [cid, Number(rec.credit_score) || 0]);
          await client.query('INSERT INTO finance_existing_loans (customer_id, existing_loan) VALUES ($1,$2) ON CONFLICT DO NOTHING', [cid, rec.existing_loan ? true : false]);
          await client.query('INSERT INTO finance_loan_limits (customer_id, loan_limits) VALUES ($1,$2) ON CONFLICT DO NOTHING', [cid, Number(rec.loan_limits) || 0]);
          await client.query('INSERT INTO finance_bank_routing_numbers (customer_id, bank_routing_number) VALUES ($1,$2) ON CONFLICT DO NOTHING', [cid, strVal(rec.bank_routing_number)]);
          await client.query('INSERT INTO finance_passwords (customer_id, password) VALUES ($1,$2) ON CONFLICT DO NOTHING', [cid, strVal(rec.password)]);
          
          imported++;
        } catch (e) {
          console.log(`  ⚠️  Skipping (customer_id=${rec.customer_id}): ${e.message}`);
          skipped++;
        }
      }
      
      await client.query('COMMIT');
      console.log(`  ✅ Imported ${Math.min(i + BATCH, records.length)} / ${records.length} records...`);
    } catch (e) {
      await client.query('ROLLBACK');
      console.error(`  ❌ Batch error at ${i}: ${e.message}`);
    } finally {
      client.release();
    }
  }
  
  console.log(`\n${'='.repeat(60)}`);
  console.log('🎉 Import complete!');
  console.log(`   ✅ ${imported} records imported`);
  console.log(`   ⚠️  ${skipped} records skipped`);
  console.log('\n📊 Table row counts in Neon PostgreSQL:');

// ──────────────────────────────────────────────
// CLI Entry Point
// ──────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--show')) { await showTables(); await pool.end(); return; }
  if (args.includes('--counts')) { await showCounts(); await pool.end(); return; }
  
  if (args.includes('--reset')) {
    console.log('🔄 Resetting tables...');
    await dropAllTables();
  }
  
  const jsonIdx = args.indexOf('--json');
  const jsonPath = jsonIdx !== -1 ? args[jsonIdx + 1] : null;
  
  await importData(jsonPath);
  await pool.end();
}

main().catch(err => {
  console.error('\n❌ Fatal error:', err);
  pool.end().catch(() => {});
  process.exit(1);
});

  await showCounts();
}
