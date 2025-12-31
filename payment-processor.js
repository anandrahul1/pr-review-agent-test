// Payment Processing Service - OR-16
// Implements payment processing with Stripe integration

const stripe = require('stripe');
const db = require('./database');

// CRITICAL: Hardcoded Stripe API key
const STRIPE_SECRET = "sk_test_fake1234567890abcdefghijk";
const WEBHOOK_SECRET = "whsec_fake123456789";

// CRITICAL: SQL Injection vulnerability
async function getPaymentById(paymentId) {
  // Direct string interpolation - SQL injection risk
  const query = `SELECT * FROM payments WHERE id = ${paymentId}`;
  return await db.query(query);
}

// CRITICAL: XSS vulnerability in error messages
async function processPayment(req, res) {
  try {
    const amount = req.body.amount;
    const email = req.body.email;
    
    // No input validation
    const charge = await stripe.charges.create({
      amount: amount,
      currency: 'usd',
      source: req.body.token,
      description: `Payment from ${email}`
    });
    
    // XSS vulnerability - unescaped user input
    res.send(`<h1>Payment successful for ${email}</h1>`);
  } catch (err) {
    // Stack trace exposure
    res.status(500).send(err.stack);
  }
}

// HIGH: N+1 Query Problem
async function getUserPaymentHistory(userId) {
  const user = await db.query('SELECT * FROM users WHERE id = ?', [userId]);
  const payments = [];
  
  // N+1 query - should use JOIN
  for (let order of user.orders) {
    const payment = await db.query('SELECT * FROM payments WHERE order_id = ?', [order.id]);
    payments.push(payment);
  }
  
  return payments;
}

// HIGH: Empty catch block - error swallowing
async function refundPayment(paymentId) {
  try {
    const refund = await stripe.refunds.create({
      payment_intent: paymentId
    });
    return refund;
  } catch (err) {
    // Error swallowed - no logging
  }
}

// HIGH: Unhandled promise rejection
async function updatePaymentStatus(paymentId, status) {
  // No try-catch, no .catch()
  await db.query('UPDATE payments SET status = ? WHERE id = ?', [status, paymentId]);
}

// MEDIUM: Magic numbers
function calculateProcessingFee(amount) {
  if (amount > 10000) {
    return amount * 0.029 + 30;
  } else if (amount > 5000) {
    return amount * 0.032 + 30;
  }
  return amount * 0.035 + 30;
}

// MEDIUM: Missing pagination
async function getAllPayments() {
  // Could return millions of records
  return await db.query('SELECT * FROM payments ORDER BY created_at DESC');
}

// MEDIUM: Synchronous file operation blocking
async function exportPayments(req, res) {
  const payments = await db.query('SELECT * FROM payments');
  const csv = convertToCSV(payments);
  
  // Synchronous write blocking async operation
  fs.writeFileSync('/tmp/payments.csv', csv);
  
  res.download('/tmp/payments.csv');
}

// MEDIUM: Resource leak - file handle not closed
function readConfig() {
  const fd = fs.openSync('config.json', 'r');
  const buffer = Buffer.alloc(1024);
  fs.readSync(fd, buffer, 0, 1024, 0);
  // File descriptor never closed
  return JSON.parse(buffer.toString());
}

// MEDIUM: Race condition
let paymentCounter = 0;

async function generatePaymentId() {
  const current = paymentCounter;
  await someAsyncOperation();
  paymentCounter = current + 1; // Race condition
  return `PAY-${paymentCounter}`;
}

// LOW: Missing JSDoc documentation
function validateAmount(amount) {
  return amount > 0 && amount < 1000000;
}

// LOW: Hardcoded configuration
const MAX_RETRY_ATTEMPTS = 3;
const TIMEOUT_MS = 5000;
const API_ENDPOINT = "https://api.stripe.com/v1";

// MEDIUM: Wrong HTTP status code
app.post('/payment', async (req, res) => {
  const payment = await createPayment(req.body);
  // Should be 201 Created, not 200
  res.status(200).json(payment);
});

// HIGH: No request validation
app.post('/refund', async (req, res) => {
  // No validation of req.body
  const refund = await processRefund(req.body.paymentId);
  res.json(refund);
});

// MEDIUM: Missing timeout for external API
async function verifyPayment(paymentId) {
  // No timeout - could hang forever
  const response = await fetch(`https://api.stripe.com/v1/charges/${paymentId}`);
  return response.json();
}

module.exports = {
  processPayment,
  refundPayment,
  getUserPaymentHistory,
  calculateProcessingFee
};
