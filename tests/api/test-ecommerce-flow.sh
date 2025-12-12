#!/bin/bash

# E-Commerce Platform API Test Script
# Tests the complete user journey through the platform

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://localhost"
TIMEOUT=5

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to make API calls
api_call() {
    local method=$1
    local url=$2
    local data=$3
    local expected_status=${4:-200}
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -m $TIMEOUT -X $method "$url" 2>/dev/null)
    else
        response=$(curl -s -w "\n%{http_code}" -m $TIMEOUT -X $method "$url" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" == "$expected_status" ]; then
        echo -e "${GREEN}✓${NC} $method $url - Status: $status_code"
        ((TESTS_PASSED++))
        echo "$body" | jq . 2>/dev/null || echo "$body"
        echo "$body"
        return 0
    else
        echo -e "${RED}✗${NC} $method $url - Expected $expected_status, got $status_code"
        echo "$body"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}Warning: jq not found. JSON output will not be formatted.${NC}"
    JQ_AVAILABLE=false
else
    JQ_AVAILABLE=true
fi

echo -e "${GREEN}=== E-Commerce Platform API Test Suite ===${NC}\n"

# 1. Health Checks
echo -e "${YELLOW}1. Testing Health Endpoints${NC}"
api_call GET "$BASE_URL:3001/health" "" 200 > /dev/null
api_call GET "$BASE_URL:3002/health" "" 200 > /dev/null
api_call GET "$BASE_URL:3003/health" "" 200 > /dev/null
api_call GET "$BASE_URL:3004/health" "" 200 > /dev/null
api_call GET "$BASE_URL:3005/health" "" 200 > /dev/null
api_call GET "$BASE_URL:3006/health" "" 200 > /dev/null
api_call GET "$BASE_URL:3007/health" "" 200 > /dev/null
api_call GET "$BASE_URL:3008/health" "" 200 > /dev/null
api_call GET "$BASE_URL:3009/health" "" 200 > /dev/null

# 2. Register User
echo -e "\n${YELLOW}2. Registering New User${NC}"
REGISTER_DATA='{"email":"testuser'$(date +%s)'@example.com","password":"password123","name":"Test User"}'
REGISTER_RESPONSE=$(api_call POST "$BASE_URL:3001/api/auth/register" "$REGISTER_DATA" 201)

if [ $JQ_AVAILABLE = true ]; then
    USER_ID=$(echo "$REGISTER_RESPONSE" | jq -r '.user.id // empty')
    TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.token // empty')
