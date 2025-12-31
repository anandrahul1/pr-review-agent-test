// User Service - Comprehensive Test for PR Review Agent
// This file intentionally contains multiple issues to test all review features

const express = require('express');
const app = express();

// SECURITY ISSUES:
// 1. Hardcoded secret
const API_KEY = "sk-prod-1234567890abcdef";
const DB_PASSWORD = "admin123";

// 2. SQL Injection vulnerability
app.get('/user', (req, res) => {
  const userId = req.query.id;
  // Direct string interpolation - SQL injection risk
  db.query(`SELECT * FROM users WHERE id = ${userId}`, (err, result) => {
    if (err) {
      // 3. Information disclosure - exposing stack trace
      res.status(500).send(err.stack);
    }
    res.json(result);
  });
});

// 4. XSS vulnerability
app.get('/search', (req, res) => {
  const searchTerm = req.query.q;
  res.send(`<h1>Results for: ${searchTerm}</h1>`);
});

// CODE QUALITY ISSUES:
// 5. God object - doing too much
class UserManager {
  createUser(data) { /* ... */ }
  deleteUser(id) { /* ... */ }
  sendEmail(user) { /* ... */ }
  generateReport(user) { /* ... */ }
  processPayment(user, amount) { /* ... */ }
  validateAddress(address) { /* ... */ }
  calculateTax(amount) { /* ... */ }
}

// 6. Long function with deep nesting
function processOrder(order, user, payment, shipping, discount, coupon, tax, insurance, gift) {
  if (order) {
    if (user) {
      if (payment) {
        if (shipping) {
          if (discount) {
            if (coupon) {
              if (tax) {
                if (insurance) {
                  // Too deep nesting
                  return true;
                }
              }
            }
          }
        }
      }
    }
  }
  return false;
}

// 7. Magic numbers
function calculateDiscount(price) {
  if (price > 100) {
    return price * 0.15;
  } else if (price > 50) {
    return price * 0.10;
  }
  return price * 0.05;
}

// 8. Code duplication
function getUserById(id) {
  const connection = db.connect();
  const result = connection.query(`SELECT * FROM users WHERE id = ${id}`);
  connection.close();
  return result;
}

function getOrderById(id) {
  const connection = db.connect();
  const result = connection.query(`SELECT * FROM orders WHERE id = ${id}`);
  connection.close();
  return result;
}

// PERFORMANCE ISSUES:
// 9. N+1 query problem
async function getUsersWithOrders() {
  const users = await db.query('SELECT * FROM users');
  for (let user of users) {
    // N+1 query - should use JOIN
    user.orders = await db.query(`SELECT * FROM orders WHERE user_id = ${user.id}`);
  }
  return users;
}

// 10. Missing pagination
app.get('/all-users', async (req, res) => {
  // No pagination - could return millions of records
  const users = await db.query('SELECT * FROM users');
  res.json(users);
});

// 11. Synchronous operation blocking async
app.get('/report', async (req, res) => {
  const data = await fetchData();
  // Synchronous file write blocking
  fs.writeFileSync('/tmp/report.txt', JSON.stringify(data));
  res.send('Done');
});

// ERROR HANDLING ISSUES:
// 12. Empty catch block - error swallowing
async function fetchUserData(id) {
  try {
    return await api.getUser(id);
  } catch (err) {
    // Empty catch - error swallowed
  }
}

// 13. Unhandled promise rejection
async function updateUser(id, data) {
  // No try-catch, no .catch()
  await db.update('users', id, data);
}

// 14. Missing timeout
async function callExternalAPI() {
  // No timeout - could hang forever
  const response = await fetch('https://external-api.com/data');
  return response.json();
}

// RESOURCE MANAGEMENT ISSUES:
// 15. File handle not closed
function readConfig() {
  const file = fs.openSync('config.json', 'r');
  const data = fs.readFileSync(file);
  // File handle never closed
  return JSON.parse(data);
}

// 16. Memory leak - event listener not removed
class DataStream {
  constructor() {
    this.emitter = new EventEmitter();
    this.emitter.on('data', this.handleData);
    // Listener never removed
  }
  
  handleData(data) {
    console.log(data);
  }
}

// DATABASE ISSUES:
// 17. Missing index hint
async function searchUsers(name) {
  // Should have index on name column
  return await db.query('SELECT * FROM users WHERE name LIKE ?', [`%${name}%`]);
}

// API DESIGN ISSUES:
// 18. Wrong HTTP status code
app.post('/user', (req, res) => {
  const user = createUser(req.body);
  // Should be 201 Created, not 200
  res.status(200).json(user);
});

// 19. No request validation
app.post('/order', (req, res) => {
  // No validation of req.body
  const order = db.insert('orders', req.body);
  res.json(order);
});

// BACKWARDS COMPATIBILITY ISSUES:
// 20. Breaking API change
// Old signature: getUser(id)
// New signature: getUser(id, includeOrders) - breaking change
function getUser(id, includeOrders) {
  // Changed function signature without deprecation
}

// TESTING ISSUES:
// 21. NO TESTS PROVIDED - This entire file has no test coverage

// DOCUMENTATION ISSUES:
// 22. No JSDoc comments
// 23. Complex logic without explanation

// CONCURRENCY ISSUES:
// 24. Race condition
let counter = 0;
async function incrementCounter() {
  const current = counter;
  await someAsyncOperation();
  counter = current + 1; // Race condition
}

// CONFIGURATION ISSUES:
// 25. Hardcoded configuration
const MAX_RETRIES = 3;
const TIMEOUT = 5000;
const API_URL = "https://api.example.com";

module.exports = { UserManager, processOrder, getUsersWithOrders };
