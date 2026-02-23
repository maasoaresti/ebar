#!/usr/bin/env python3
"""
EventPay Backend API Test Suite
Comprehensive testing for all EventPay backend APIs
"""

import requests
import json
import sys
import time
from typing import Dict, Optional

# Use the backend URL from frontend environment
BASE_URL = "https://fastcheck-7.preview.emergentagent.com/api"

class EventPayTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_event_id = None
        self.test_product_ids = []
        self.test_order_id = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }

    def log_result(self, test_name: str, success: bool, message: str = ""):
        if success:
            self.results["passed"] += 1
            print(f"✅ {test_name}")
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: {message}")

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    token: Optional[str] = None, params: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request with optional authentication"""
        url = f"{BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error for {method} {endpoint}: {str(e)}")
            raise

    def test_user_registration(self):
        """Test user registration endpoint"""
        print("\n🔵 Testing User Registration...")
        
        # Test registering a new user
        new_user_data = {
            "email": "testuser@eventpay.com",
            "password": "testpass123",
            "name": "Usuário de Teste",
            "phone": "+55 11 97777-7777"
        }
        
        response = self.make_request("POST", "/auth/register", new_user_data)
        
        if response.status_code == 201 or response.status_code == 200:
            self.log_result("User Registration", True)
            return True
        elif response.status_code == 400 and "já cadastrado" in response.text:
            # User already exists, which is fine for testing
            self.log_result("User Registration", True, "User already exists (expected)")
            return True
        else:
            self.log_result("User Registration", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_admin_login(self):
        """Test admin login and store token"""
        print("\n🔵 Testing Admin Login...")
        
        admin_credentials = {
            "email": "admin@eventpay.com",
            "password": "admin123"
        }
        
        response = self.make_request("POST", "/auth/login", admin_credentials)
        
        if response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                self.admin_token = data["token"]
                self.log_result("Admin Login", True)
                return True
            else:
                self.log_result("Admin Login", False, "Missing token or user in response")
                return False
        else:
            self.log_result("Admin Login", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_user_login(self):
        """Test regular user login and store token"""
        print("\n🔵 Testing User Login...")
        
        user_credentials = {
            "email": "user@eventpay.com", 
            "password": "user123"
        }
        
        response = self.make_request("POST", "/auth/login", user_credentials)
        
        if response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                self.user_token = data["token"]
                self.log_result("User Login", True)
                return True
            else:
                self.log_result("User Login", False, "Missing token or user in response")
                return False
        else:
            self.log_result("User Login", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_get_user_profile(self):
        """Test getting user profile with JWT token"""
        print("\n🔵 Testing User Profile...")
        
        if not self.admin_token:
            self.log_result("Get User Profile", False, "No admin token available")
            return False
            
        response = self.make_request("GET", "/auth/me", token=self.admin_token)
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data and "email" in data and "role" in data:
                self.log_result("Get User Profile", True)
                return True
            else:
                self.log_result("Get User Profile", False, "Missing required fields in profile")
                return False
        else:
            self.log_result("Get User Profile", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_create_event(self):
        """Test creating an event (admin only)"""
        print("\n🔵 Testing Create Event...")
        
        if not self.admin_token:
            self.log_result("Create Event", False, "No admin token available")
            return False

        event_data = {
            "name": "Festival de Música 2025",
            "description": "Festival de verão com grandes artistas nacionais e internacionais",
            "date": "2025-06-15",
            "location": "Parque Ibirapuera, São Paulo"
        }
        
        response = self.make_request("POST", "/events", event_data, token=self.admin_token)
        
        if response.status_code in [200, 201]:
            data = response.json()
            if "id" in data:
                self.test_event_id = data["id"]
                self.log_result("Create Event", True)
                return True
            else:
                self.log_result("Create Event", False, "Missing event ID in response")
                return False
        else:
            self.log_result("Create Event", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_get_events(self):
        """Test getting all events"""
        print("\n🔵 Testing Get Events...")
        
        response = self.make_request("GET", "/events")
        
        if response.status_code == 200:
            events = response.json()
            if isinstance(events, list):
                self.log_result("Get Events", True)
                # If we don't have a test event ID yet, try to get one from the list
                if not self.test_event_id and len(events) > 0:
                    self.test_event_id = events[0]["id"]
                return True
            else:
                self.log_result("Get Events", False, "Response is not a list")
                return False
        else:
            self.log_result("Get Events", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_get_events_filtered(self):
        """Test getting filtered events (active status)"""
        print("\n🔵 Testing Get Events (Filtered)...")
        
        response = self.make_request("GET", "/events", params={"status": "active"})
        
        if response.status_code == 200:
            events = response.json()
            if isinstance(events, list):
                self.log_result("Get Events (Filtered)", True)
                return True
            else:
                self.log_result("Get Events (Filtered)", False, "Response is not a list")
                return False
        else:
            self.log_result("Get Events (Filtered)", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_get_event_details(self):
        """Test getting specific event details"""
        print("\n🔵 Testing Get Event Details...")
        
        if not self.test_event_id:
            self.log_result("Get Event Details", False, "No test event ID available")
            return False
        
        response = self.make_request("GET", f"/events/{self.test_event_id}")
        
        if response.status_code == 200:
            event = response.json()
            if "id" in event and "name" in event:
                self.log_result("Get Event Details", True)
                return True
            else:
                self.log_result("Get Event Details", False, "Missing required event fields")
                return False
        else:
            self.log_result("Get Event Details", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_create_products(self):
        """Test creating products for an event (admin only)"""
        print("\n🔵 Testing Create Products...")
        
        if not self.admin_token or not self.test_event_id:
            self.log_result("Create Products", False, "Missing admin token or event ID")
            return False

        products = [
            {"name": "Cerveja Pilsen", "description": "Cerveja gelada 350ml", "price": 8.50, "stock": 100},
            {"name": "Refrigerante", "description": "Coca-Cola 350ml", "price": 5.00, "stock": 50},
            {"name": "Hambúrguer Artesanal", "description": "Hambúrguer com queijo e bacon", "price": 25.00, "stock": 30},
            {"name": "Batata Frita", "description": "Porção de batata frita", "price": 12.00, "stock": 40},
            {"name": "Água Mineral", "description": "Água mineral 500ml", "price": 3.00, "stock": 80}
        ]
        
        success_count = 0
        for product in products:
            response = self.make_request("POST", f"/events/{self.test_event_id}/products", 
                                       product, token=self.admin_token)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if "id" in data:
                    self.test_product_ids.append(data["id"])
                    success_count += 1
        
        if success_count == len(products):
            self.log_result("Create Products", True)
            return True
        else:
            self.log_result("Create Products", False, f"Only {success_count}/{len(products)} products created")
            return False

    def test_get_event_products(self):
        """Test getting products for an event"""
        print("\n🔵 Testing Get Event Products...")
        
        if not self.test_event_id:
            self.log_result("Get Event Products", False, "No test event ID available")
            return False
        
        response = self.make_request("GET", f"/events/{self.test_event_id}/products")
        
        if response.status_code == 200:
            products = response.json()
            if isinstance(products, list):
                self.log_result("Get Event Products", True)
                # Store product IDs if we don't have them
                if not self.test_product_ids and len(products) > 0:
                    self.test_product_ids = [p["id"] for p in products]
                return True
            else:
                self.log_result("Get Event Products", False, "Response is not a list")
                return False
        else:
            self.log_result("Get Event Products", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_create_order(self):
        """Test creating an order"""
        print("\n🔵 Testing Create Order...")
        
        if not self.user_token or not self.test_event_id or not self.test_product_ids:
            self.log_result("Create Order", False, "Missing user token, event ID, or product IDs")
            return False

        # Create order with first two products
        order_data = {
            "event_id": self.test_event_id,
            "items": [
                {
                    "product_id": self.test_product_ids[0],
                    "product_name": "Cerveja Pilsen",
                    "quantity": 2,
                    "unit_price": 8.50
                },
                {
                    "product_id": self.test_product_ids[1] if len(self.test_product_ids) > 1 else self.test_product_ids[0],
                    "product_name": "Refrigerante", 
                    "quantity": 1,
                    "unit_price": 5.00
                }
            ],
            "use_credits": 0.0
        }
        
        response = self.make_request("POST", "/orders", order_data, token=self.user_token)
        
        if response.status_code in [200, 201]:
            data = response.json()
            if "id" in data and "qr_code" in data:
                self.test_order_id = data["id"]
                # Verify 10% platform fee calculation
                expected_subtotal = (8.50 * 2) + (5.00 * 1)  # 22.00
                expected_fee = expected_subtotal * 0.10  # 2.20
                expected_total = expected_subtotal + expected_fee  # 24.20
                
                actual_subtotal = data.get("subtotal", 0)
                actual_fee = data.get("platform_fee", 0)
                actual_total = data.get("total", 0)
                
                if (abs(actual_subtotal - expected_subtotal) < 0.01 and 
                    abs(actual_fee - expected_fee) < 0.01 and 
                    abs(actual_total - expected_total) < 0.01):
                    self.log_result("Create Order", True)
                    return True
                else:
                    self.log_result("Create Order", False, 
                                  f"Fee calculation incorrect. Expected: {expected_total}, Got: {actual_total}")
                    return False
            else:
                self.log_result("Create Order", False, "Missing order ID or QR code in response")
                return False
        else:
            self.log_result("Create Order", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_get_my_orders(self):
        """Test getting user's orders"""
        print("\n🔵 Testing Get My Orders...")
        
        if not self.user_token:
            self.log_result("Get My Orders", False, "No user token available")
            return False
        
        response = self.make_request("GET", "/orders", token=self.user_token)
        
        if response.status_code == 200:
            orders = response.json()
            if isinstance(orders, list):
                self.log_result("Get My Orders", True)
                return True
            else:
                self.log_result("Get My Orders", False, "Response is not a list")
                return False
        else:
            self.log_result("Get My Orders", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_get_order_details(self):
        """Test getting specific order details"""
        print("\n🔵 Testing Get Order Details...")
        
        if not self.user_token or not self.test_order_id:
            self.log_result("Get Order Details", False, "Missing user token or order ID")
            return False
        
        response = self.make_request("GET", f"/orders/{self.test_order_id}", token=self.user_token)
        
        if response.status_code == 200:
            order = response.json()
            if "id" in order and "qr_code" in order:
                self.log_result("Get Order Details", True)
                return True
            else:
                self.log_result("Get Order Details", False, "Missing required order fields")
                return False
        else:
            self.log_result("Get Order Details", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_validate_qr_code(self):
        """Test QR code validation (admin only)"""
        print("\n🔵 Testing QR Code Validation...")
        
        if not self.admin_token or not self.test_order_id:
            self.log_result("QR Code Validation", False, "Missing admin token or order ID")
            return False
        
        # First get the order to retrieve QR code
        response = self.make_request("GET", f"/orders/{self.test_order_id}", token=self.admin_token)
        if response.status_code != 200:
            self.log_result("QR Code Validation", False, "Could not retrieve order for QR code")
            return False
        
        order = response.json()
        qr_code = order.get("qr_code")
        
        if not qr_code:
            self.log_result("QR Code Validation", False, "No QR code found in order")
            return False
        
        # Now validate the QR code
        response = self.make_request("POST", f"/orders/validate-qr?qr_code={qr_code}", token=self.admin_token)
        
        if response.status_code == 200:
            data = response.json()
            if "message" in data and "order" in data:
                self.log_result("QR Code Validation", True)
                return True
            else:
                self.log_result("QR Code Validation", False, "Missing message or order in response")
                return False
        else:
            self.log_result("QR Code Validation", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_credits_balance(self):
        """Test getting credits balance"""
        print("\n🔵 Testing Credits Balance...")
        
        if not self.user_token:
            self.log_result("Credits Balance", False, "No user token available")
            return False
        
        response = self.make_request("GET", "/credits/balance", token=self.user_token)
        
        if response.status_code == 200:
            data = response.json()
            if "credits" in data:
                self.log_result("Credits Balance", True)
                return True
            else:
                self.log_result("Credits Balance", False, "Missing credits field in response")
                return False
        else:
            self.log_result("Credits Balance", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_add_credits(self):
        """Test adding credits"""
        print("\n🔵 Testing Add Credits...")
        
        if not self.user_token:
            self.log_result("Add Credits", False, "No user token available")
            return False
        
        response = self.make_request("POST", "/credits/add?amount=25.0", token=self.user_token)
        
        if response.status_code == 200:
            data = response.json()
            if "message" in data and "new_balance" in data:
                self.log_result("Add Credits", True)
                return True
            else:
                self.log_result("Add Credits", False, "Missing message or new_balance in response")
                return False
        else:
            self.log_result("Add Credits", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_admin_orders(self):
        """Test admin access to all orders"""
        print("\n🔵 Testing Admin Orders...")
        
        if not self.admin_token:
            self.log_result("Admin Orders", False, "No admin token available")
            return False
        
        response = self.make_request("GET", "/admin/orders", token=self.admin_token)
        
        if response.status_code == 200:
            orders = response.json()
            if isinstance(orders, list):
                self.log_result("Admin Orders", True)
                return True
            else:
                self.log_result("Admin Orders", False, "Response is not a list")
                return False
        else:
            self.log_result("Admin Orders", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_admin_reports(self):
        """Test admin reports"""
        print("\n🔵 Testing Admin Reports...")
        
        if not self.admin_token:
            self.log_result("Admin Reports", False, "No admin token available")
            return False
        
        response = self.make_request("GET", "/admin/reports", token=self.admin_token)
        
        if response.status_code == 200:
            data = response.json()
            expected_fields = ["total_orders", "total_sales", "platform_fees", "organizer_amount"]
            if all(field in data for field in expected_fields):
                self.log_result("Admin Reports", True)
                return True
            else:
                self.log_result("Admin Reports", False, "Missing required fields in reports")
                return False
        else:
            self.log_result("Admin Reports", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_unauthorized_access(self):
        """Test that admin endpoints reject regular users"""
        print("\n🔵 Testing Authorization Controls...")
        
        if not self.user_token:
            self.log_result("Authorization Controls", False, "No user token available")
            return False
        
        # Try to access admin endpoint with user token
        response = self.make_request("GET", "/admin/orders", token=self.user_token)
        
        if response.status_code == 403:
            self.log_result("Authorization Controls", True)
            return True
        else:
            self.log_result("Authorization Controls", False, 
                          f"Expected 403, got {response.status_code}")
            return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting EventPay Backend API Tests")
        print(f"Base URL: {BASE_URL}")
        print("=" * 60)
        
        # Authentication tests
        self.test_user_registration()
        self.test_admin_login()
        self.test_user_login()
        self.test_get_user_profile()
        
        # Event tests
        self.test_get_events()
        self.test_get_events_filtered()
        self.test_create_event()
        self.test_get_event_details()
        
        # Product tests
        self.test_create_products()
        self.test_get_event_products()
        
        # Order tests
        self.test_create_order()
        self.test_get_my_orders()
        self.test_get_order_details()
        self.test_validate_qr_code()
        
        # Credits tests
        self.test_credits_balance()
        self.test_add_credits()
        
        # Admin tests
        self.test_admin_orders()
        self.test_admin_reports()
        
        # Security tests
        self.test_unauthorized_access()
        
        # Print final results
        print("\n" + "=" * 60)
        print("🏁 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['errors']:
            print(f"\n🚨 Failed Tests:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100
        print(f"\n📊 Success Rate: {success_rate:.1f}%")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = EventPayTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)