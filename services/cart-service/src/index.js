const express = require('express');
const redis = require('redis');
require('dotenv').config();

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3005;

const redisClient = redis.createClient({
  url: process.env.REDIS_URL || 'redis://redis:6379'
});

redisClient.on('error', (err) => console.error('Redis Client Error', err));
redisClient.connect().catch(console.error);

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'cart-service' });
});

app.get('/api/cart/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const cart = await redisClient.get(`cart:${userId}`);
    
    if (!cart) {
      return res.json({ items: [] });
    }
    
    res.json(JSON.parse(cart));
  } catch (error) {
    console.error('Error fetching cart:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/api/cart/:userId/items', async (req, res) => {
  try {
    const { userId } = req.params;
    const { productId, quantity, price } = req.body;
    
    const cartKey = `cart:${userId}`;
    const cart = await redisClient.get(cartKey);
    
    let items = cart ? JSON.parse(cart).items : [];
    
    const existingIndex = items.findIndex(item => item.productId === productId);
    if (existingIndex >= 0) {
      items[existingIndex].quantity += quantity;
    } else {
      items.push({ productId, quantity, price });
    }
    
    await redisClient.setEx(cartKey, 86400, JSON.stringify({ items }));
    
    res.json({ items });
  } catch (error) {
    console.error('Error adding to cart:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.delete('/api/cart/:userId/items/:productId', async (req, res) => {
  try {
    const { userId, productId } = req.params;
    const cartKey = `cart:${userId}`;
    const cart = await redisClient.get(cartKey);
    
    if (!cart) {
      return res.status(404).json({ error: 'Cart not found' });
    }
    
    let { items } = JSON.parse(cart);
    items = items.filter(item => item.productId !== productId);
    
    await redisClient.setEx(cartKey, 86400, JSON.stringify({ items }));
    
    res.json({ items });
  } catch (error) {
    console.error('Error removing from cart:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.delete('/api/cart/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    await redisClient.del(`cart:${userId}`);
    res.json({ message: 'Cart cleared' });
  } catch (error) {
    console.error('Error clearing cart:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.listen(PORT, () => {
  console.log(`Cart service running on port ${PORT}`);
});

