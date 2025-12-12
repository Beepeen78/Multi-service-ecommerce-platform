package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	_ "github.com/lib/pq"
	"github.com/redis/go-redis/v9"
	"github.com/segmentio/kafka-go"
)

type Order struct {
	ID        int       `json:"id"`
	UserID    int       `json:"user_id"`
	Status    string    `json:"status"`
	Total     float64   `json:"total"`
	Items     []OrderItem `json:"items"`
	CreatedAt time.Time `json:"created_at"`
}

type OrderItem struct {
	ProductID int     `json:"product_id"`
	Quantity  int     `json:"quantity"`
	Price     float64 `json:"price"`
}

type OrderService struct {
	db    *sql.DB
	redis *redis.Client
	kafka *kafka.Writer
}

func NewOrderService() (*OrderService, error) {
	dbHost := getEnv("DB_HOST", "postgres")
	dbPort := getEnv("DB_PORT", "5432")
	dbUser := getEnv("DB_USER", "ecommerce")
	dbPassword := getEnv("DB_PASSWORD", "ecommerce123")
	dbName := getEnv("DB_NAME", "ecommerce")

	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		dbHost, dbPort, dbUser, dbPassword, dbName)

	db, err := sql.Open("postgres", dsn)
	if err != nil {
		return nil, err
	}

	if err := db.Ping(); err != nil {
		return nil, err
	}

	rdb := redis.NewClient(&redis.Options{
		Addr: getEnv("REDIS_URL", "redis:6379"),
	})

	kw := &kafka.Writer{
		Addr:     kafka.TCP(getEnv("KAFKA_BROKER", "kafka:9092")),
		Topic:    "orders",
		Balancer: &kafka.LeastBytes{},
	}

	return &OrderService{db: db, redis: rdb, kafka: kw}, nil
}

func (s *OrderService) CreateOrder(w http.ResponseWriter, r *http.Request) {
	var order Order
	if err := json.NewDecoder(r.Body).Decode(&order); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// Create order in database
	var orderID int
	err := s.db.QueryRow(
		"INSERT INTO orders (user_id, status, total, created_at) VALUES ($1, $2, $3, NOW()) RETURNING id",
		order.UserID, "pending", order.Total,
	).Scan(&orderID)

	if err != nil {
		http.Error(w, "Failed to create order", http.StatusInternalServerError)
		return
	}

	// Insert order items
	for _, item := range order.Items {
		_, err = s.db.Exec(
			"INSERT INTO order_items (order_id, product_id, quantity, price) VALUES ($1, $2, $3, $4)",
			orderID, item.ProductID, item.Quantity, item.Price,
		)
		if err != nil {
			log.Printf("Error inserting order item: %v", err)
		}
	}

	order.ID = orderID
	order.Status = "pending"

	// Publish to Kafka
	orderJSON, _ := json.Marshal(order)
	ctx := context.Background()
	s.kafka.WriteMessages(ctx, kafka.Message{
		Key:   []byte(strconv.Itoa(orderID)),
		Value: orderJSON,
	})

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(order)
}

func (s *OrderService) GetOrder(w http.ResponseWriter, r *http.Request) {
	orderID := r.URL.Query().Get("id")
	if orderID == "" {
		http.Error(w, "Order ID required", http.StatusBadRequest)
		return
	}

	id, err := strconv.Atoi(orderID)
	if err != nil {
		http.Error(w, "Invalid order ID", http.StatusBadRequest)
		return
	}

	var order Order
	err = s.db.QueryRow(
		"SELECT id, user_id, status, total, created_at FROM orders WHERE id = $1",
		id,
	).Scan(&order.ID, &order.UserID, &order.Status, &order.Total, &order.CreatedAt)

	if err == sql.ErrNoRows {
		http.Error(w, "Order not found", http.StatusNotFound)
		return
	}
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	// Get order items
	rows, err := s.db.Query(
		"SELECT product_id, quantity, price FROM order_items WHERE order_id = $1",
		id,
	)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	for rows.Next() {
		var item OrderItem
		rows.Scan(&item.ProductID, &item.Quantity, &item.Price)
		order.Items = append(order.Items, item)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(order)
}

func (s *OrderService) HealthCheck(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"status":  "healthy",
		"service": "order-service",
	})
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func main() {
	service, err := NewOrderService()
	if err != nil {
		log.Fatal("Failed to initialize service:", err)
	}
	defer service.db.Close()
	defer service.redis.Close()
	defer service.kafka.Close()

	http.HandleFunc("/health", service.HealthCheck)
	http.HandleFunc("/api/orders", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodPost:
			service.CreateOrder(w, r)
		case http.MethodGet:
			service.GetOrder(w, r)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	port := getEnv("PORT", "3006")
	log.Printf("Order service running on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}


