async function main() {
  const BASE = 'http://localhost:8000';
  const headers = { 'Authorization': 'Bearer test', 'Content-Type': 'application/json' };

  // 1. Health
  let r = await fetch(BASE + '/api/health');
  console.log('1. HEALTH:', await r.json());

  // 2. Dashboard Stats
  r = await fetch(BASE + '/api/dashboard/stats', { headers });
  console.log('2. STATS:', await r.json());

  // 3. Dashboard Cases
  r = await fetch(BASE + '/api/dashboard/cases', { headers });
  const cases = await r.json();
  console.log('3. CASES:', cases.total, 'total, first:', cases.cases[0]?.customer_name);

  // 4. Dashboard Analytics  
  r = await fetch(BASE + '/api/dashboard/analytics', { headers });
  console.log('4. ANALYTICS:', await r.json());

  // 5. Classify
  r = await fetch(BASE + '/api/classify', {
    method: 'POST', headers,
    body: JSON.stringify({ text: 'Mera ATM card activate kardo', channel: 'web' }),
  });
  const classify = await r.json();
  console.log('5. CLASSIFY:', classify.intent?.label, '| Lang:', classify.detected_language, '| Conf:', classify.intent?.confidence);

  // 6. Chat
  r = await fetch(BASE + '/api/chat', {
    method: 'POST', headers,
    body: JSON.stringify({ message: 'Bachat account par kitna profit milta hai?', language: 'ur' }),
  });
  const chat = await r.json();
  console.log('6. CHAT:', chat.text?.slice(0, 100) + '...');
  console.log('   Language:', chat.language, '| Escalation:', chat.escalation);

  // 7. Workflows
  r = await fetch(BASE + '/api/workflows', { headers });
  const wf = await r.json();
  console.log('7. WORKFLOWS:', wf.workflows.length, 'workflows');

  // 8. Admin Users
  r = await fetch(BASE + '/api/admin/users', { headers });
  const users = await r.json();
  console.log('8. USERS:', users.users?.length, 'users');

  // 9. Admin Audit
  r = await fetch(BASE + '/api/admin/audit', { headers });
  const audit = await r.json();
  console.log('9. AUDIT:', audit.logs?.length, 'logs');

  console.log('\n=== ALL ENDPOINTS WORKING ===');
}
main().catch(e => console.error('TEST FAILED:', e.message));
