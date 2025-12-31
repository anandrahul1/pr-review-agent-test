// API with security issues
const express = require('express');
const app = express();

// SQL Injection vulnerability
app.get('/user', (req, res) => {
  const query = `SELECT * FROM users WHERE id = ${req.query.id}`;
  db.query(query);
});

// Hardcoded credentials
const API_KEY = "sk-1234567890abcdef";
const DB_PASSWORD = "admin123";

// Using eval
app.post('/calc', (req, res) => {
  const result = eval(req.body.expression);
  res.json({ result });
});
