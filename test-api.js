// Test API with vulnerabilities
const db = require('./db');

// SQL Injection
app.get('/user', (req, res) => {
  db.query(`SELECT * FROM users WHERE id = ${req.query.id}`);
});

// Hardcoded secret
const SECRET = "sk-prod-1234567890";
// Update 1767160067
// Fix permissions 1767160695
