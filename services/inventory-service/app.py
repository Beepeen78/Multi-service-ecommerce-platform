from flask import Flask, request, jsonify
import psycopg2
import redis
import os
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
    return jsonify({'status': 'healthy', 'service': 'inventory-service'})

@app.route('/api/inventory/<int:product_id>', methods=['GET'])
def get_inventory(product_id):
    try:
        # Check cache
        cache_key = f'inventory:{product_id}'
        cached = redis_client.get(cache_key)
        if cached:
            return jsonify(eval(cached))
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'SELECT product_id, quantity, reserved, available FROM inventory WHERE product_id = %s',
            (product_id,)
        )
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if not result:
            return jsonify({'error': 'Inventory not found'}), 404
        
        inventory = {
            'product_id': result[0],
            'quantity': result[1],
            'reserved': result[2],
            'available': result[3]
        }
        
        # Cache for 5 minutes
        redis_client.setex(cache_key, 300, str(inventory))
        
        return jsonify(inventory)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/<int:product_id>/reserve', methods=['POST'])
def reserve_inventory(product_id):
    try:
        data = request.json
        quantity = data.get('quantity', 0)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check available inventory
        cur.execute(
            'SELECT available FROM inventory WHERE product_id = %s FOR UPDATE',
            (product_id,)
        )
        result = cur.fetchone()
        
        if not result:
            cur.close()
            conn.close()
            return jsonify({'error': 'Inventory not found'}), 404
        
        available = result[0]
        if available < quantity:
            cur.close()
            conn.close()
            return jsonify({'error': 'Insufficient inventory'}), 400
        
        # Reserve inventory
        cur.execute(
            'UPDATE inventory SET reserved = reserved + %s, available = available - %s WHERE product_id = %s',
            (quantity, quantity, product_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        # Invalidate cache
        redis_client.delete(f'inventory:{product_id}')
        
        return jsonify({'message': 'Inventory reserved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/<int:product_id>/release', methods=['POST'])
def release_inventory(product_id):
    try:
        data = request.json
        quantity = data.get('quantity', 0)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            'UPDATE inventory SET reserved = reserved - %s, available = available + %s WHERE product_id = %s',
            (quantity, quantity, product_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        # Invalidate cache
        redis_client.delete(f'inventory:{product_id}')
        
        return jsonify({'message': 'Inventory released successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', '3004'))
    app.run(host='0.0.0.0', port=port)

