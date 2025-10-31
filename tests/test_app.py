import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_portal_selection(client):
    """Test portal selection page loads"""
    rv = client.get('/')
    assert rv.status_code == 302  # Should redirect
    rv = client.get('/portal-selection')
    assert rv.status_code == 200
    assert b'AutoPredict AI' in rv.data

def test_admin_login_page(client):
    """Test admin login page loads"""
    rv = client.get('/admin/login')
    assert rv.status_code == 200
    assert b'Admin Portal - Login' in rv.data

def test_user_login_page(client):
    """Test user login page loads"""
    rv = client.get('/user/login')
    assert rv.status_code == 200
    assert b'User Portal - Login' in rv.data

def test_admin_login_fail(client):
    """Test admin login with incorrect credentials"""
    rv = client.post('/admin/login', data={
        'username': 'bad',
        'password': 'bad'
    })
    assert b'Invalid admin credentials' in rv.data

def test_register_and_user_login(client):
    """Test user registration and login flow"""
    # Register new user
    rv = client.post('/register', data={
        'reg_name': 'Test User',
        'reg_vehicle': 'TEST-123'
    }, follow_redirects=True)
    assert b'Registration successful' in rv.data

    # Login as registered user
    rv2 = client.post('/user/login', data={
        'name': 'Test User',
        'vehicle_no': 'TEST-123'
    }, follow_redirects=True)
    assert b'Dashboard' in rv2.data or b'User Portal' in rv2.data
