// Payment Service - Final Test
// Testing all review features with various issues

const stripe = require('stripe');

// CRITICAL: Hardcoded API key
const STRIPE_KEY = "sk_live_51234567890abcdef";

// CRITICAL: SQL Injection
async function getPayment(paymentId) {
  return await db.query(`SELECT * FROM payments WHERE id = ${paymentId}`);
}

// HIGH: N+1 Query Problem
async function getUserPayments(userId) {
  const user = await db.query('SELECT * FROM users WHERE id = ?', [userId]);
  const payments = [];
  for (let order of user.orders) {
    // N+1 query - should use JOIN
    const payment = await db.query('SELECT * FROM payments WHERE order_id = ?', [order.id]);
    payments.push(payment);
  }
  return payments;
}

// HIGH: Empty catch block
async function processRefund(paymentId) {
  try {
    await stripe.refunds.create({ payment_intent: paymentId });
  } catch (err) {
    // Error swallowed - no logging
  }
}

// MEDIUM: Magic numbers
function calculateFee(amount) {
  if (amount > 1000) {
    return amount * 0.029 + 0.30;
  }
  return amount * 0.035 + 0.30;
}

// MEDIUM: Missing pagination
async function getAllPayments() {
  return await db.query('SELECT * FROM payments');
}

// LOW: No JSDoc
function validateCard(cardNumber) {
  return cardNumber.length === 16;
}

module.exports = { getPayment, processRefund, calculateFee };
