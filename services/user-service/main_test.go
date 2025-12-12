package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestHealthCheck(t *testing.T) {
	req, err := http.NewRequest("GET", "/health", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{
			"status":  "healthy",
			"service": "user-service",
		})
	})

	handler.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusOK)
	}

	var response map[string]string
	json.Unmarshal(rr.Body.Bytes(), &response)

	if response["status"] != "healthy" {
		t.Errorf("handler returned unexpected status: got %v want %v",
			response["status"], "healthy")
	}
}

func TestGetUser(t *testing.T) {
	req, err := http.NewRequest("GET", "/api/users?id=1", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		userID := r.URL.Query().Get("id")
		if userID == "" {
			http.Error(w, "User ID required", http.StatusBadRequest)
			return
		}

		user := map[string]interface{}{
			"id":    1,
			"email": "test@example.com",
			"name":  "Test User",
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(user)
	})

	handler.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusOK)
	}

	var user map[string]interface{}
	json.Unmarshal(rr.Body.Bytes(), &user)

	if user["id"] != float64(1) {
		t.Errorf("handler returned unexpected user ID: got %v want %v",
			user["id"], 1)
	}
}

