const express = require('express');
const { Pool } = require('pg');
const redis = require('redis');
require('dotenv').config();

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3007;

const pgPool = new Pool({
  host: process.env.DB_HOST || 'postgres',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'ecommerce',
  user: process.env.DB_USER || 'ecommerce',
  password: process.env.DB_PASSWORD || 'ecommerce123',
});

const redisClient = redis.createClient({
  url: process.env.REDIS_URL || 'redis://redis:6379'
});

redisClient.on('error', (err) => console.error('Redis Client Error', err));
redisClient.connect().catch(console.error);

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'payment-service' });
});

app.post('/api/payments', async (req, res) => {
  try {
    const { orderId, amount, paymentMethod, cardToken } = req.body;
    
    if (!orderId || !amount || !paymentMethod) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    // Simulate payment processing
    const paymentStatus = Math.random() > 0.1 ? 'completed' : 'failed';
    const transactionId = `txn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const result = await pgPool.query(
      'INSERT INTO payments (order_id, amount, payment_method, status, transaction_id, created_at) VALUES ($1, $2, $3, $4, $5, NOW()) RETURNING *',
      [orderId, amount, paymentMethod, paymentStatus, transactionId]
    );

    const payment = result.rows[0];

    // Cache payment status
    await redisClient.setEx(`payment:${orderId}`, 3600, JSON.stringify(payment));

    res.status(201).json(payment);
  } catch (error) {
    console.error('Error processing payment:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/payments/:orderId', async (req, res) => {
  try {
    const { orderId } = req.params;
    
    const cached = await redisClient.get(`payment:${orderId}`);
    if (cached) {
      return res.json(JSON.parse(cached));
    }

    const result = await pgPool.query(
      'SELECT * FROM payments WHERE order_id = $1 ORDER BY created_at DESC LIMIT 1',
      [orderId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Payment not found' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error('Error fetching payment:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.listen(PORT, () => {
  console.log(`Payment service running on port ${PORT}`);
});

