#!/usr/bin/env node
/**
 * run_import_neon.cjs
 * Import finance_data.json -> Neon PostgreSQL (har field ka alag table)
 * Usage: node scripts/run_import_neon.cjs
 */

require('dotenv').config();
const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
  connectionTimeoutMillis: 30000,
  max: 10,
});

async function run() {
  // 1. Create tables from SQL file
  console.log('🏗️  Creating 20 tables...');
  const sql = fs.readFileSync(path.join(__dirname, 'tables.sql'), 'utf8');
  await pool.query(sql);
  console.log('✅ Tables created/verified.');

  // 2. Load JSON data
  const jsonPath = path.join(__dirname, '..', 'finance_data.json');
  const records = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
  console.log(`📦 ${records.length} records loaded.`);

  // 3. Check existing
  const { rows } = await pool.query('SELECT COUNT(*)::int as c FROM finance_customer_ids');
  if (rows[0].c > 0) {
    console.log(`⚠️  Already has ${rows[0].c} records. Use --reset to re-import.`);
    await pool.end();
    return;
  }

  // 4. Import in batches
  let imported = 0, skipped = 0, BATCH = 50;

  for (let i = 0; i < records.length; i += BATCH) {
    const batch = records.slice(i, i + BATCH);
    const client = await pool.connect();
    try {
      await client.query('BEGIN');
      for (const r of batch) {
        try {
          const cid = r.customer_id;
          if (cid == null) { skipped++; continue; }

          const ins = (tbl, col, val) =>
            client.query(`INSERT INTO ${tbl} (customer_id, ${col}) VALUES ($1,$2) ON CONFLICT DO NOTHING`, [cid, val]);

          await client.query('INSERT INTO finance_customer_ids (customer_id) VALUES ($1) ON CONFLICT DO NOTHING', [cid]);
          await ins('finance_account_numbers', 'account_number', r.account_number != null ? String(r.account_number) : null);
          await ins('finance_full_names', 'full_name', r.full_name != null ? String(r.full_name) : null);
          await ins('finance_father_names', 'father_name', r.father_name != null ? String(r.father_name) : null);
          await ins('finance_mother_names', 'mother_name', r.mother_name != null ? String(r.mother_name) : null);
          await ins('finance_dates_of_birth', 'date_of_birth', r.date_of_birth != null ? String(r.date_of_birth) : null);
          await ins('finance_cnic_dummies', 'cnic_dummy', r.cnic_dummy != null ? String(r.cnic_dummy) : null);
          await ins('finance_phones', 'phone', r.phone != null ? String(r.phone) : null);
          await ins('finance_emails', 'email', r.email != null ? String(r.email) : null);
          await ins('finance_addresses', 'address', r.address != null ? String(r.address) : null);
          await ins('finance_cities', 'city', r.city != null ? String(r.city) : null);
          await ins('finance_professions', 'profession', r.profession != null ? String(r.profession) : null);
          await ins('finance_employment_types', 'employment_type', r.employment_type != null ? String(r.employment_type) : null);
          await ins('finance_monthly_incomes', 'monthly_income', Number(r.monthly_income) || 0);
          await ins('finance_account_balances', 'account_balance', Number(r.account_balance) || 0);
          await ins('finance_credit_scores', 'credit_score', Number(r.credit_score) || 0);
          await ins('finance_existing_loans', 'existing_loan', !!r.existing_loan);
          await ins('finance_loan_limits', 'loan_limits', Number(r.loan_limits) || 0);
          await ins('finance_bank_routing_numbers', 'bank_routing_number', r.bank_routing_number != null ? String(r.bank_routing_number) : null);
          await ins('finance_passwords', 'password', r.password != null ? String(r.password) : null);

          imported++;
        } catch (e) {
          console.log(`  ⚠️  Skip id=${r.customer_id}: ${e.message}`);
          skipped++;
        }
      }
      await client.query('COMMIT');
      const done = Math.min(i + BATCH, records.length);
      process.stdout.write(`\r  ✅ ${done}/${records.length} (${imported} imported, ${skipped} skipped)`);
    } catch (e) {
      await client.query('ROLLBACK');
      console.error(`\n  ❌ Batch error at ${i}: ${e.message}`);
    } finally {
      client.release();
    }
  }

  console.log(`\n${'='.repeat(60)}`);
  console.log('🎉 Done!');
  console.log(`   ✅ Imported: ${imported}`);
  console.log(`   ⚠️  Skipped: ${skipped}`);

  // 5. Show final counts
  console.log('\n📊 Final row counts:');
  const tables = [
    'finance_customer_ids', 'finance_account_numbers', 'finance_full_names',
    'finance_father_names', 'finance_mother_names', 'finance_dates_of_birth',
    'finance_cnic_dummies', 'finance_phones', 'finance_emails', 'finance_addresses',
    'finance_cities', 'finance_professions', 'finance_employment_types',
    'finance_monthly_incomes', 'finance_account_balances', 'finance_credit_scores',
    'finance_existing_loans', 'finance_loan_limits', 'finance_bank_routing_numbers',
    'finance_passwords',
  ];
  for (const t of tables) {
    const r = await pool.query(`SELECT COUNT(*)::int as c FROM ${t}`);
    console.log(`   🗂️  ${t}: ${r.rows[0].c} rows`);
  }

  await pool.end();
}

run().catch(err => {
  console.error('❌', err);
  pool.end().catch(() => {});
  process.exit(1);
});
