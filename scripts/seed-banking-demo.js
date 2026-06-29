// SmartBank — Seed Banking Demo Data
// Usage: node scripts/seed-banking-demo.js
// Creates sample NADRA, CBS, 1LINK, Raast records in the local SQLite DB
// and attempts to write to Firestore if configured.

(async () => {
const path = require('path')
const fs = require('fs')
const crypto = require('crypto')
require('dotenv').config({ path: path.join(__dirname, '..', '.env') })

// Attempt to load firebase-admin — ignore if unavailable
let firestore = null
let admin = null
try {
  admin = require('firebase-admin')
  const fbPath = path.join(__dirname, '..', 'firebase-service-account.json')
  if (fs.existsSync(fbPath)) {
    const serviceAccount = require(fbPath)
    if (!admin.apps.length) {
      admin.initializeApp({ credential: admin.cert(serviceAccount) })
    }
    firestore = admin.firestore()
    console.log('Firestore connected ✓')
  }
} catch (e) {
  console.log('Firestore not available (will use local DB only)')
}

// Local SQLite
const dbPath = path.join(__dirname, '..', process.env.DB_PATH || 'smartbank.db')
let db = null
try {
  const Database = require('better-sqlite3')
  db = new Database(dbPath)
  console.log('SQLite connected ✓')
} catch (e) {
  console.log('SQLite not available:', e.message)
  process.exit(1)
}

// Table helper
const tbl = name => {
  const pg = process.env.USE_POSTGRES === 'true'
  return pg ? `"${name}"` : name
}

const uid = 'demo-seed-user'
const ts = new Date().toISOString()

// 1. Create sample NADRA verification logs
console.log('\n--- Seeding NADRA Verifications ---')
const testCnic = '12345-1234567-1'
const failedCnic = '54321-1234567-1'

const nadraEntries = [
  { cnic: testCnic, verified: true, timestamp: ts },
  { cnic: failedCnic, verified: false, timestamp: ts },
  { cnic: testCnic, verified: true, timestamp: new Date(Date.now() - 86400000).toISOString() },
]

for (const entry of nadraEntries) {
  try {
    db.prepare(`INSERT INTO ${tbl('audit_logs')} (action, actor, resource, details) VALUES (?,?,?,?)`).run(
      'NADRA_VERIFY', uid, '/api/nadra/verify',
      JSON.stringify({ cnic: entry.cnic, verified: entry.verified, timestamp: entry.timestamp }))
    console.log(`  NADRA ${entry.cnic} → ${entry.verified ? 'VERIFIED' : 'NOT FOUND'}`)
  } catch (e) { console.log(`  NADRA skip: ${e.message}`) }

  if (firestore) {
    await firestore.collection('verification_logs').add({
      userId: uid, cnic: entry.cnic, verified: entry.verified,
      type: 'nadra', timestamp: entry.timestamp,
    }).catch(() => {})
  }
}

// 2. Create sample CBS account checks
console.log('\n--- Seeding CBS Account Checks ---')
const testAcct = 'PK00123456789'
const unknownAcct = 'PK00999999999'

const cbsEntries = [
  { accountNumber: testAcct, status: 'active', customerName: 'Muhammad Ali', availableBalance: 50000 },
  { accountNumber: unknownAcct, status: 'not_found', customerName: null, availableBalance: 0 },
  { accountNumber: testAcct, status: 'active', customerName: 'Muhammad Ali', availableBalance: 47500 },
]

for (const entry of cbsEntries) {
  try {
    db.prepare(`INSERT INTO ${tbl('audit_logs')} (action, actor, resource, details) VALUES (?,?,?,?)`).run(
      'CBS_CHECK', uid, '/api/cbs/account-check',
      JSON.stringify({ accountNumber: entry.accountNumber, status: entry.status, customerName: entry.customerName, balance: entry.availableBalance }))
    console.log(`  CBS ${entry.accountNumber} → ${entry.status.toUpperCase()}`)
  } catch (e) {}

  if (firestore) {
    await firestore.collection('transactions').add({
      userId: uid, accountNumber: entry.accountNumber, type: 'cbs_check',
      status: entry.status, timestamp: ts,
    }).catch(() => {})
  }
}

// 3. Create sample 1LINK payments
console.log('\n--- Seeding 1LINK Payments ---')
const paymentEntries = [
  { accountNumber: testAcct, amount: 2500 },
  { accountNumber: testAcct, amount: 5000 },
  { accountNumber: testAcct, amount: 10000 },
]

for (const entry of paymentEntries) {
  const txnId = 'TXN' + crypto.randomUUID().slice(0, 8).toUpperCase()
  try {
    db.prepare(`INSERT INTO ${tbl('audit_logs')} (action, actor, resource, details) VALUES (?,?,?,?)`).run(
      'ONELINK_PAYMENT', uid, '/api/onelink/payment',
      JSON.stringify({ accountNumber: entry.accountNumber, amount: entry.amount, transactionId: txnId, status: 'success' }))
    console.log(`  1LINK PKR ${entry.amount} → ${txnId}`)
  } catch (e) {}

  if (firestore) {
    await firestore.collection('payments').add({
      userId: uid, accountNumber: entry.accountNumber, amount: entry.amount,
      transactionId: txnId, status: 'success', timestamp: ts,
    }).catch(() => {})
  }
}

// 4. Create sample Raast transfers
console.log('\n--- Seeding Raast Transfers ---')
const transferEntries = [
  { receiverAccount: 'PK00987654321', amount: 1500 },
  { receiverAccount: 'PK00555555555', amount: 3000 },
  { receiverAccount: 'PK00111111111', amount: 7500 },
]

for (const entry of transferEntries) {
  const refId = 'RAAST' + crypto.randomUUID().slice(0, 8).toUpperCase()
  try {
    db.prepare(`INSERT INTO ${tbl('audit_logs')} (action, actor, resource, details) VALUES (?,?,?,?)`).run(
      'RAAST_TRANSFER', uid, '/api/raast/transfer',
      JSON.stringify({ receiverAccount: entry.receiverAccount, amount: entry.amount, referenceId: refId, status: 'completed' }))
    console.log(`  Raast PKR ${entry.amount} → ${refId}`)
  } catch (e) {}

  if (firestore) {
    await firestore.collection('transfers').add({
      userId: uid, receiverAccount: entry.receiverAccount, amount: entry.amount,
      referenceId: refId, status: 'completed', timestamp: ts,
    }).catch(() => {})
  }
}

// 5. Create sample workflow execution
console.log('\n--- Seeding Workflow Execution ---')
try {
  db.prepare('INSERT INTO workflow_executions (workflow_name,case_id,status,started_at,completed_at) VALUES (?,?,?,?,?)').run(
    'banking-workflow', 'BNK-DEMO001', 'completed', ts, ts)
  db.prepare('INSERT INTO workflow_executions (workflow_name,case_id,status,started_at,completed_at) VALUES (?,?,?,?,?)').run(
    'banking-workflow', 'BNK-DEMO002', 'running', ts, null)
  console.log('  Workflow executions created')
} catch (e) {}

console.log('\n✓ Banking demo data seeded successfully!')
console.log(`  Test CNIC:     ${testCnic}`)
console.log(`  Test Account:  ${testAcct}`)
console.log('  Try the UI at: http://localhost:8000/banking')
console.log('  Try the API:   curl -X POST http://localhost:8000/api/workflows/trigger-banking -H "Authorization: Bearer demo-token" -H "Content-Type: application/json" -d \'{"cnic":"12345-1234567-1","accountNumber":"PK00123456789","amount":5000}\'')
console.log('')

if (db) db.close()
})()
