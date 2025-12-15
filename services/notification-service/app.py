from flask import Flask, request, jsonify
import psycopg2
import redis
import os
import json
from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime
import threading

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

# Kafka producer
kafka_producer = KafkaProducer(
    bootstrap_servers=os.getenv('KAFKA_BROKER', 'kafka:9092'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def consume_orders():
    """Consume order events from Kafka and send notifications"""
    consumer = KafkaConsumer(
        'orders',
        bootstrap_servers=os.getenv('KAFKA_BROKER', 'kafka:9092'),
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id='notification-service'
    )
    
    for message in consumer:
        order = message.value
        send_order_notification(order)

def send_order_notification(order):
    """Send notification for order"""
    notification = {
        'type': 'order_created',
        'user_id': order.get('user_id'),
        'order_id': order.get('id'),
        'message': f'Your order #{order.get("id")} has been created',
        'created_at': datetime.now().isoformat()
    }
    
    # Store in database
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO notifications (user_id, type, message, created_at) VALUES (%s, %s, %s, NOW())',
        (notification['user_id'], notification['type'], notification['message'])
    )
    conn.commit()
    cur.close()
    conn.close()
    
    # Cache notification
    redis_client.lpush(f'notifications:{notification["user_id"]}', json.dumps(notification))
    redis_client.ltrim(f'notifications:{notification["user_id"]}', 0, 99)  # Keep last 100

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'notification-service'})

@app.route('/api/notifications/<int:user_id>', methods=['GET'])
def get_notifications(user_id):
    try:
        # Check cache first
        cached = redis_client.lrange(f'notifications:{user_id}', 0, 19)
        if cached:
            notifications = [json.loads(n) for n in cached]
            return jsonify({'notifications': notifications})
        
        # Query database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'SELECT id, type, message, created_at FROM notifications WHERE user_id = %s ORDER BY created_at DESC LIMIT 20',
            (user_id,)
        )
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        notifications = [
            {
                'id': r[0],
                'type': r[1],
                'message': r[2],
                'created_at': r[3].isoformat()
            }
            for r in results
        ]
        
        return jsonify({'notifications': notifications})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications', methods=['POST'])
def send_notification():
    try:
        data = request.json
        user_id = data.get('user_id')
        notification_type = data.get('type')
        message = data.get('message')
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO notifications (user_id, type, message, created_at) VALUES (%s, %s, %s, NOW()) RETURNING id',
            (user_id, notification_type, message)
        )
        notification_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        notification = {
            'id': notification_id,
            'user_id': user_id,
            'type': notification_type,
            'message': message,
            'created_at': datetime.now().isoformat()
        }
        
        # Cache notification
        redis_client.lpush(f'notifications:{user_id}', json.dumps(notification))
        
        return jsonify(notification), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Start Kafka consumer in background thread
if __name__ == '__main__':
    consumer_thread = threading.Thread(target=consume_orders, daemon=True)
    consumer_thread.start()
    
    port = int(os.getenv('PORT', '3008'))
    app.run(host='0.0.0.0', port=port)

