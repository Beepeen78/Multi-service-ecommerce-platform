from flask import Flask, request, jsonify
import psycopg2
import redis
import os
import json
from datetime import datetime

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'postgres'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'ecommerce'),
        user=os.getenv('DB_USER', 'ecommerce'),
        password=os.getenv('DB_PASSWORD', 'ecommerce123')
    )
    return conn

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', '6379')),
    decode_responses=True
)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'recommendation-service'})

@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    try:
        # Check cache
        cache_key = f'recommendations:{user_id}'
        cached = redis_client.get(cache_key)
        if cached:
            return jsonify(json.loads(cached))
        
        # Get user's order history
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get user's purchased products
        cur.execute('''
            SELECT DISTINCT oi.product_id, COUNT(*) as purchase_count
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            WHERE o.user_id = %s AND o.status = 'completed'
            GROUP BY oi.product_id
            ORDER BY purchase_count DESC
            LIMIT 10
        ''', (user_id,))
        
        purchased_products = [row[0] for row in cur.fetchall()]
        
        # Get similar products based on category
        recommendations = []
        if purchased_products:
            placeholders = ','.join(['%s'] * len(purchased_products))
            cur.execute(f'''
                SELECT DISTINCT p.id, p.name, p.price, p.category
                FROM products p
                WHERE p.category IN (
                    SELECT DISTINCT category FROM products WHERE id IN ({placeholders})
                )
                AND p.id NOT IN ({placeholders})
                ORDER BY p.price DESC
                LIMIT 10
            ''', purchased_products + purchased_products)
            
            recommendations = [
                {
                    'product_id': row[0],
                    'name': row[1],
                    'price': float(row[2]),
                    'category': row[3]
                }
                for row in cur.fetchall()
            ]
        
        # If no recommendations, get popular products
        if not recommendations:
            cur.execute('''
                SELECT p.id, p.name, p.price, p.category
                FROM products p
                JOIN (
                    SELECT product_id, COUNT(*) as order_count
                    FROM order_items
                    GROUP BY product_id
                    ORDER BY order_count DESC
                    LIMIT 10
                ) popular ON p.id = popular.product_id
            ''')
            
            recommendations = [
                {
                    'product_id': row[0],
                    'name': row[1],
                    'price': float(row[2]),
                    'category': row[3]
                }
                for row in cur.fetchall()
            ]
        
        cur.close()
        conn.close()
        
        result = {
            'user_id': user_id,
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat()
        }
        
        # Cache for 1 hour
        redis_client.setex(cache_key, 3600, json.dumps(result))
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations/product/<int:product_id>', methods=['GET'])
def get_product_recommendations(product_id):
    try:
        cache_key = f'product_recommendations:{product_id}'
        cached = redis_client.get(cache_key)
        if cached:
            return jsonify(json.loads(cached))
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get product category
        cur.execute('SELECT category FROM products WHERE id = %s', (product_id,))
        result = cur.fetchone()
        
        if not result:
            return jsonify({'error': 'Product not found'}), 404
        
        category = result[0]
        
        # Get similar products in same category
        cur.execute('''
            SELECT id, name, price, category
            FROM products
            WHERE category = %s AND id != %s
            ORDER BY price DESC
            LIMIT 10
        ''', (category, product_id))
        
        recommendations = [
            {
                'product_id': row[0],
                'name': row[1],
                'price': float(row[2]),
                'category': row[3]
            }
            for row in cur.fetchall()
        ]
        
        cur.close()
        conn.close()
        
        result = {
            'product_id': product_id,
            'recommendations': recommendations
        }
        
        redis_client.setex(cache_key, 3600, json.dumps(result))
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', '3009'))
    app.run(host='0.0.0.0', port=port)

