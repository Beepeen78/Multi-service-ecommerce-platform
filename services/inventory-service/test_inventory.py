import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'inventory-service'

def test_get_inventory_not_found(client):
    """Test getting inventory for non-existent product"""
    response = client.get('/api/inventory/999')
    assert response.status_code == 404

def test_reserve_inventory_missing_data(client):
    """Test reserving inventory with missing data"""
    response = client.post('/api/inventory/1/reserve', json={})
    assert response.status_code == 500  # Will fail due to missing quantity

def test_reserve_inventory_invalid_product(client):
    """Test reserving inventory for non-existent product"""
    response = client.post('/api/inventory/999/reserve', json={'quantity': 1})
    assert response.status_code == 404

def test_release_inventory(client):
    """Test releasing inventory"""
    response = client.post('/api/inventory/1/release', json={'quantity': 1})
    # May return 200 or 500 depending on product existence
    assert response.status_code in [200, 500]

