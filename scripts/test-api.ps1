# PowerShell script to test the E-Commerce Platform APIs
# Usage: .\scripts\test-api.ps1

$baseUrl = "http://localhost:8080"
$token = $null

function Write-TestResult {
    param($TestName, $Success, $Message = "")
    $color = if ($Success) { "Green" } else { "Red" }
    $status = if ($Success) { "✓ PASS" } else { "✗ FAIL" }
    Write-Host "[$status] $TestName" -ForegroundColor $color
    if ($Message) {
        Write-Host "  $Message" -ForegroundColor $color
    }
}

Write-Host "=== E-Commerce Platform API Tests ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: API Gateway Health
Write-Host "1. Testing API Gateway Health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/health" -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    Write-TestResult "API Gateway Health" ($result.status -eq "ok")
} catch {
    Write-TestResult "API Gateway Health" $false $_.Exception.Message
}

# Test 2: Register User
Write-Host "`n2. Testing User Registration..." -ForegroundColor Yellow
try {
    $body = @{
        email = "test$(Get-Random)@example.com"
        password = "test123"
        name = "Test User"
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "$baseUrl/api/users/register" `
        -Method POST `
        -Body $body `
        -ContentType "application/json" `
        -UseBasicParsing
    
    $result = $response.Content | ConvertFrom-Json
    $token = $result.token
    Write-TestResult "User Registration" ($result.message -like "*successfully*") "Token: $($token.Substring(0, 20))..."
} catch {
    Write-TestResult "User Registration" $false $_.Exception.Message
}

# Test 3: Login
Write-Host "`n3. Testing User Login..." -ForegroundColor Yellow
if ($token) {
    try {
        $body = @{
            email = "test@example.com"
            password = "test123"
        } | ConvertTo-Json

        $response = Invoke-WebRequest -Uri "$baseUrl/api/users/login" `
            -Method POST `
            -Body $body `
            -ContentType "application/json" `
            -UseBasicParsing -ErrorAction SilentlyContinue
        
        if ($response) {
            $result = $response.Content | ConvertFrom-Json
            Write-TestResult "User Login" ($result.message -like "*successful*")
        } else {
            Write-TestResult "User Login" $false "User may not exist, skipping..."
        }
    } catch {
        Write-TestResult "User Login" $false "Expected if user doesn't exist"
    }
}

# Test 4: Get Products (Empty)
Write-Host "`n4. Testing Get Products..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/products" -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    Write-TestResult "Get Products" ($result.products -ne $null) "Found $($result.products.Count) products"
} catch {
    Write-TestResult "Get Products" $false $_.Exception.Message
}

# Test 5: Create Product
Write-Host "`n5. Testing Create Product..." -ForegroundColor Yellow
try {
    $body = @{
        name = "Test Product"
        description = "A test product"
        price = 99.99
        category = "test"
        stock_quantity = 10
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "$baseUrl/api/products" `
        -Method POST `
        -Body $body `
        -ContentType "application/json" `
        -UseBasicParsing
    
    $result = $response.Content | ConvertFrom-Json
    $productId = $result.product.id
    Write-TestResult "Create Product" ($result.message -like "*successfully*") "Product ID: $productId"
} catch {
    Write-TestResult "Create Product" $false $_.Exception.Message
}

# Test 6: Get Product by ID
Write-Host "`n6. Testing Get Product by ID..." -ForegroundColor Yellow
if ($productId) {
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl/api/products/$productId" -UseBasicParsing
        $result = $response.Content | ConvertFrom-Json
        Write-TestResult "Get Product by ID" ($result.product.id -eq $productId)
    } catch {
        Write-TestResult "Get Product by ID" $false $_.Exception.Message
    }
}

# Test 7: Create Order (if we have token)
Write-Host "`n7. Testing Create Order..." -ForegroundColor Yellow
if ($token -and $productId) {
    try {
        $body = @{
            items = @(
                @{
                    product_id = $productId
                    quantity = 1
                }
            )
            shipping_address = "123 Test Street"
        } | ConvertTo-Json

        $response = Invoke-WebRequest -Uri "$baseUrl/api/orders" `
            -Method POST `
            -Body $body `
            -ContentType "application/json" `
            -Headers @{Authorization = "Bearer $token"} `
            -UseBasicParsing
        
        $result = $response.Content | ConvertFrom-Json
        $orderId = $result.order.id
        Write-TestResult "Create Order" ($result.message -like "*successfully*") "Order ID: $orderId"
    } catch {
        Write-TestResult "Create Order" $false $_.Exception.Message
    }
} else {
    Write-TestResult "Create Order" $false "Skipped (no token or product)"
}

# Test 8: Order Service Health
Write-Host "`n8. Testing Order Service Health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/orders/health" -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    Write-TestResult "Order Service Health" ($result.status -eq "ok")
} catch {
    Write-TestResult "Order Service Health" $false $_.Exception.Message
}

Write-Host "`n=== Tests Complete ===" -ForegroundColor Cyan

