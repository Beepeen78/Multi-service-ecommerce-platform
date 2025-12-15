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
)

type User struct {
	ID        int       `json:"id"`
	Email     string    `json:"email"`
	Name      string    `json:"name"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

type UserService struct {
	db    *sql.DB
	redis *redis.Client
}

func NewUserService() (*UserService, error) {
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

	return &UserService{db: db, redis: rdb}, nil
}

func (s *UserService) GetUser(w http.ResponseWriter, r *http.Request) {
	userID := r.URL.Query().Get("id")
	if userID == "" {
		http.Error(w, "User ID required", http.StatusBadRequest)
		return
	}

	id, err := strconv.Atoi(userID)
	if err != nil {
		http.Error(w, "Invalid user ID", http.StatusBadRequest)
		return
	}

	// Check cache first
	ctx := context.Background()
	cached, err := s.redis.Get(ctx, fmt.Sprintf("user:%d", id)).Result()
	if err == nil {
		w.Header().Set("Content-Type", "application/json")
		w.Write([]byte(cached))
		return
	}

	// Query database
	var user User
	err = s.db.QueryRow(
		"SELECT id, email, name, created_at, updated_at FROM users WHERE id = $1",
		id,
	).Scan(&user.ID, &user.Email, &user.Name, &user.CreatedAt, &user.UpdatedAt)

	if err == sql.ErrNoRows {
		http.Error(w, "User not found", http.StatusNotFound)
		return
	}
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	// Cache result
	userJSON, _ := json.Marshal(user)
	s.redis.Set(ctx, fmt.Sprintf("user:%d", id), userJSON, time.Hour)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(user)
}

func (s *UserService) UpdateUser(w http.ResponseWriter, r *http.Request) {
	var user User
	if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	userID := r.URL.Query().Get("id")
	if userID == "" {
		http.Error(w, "User ID required", http.StatusBadRequest)
		return
	}

	id, err := strconv.Atoi(userID)
	if err != nil {
		http.Error(w, "Invalid user ID", http.StatusBadRequest)
		return
	}

	_, err = s.db.Exec(
		"UPDATE users SET name = $1, updated_at = NOW() WHERE id = $2",
		user.Name, id,
	)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	// Invalidate cache
	ctx := context.Background()
	s.redis.Del(ctx, fmt.Sprintf("user:%d", id))

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"message": "User updated"})
}

func (s *UserService) HealthCheck(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"status":  "healthy",
		"service": "user-service",
	})
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func main() {
	service, err := NewUserService()
	if err != nil {
		log.Fatal("Failed to initialize service:", err)
	}
	defer service.db.Close()
	defer service.redis.Close()

	http.HandleFunc("/health", service.HealthCheck)
	http.HandleFunc("/api/users", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			service.GetUser(w, r)
		case http.MethodPut:
			service.UpdateUser(w, r)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	port := getEnv("PORT", "3002")
	log.Printf("User service running on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}

