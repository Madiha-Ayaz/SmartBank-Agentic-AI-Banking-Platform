const Database = require('better-sqlite3');
const db = new Database('smartbank.db');
const tables = db.prepare("SELECT name FROM sqlite_master WHERE type='table'").all();
for (const t of tables) {
  console.log('TABLE:', t.name);
  const cols = db.prepare('PRAGMA table_info(' + t.name + ')').all();
  for (const c of cols) console.log('  ', c.name, c.type);
}