else
    USER_ID=$(echo "$REGISTER_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    TOKEN=$(echo "$REGISTER_RESPONSE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
fi

if [ -z "$USER_ID" ] || [ -z "$TOKEN" ]; then
    echo -e "${RED}Failed to extract user ID or token from registration response${NC}"
    exit 1
fi

echo "User ID: $USER_ID"
echo "Token: ${TOKEN:0:20}..."

# 3. Login
echo -e "\n${YELLOW}3. Testing Login${NC}"
LOGIN_EMAIL=$(echo "$REGISTER_DATA" | jq -r '.email' 2>/dev/null || echo "testuser@example.com")
LOGIN_DATA="{\"email\":\"$LOGIN_EMAIL\",\"password\":\"password123\"}"
api_call POST "$BASE_URL:3001/api/auth/login" "$LOGIN_DATA" 200 > /dev/null

# 4. Verify Token
echo -e "\n${YELLOW}4. Verifying Token${NC}"
api_call POST "$BASE_URL:3001/api/auth/verify" "" 401 > /dev/null  # Without token should fail
# Note: Add token to header if auth middleware is implemented

# 5. Get Products
echo -e "\n${YELLOW}5. Fetching Products${NC}"
PRODUCTS_RESPONSE=$(api_call GET "$BASE_URL:3003/api/products" "" 200)

# 6. Get Single Product (if products exist)
if [ $JQ_AVAILABLE = true ]; then
    FIRST_PRODUCT_ID=$(echo "$PRODUCTS_RESPONSE" | jq -r '.[0].id // empty' 2>/dev/null)
    if [ ! -z "$FIRST_PRODUCT_ID" ] && [ "$FIRST_PRODUCT_ID" != "null" ]; then
        echo -e "\n${YELLOW}6. Fetching Single Product${NC}"
        api_call GET "$BASE_URL:3003/api/products/$FIRST_PRODUCT_ID" "" 200 > /dev/null
    fi
fi

# 7. Add to Cart
echo -e "\n${YELLOW}7. Adding Item to Cart${NC}"
CART_DATA='{"productId":1,"quantity":2,"price":29.99}'
api_call POST "$BASE_URL:3005/api/cart/$USER_ID/items" "$CART_DATA" 200 > /dev/null

# 8. Get Cart
echo -e "\n${YELLOW}8. Retrieving Cart${NC}"
api_call GET "$BASE_URL:3005/api/cart/$USER_ID" "" 200 > /dev/null

# 9. Create Order
echo -e "\n${YELLOW}9. Creating Order${NC}"
ORDER_DATA="{\"userId\":$USER_ID,\"total\":59.98,\"items\":[{\"productId\":1,\"quantity\":2,\"price\":29.99}]}"
ORDER_RESPONSE=$(api_call POST "$BASE_URL:3006/api/orders" "$ORDER_DATA" 201)

if [ $JQ_AVAILABLE = true ]; then
    ORDER_ID=$(echo "$ORDER_RESPONSE" | jq -r '.id // empty' 2>/dev/null)
else
    ORDER_ID=$(echo "$ORDER_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
fi

if [ ! -z "$ORDER_ID" ] && [ "$ORDER_ID" != "null" ]; then
    echo "Order ID: $ORDER_ID"
    
    # 10. Get Order
    echo -e "\n${YELLOW}10. Retrieving Order${NC}"
    api_call GET "$BASE_URL:3006/api/orders?id=$ORDER_ID" "" 200 > /dev/null
    
    # 11. Process Payment
    echo -e "\n${YELLOW}11. Processing Payment${NC}"
    PAYMENT_DATA="{\"orderId\":$ORDER_ID,\"amount\":59.98,\"paymentMethod\":\"credit_card\",\"cardToken\":\"tok_test123\"}"
    api_call POST "$BASE_URL:3007/api/payments" "$PAYMENT_DATA" 201 > /dev/null
    
    # 12. Get Payment Status
    echo -e "\n${YELLOW}12. Checking Payment Status${NC}"
    api_call GET "$BASE_URL:3007/api/payments/$ORDER_ID" "" 200 > /dev/null
fi

# 13. Wait for Kafka and check notifications
echo -e "\n${YELLOW}13. Checking Notifications${NC}"
sleep 3  # Wait for Kafka consumer to process
api_call GET "$BASE_URL:3008/api/notifications/$USER_ID" "" 200 > /dev/null

# 14. Get Recommendations
echo -e "\n${YELLOW}14. Getting Recommendations${NC}"
api_call GET "$BASE_URL:3009/api/recommendations/$USER_ID" "" 200 > /dev/null

# 15. Test Inventory
echo -e "\n${YELLOW}15. Testing Inventory Service${NC}"
if [ ! -z "$FIRST_PRODUCT_ID" ] && [ "$FIRST_PRODUCT_ID" != "null" ]; then
    api_call GET "$BASE_URL:3004/api/inventory/$FIRST_PRODUCT_ID" "" 200 > /dev/null
fi

# Summary
echo -e "\n${GREEN}=== Test Summary ===${NC}"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
TOTAL=$((TESTS_PASSED + TESTS_FAILED))
if [ $TOTAL -gt 0 ]; then
    SUCCESS_RATE=$((TESTS_PASSED * 100 / TOTAL))
    echo -e "Success Rate: ${SUCCESS_RATE}%"
fi

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed! ✗${NC}"
    exit 1
fi

