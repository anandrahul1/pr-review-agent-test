const express = require('express');
const app = express();

// Vulnerable: SQL injection
app.get('/user/:id', (req, res) => {
  const query = `SELECT * FROM users WHERE id = ${req.params.id}`;
  db.query(query, (err, results) => {
    res.json(results);
  });
});

// Vulnerable: Hardcoded credentials
const DB_PASSWORD = "admin123";
const API_KEY = "sk_live_51234567890";

// Vulnerable: eval() usage
app.post('/calculate', (req, res) => {
  const result = eval(req.body.expression);
  res.json({ result });
});

app.listen(3000);
// Trigger review
// Trigger review v2
// Trigger review v3
// Trigger review v4
