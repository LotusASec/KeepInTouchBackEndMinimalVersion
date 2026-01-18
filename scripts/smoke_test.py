"""
Smoke Test Script for Animal Tracking API
Tests all CRUD operations and verifies data changes
"""
import requests
import json
import sys
from typing import Optional, Dict, Any

BASE_URL = "http://localhost:8000"

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.admin_token = None
        self.regular_token = None
        self.test_results = []
        
    def log(self, message: str, color: str = RESET):
        print(f"{color}{message}{RESET}")
    
    def test(self, name: str, func):
        """Run a test and track results"""
        self.log(f"\n▶ Testing: {name}", BLUE)
        try:
            func()
            self.log(f"✓ PASSED: {name}", GREEN)
            self.test_results.append((name, True, None))
            return True
        except AssertionError as e:
            self.log(f"✗ FAILED: {name}", RED)
            self.log(f"  Error: {str(e)}", RED)
            self.test_results.append((name, False, str(e)))
            return False
        except Exception as e:
            self.log(f"✗ ERROR: {name}", RED)
            self.log(f"  Exception: {str(e)}", RED)
            self.test_results.append((name, False, str(e)))
            return False
    
    def assert_equal(self, actual, expected, message=""):
        """Custom assertion with detailed message"""
        if actual != expected:
            raise AssertionError(f"{message}\n  Expected: {expected}\n  Got: {actual}")
    
    def assert_in(self, item, container, message=""):
        """Assert item is in container"""
        if item not in container:
            raise AssertionError(f"{message}\n  '{item}' not found in {container}")
    
    # ========== Authentication Tests ==========
    
    def test_admin_login(self):
        """Test admin user login"""
        response = requests.post(
            f"{self.base_url}/users/token",
            data={"username": "admin", "password": "admin123"}
        )
        self.assert_equal(response.status_code, 200, "Admin login failed")
        data = response.json()
        self.assert_in("access_token", data, "No access token in response")
        self.admin_token = data["access_token"]
        self.log(f"  Admin token received: {self.admin_token[:20]}...")
    
    def test_regular_user_login(self):
        """Test regular user login"""
        response = requests.post(
            f"{self.base_url}/users/token",
            data={"username": "operator1", "password": "operator123"}
        )
        self.assert_equal(response.status_code, 200, "Regular user login failed")
        data = response.json()
        self.assert_in("access_token", data, "No access token in response")
        self.regular_token = data["access_token"]
        self.log(f"  Regular user token received: {self.regular_token[:20]}...")
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        response = requests.post(
            f"{self.base_url}/users/token",
            data={"username": "admin", "password": "wrong_password"}
        )
        self.assert_equal(response.status_code, 401, "Should reject invalid credentials")
        self.log("  Invalid login correctly rejected")
    
    # ========== User CRUD Tests ==========
    
    def test_create_user(self):
        """Test creating a new user (admin only)"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        new_user = {
            "name": "testuser",
            "password": "testpass123",
            "role": "regular"
        }
        
        # Create user
        response = requests.post(
            f"{self.base_url}/users/register",
            json=new_user,
            headers=headers
        )
        self.assert_equal(response.status_code, 201, "User creation failed")
        data = response.json()
        self.assert_equal(data["name"], "testuser", "Username mismatch")
        self.assert_equal(data["role"], "regular", "Role mismatch")
        user_id = data["id"]
        self.log(f"  Created user with ID: {user_id}")
        
        # Verify user exists by reading
        response = requests.get(
            f"{self.base_url}/users/{user_id}",
            headers=headers
        )
        self.assert_equal(response.status_code, 200, "Failed to read created user")
        data = response.json()
        self.assert_equal(data["name"], "testuser", "User verification failed")
        self.log(f"  ✓ Verified user exists in database")
    
    def test_read_users(self):
        """Test reading all users (admin only)"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(
            f"{self.base_url}/users/",
            headers=headers
        )
        self.assert_equal(response.status_code, 200, "Failed to read users")
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) >= 3, "Should have at least 3 users (admin, operator1, testuser)"
        self.log(f"  Found {len(data)} users")
    
    def test_update_user(self):
        """Test updating user information"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # First, get the testuser ID
        response = requests.get(f"{self.base_url}/users/", headers=headers)
        users = response.json()
        testuser = next((u for u in users if u["name"] == "testuser"), None)
        assert testuser is not None, "testuser not found"
        user_id = testuser["id"]
        
        # Update user
        update_data = {"role": "admin"}
        response = requests.put(
            f"{self.base_url}/users/{user_id}",
            json=update_data,
            headers=headers
        )
        self.assert_equal(response.status_code, 200, "User update failed")
        
        # Verify update
        response = requests.get(
            f"{self.base_url}/users/{user_id}",
            headers=headers
        )
        data = response.json()
        self.assert_equal(data["role"], "admin", "Role was not updated")
        self.log(f"  ✓ Verified user role updated to 'admin'")
    
    def test_delete_user(self):
        """Test deleting a user"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get testuser ID
        response = requests.get(f"{self.base_url}/users/", headers=headers)
        users = response.json()
        testuser = next((u for u in users if u["name"] == "testuser"), None)
        assert testuser is not None, "testuser not found"
        user_id = testuser["id"]
        
        # Delete user
        response = requests.delete(
            f"{self.base_url}/users/{user_id}",
            headers=headers
        )
        self.assert_equal(response.status_code, 204, "User deletion failed")
        
        # Verify deletion
        response = requests.get(
            f"{self.base_url}/users/{user_id}",
            headers=headers
        )
        self.assert_equal(response.status_code, 404, "Deleted user still exists")
        self.log(f"  ✓ Verified user deleted from database")
    
    def test_regular_user_cannot_create_user(self):
        """Test that regular users cannot create users"""
        headers = {"Authorization": f"Bearer {self.regular_token}"}
        new_user = {
            "name": "unauthorized",
            "password": "test123",
            "role": "regular"
        }
        response = requests.post(
            f"{self.base_url}/users/register",
            json=new_user,
            headers=headers
        )
        self.assert_equal(response.status_code, 403, "Regular user should not create users")
        self.log("  Regular user correctly denied")
    
    # ========== Animal CRUD Tests ==========
    
    def test_create_animal(self):
        """Test creating a new animal"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get admin user ID
        response = requests.get(f"{self.base_url}/users/", headers=headers)
        users = response.json()
        admin = next(u for u in users if u["role"] == "admin")
        
        new_animal = {
            "name": "TestKedi",
            "responsible_user_id": admin["id"],
            "owner_name": "Test Sahibi",
            "owner_contact_number": "+90 555 111 2233",
            "owner_contact_email": "test@example.com",
            "form_generation_period": 30
        }
        
        # Create animal
        response = requests.post(
            f"{self.base_url}/animals/",
            json=new_animal,
            headers=headers
        )
        self.assert_equal(response.status_code, 201, "Animal creation failed")
        data = response.json()
        self.assert_equal(data["name"], "TestKedi", "Animal name mismatch")
        self.assert_equal(data["is_controlled"], False, "Default is_controlled should be False")
        animal_id = data["id"]
        self.log(f"  Created animal with ID: {animal_id}")
        
        # Verify animal exists
        response = requests.get(
            f"{self.base_url}/animals/{animal_id}",
            headers=headers
        )
        self.assert_equal(response.status_code, 200, "Failed to read created animal")
        data = response.json()
        self.assert_equal(data["name"], "TestKedi", "Animal verification failed")
        self.log(f"  ✓ Verified animal exists in database")
    
    def test_read_animals(self):
        """Test reading all animals"""
        headers = {"Authorization": f"Bearer {self.regular_token}"}
        response = requests.get(
            f"{self.base_url}/animals/",
            headers=headers
        )
        self.assert_equal(response.status_code, 200, "Failed to read animals")
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) >= 3, "Should have at least 3 animals"
        self.log(f"  Found {len(data)} animals")
    
    def test_update_animal(self):
        """Test updating animal information"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get TestKedi
        response = requests.get(f"{self.base_url}/animals/", headers=headers)
        animals = response.json()
        test_animal = next((a for a in animals if a["name"] == "TestKedi"), None)
        assert test_animal is not None, "TestKedi not found"
        animal_id = test_animal["id"]
        
        # Update animal
        update_data = {
            "is_controlled": True,
            "is_sent": True,
            "owner_name": "Updated Sahibi"
        }
        response = requests.put(
            f"{self.base_url}/animals/{animal_id}",
            json=update_data,
            headers=headers
        )
        self.assert_equal(response.status_code, 200, "Animal update failed")
        
        # Verify update
        response = requests.get(
            f"{self.base_url}/animals/{animal_id}",
            headers=headers
        )
        data = response.json()
        self.assert_equal(data["is_controlled"], True, "is_controlled not updated")
        self.assert_equal(data["is_sent"], True, "is_sent not updated")
        self.assert_equal(data["owner_name"], "Updated Sahibi", "owner_name not updated")
        self.log(f"  ✓ Verified animal fields updated")
    
    def test_create_form_for_animal(self):
        """Test creating a form for an animal"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get TestKedi
        response = requests.get(f"{self.base_url}/animals/", headers=headers)
        animals = response.json()
        test_animal = next((a for a in animals if a["name"] == "TestKedi"), None)
        animal_id = test_animal["id"]
        
        # Create form
        response = requests.post(
            f"{self.base_url}/animals/{animal_id}/create-form",
            headers=headers
        )
        self.assert_equal(response.status_code, 200, "Form creation failed")
        data = response.json()
        self.assert_equal(data["animal_id"], animal_id, "Form animal_id mismatch")
        form_id = data["id"]
        self.log(f"  Created form with ID: {form_id}")
        
        # Verify animal's form_ids updated
        response = requests.get(
            f"{self.base_url}/animals/{animal_id}",
            headers=headers
        )
        animal = response.json()
        self.assert_in(form_id, animal["form_ids"], "Form ID not in animal's form_ids")
        self.log(f"  ✓ Verified form added to animal's form_ids list")
    
    # ========== Form CRUD Tests ==========
    
    def test_create_form(self):
        """Test creating a form directly"""
        headers = {"Authorization": f"Bearer {self.regular_token}"}
        
        # Get an animal
        response = requests.get(f"{self.base_url}/animals/", headers=headers)
        animals = response.json()
        animal_id = animals[0]["id"]
        
        # Create form
        response = requests.post(
            f"{self.base_url}/forms/",
            json={"animal_id": animal_id},
            headers=headers
        )
        self.assert_equal(response.status_code, 201, "Form creation failed")
        data = response.json()
        self.assert_equal(data["is_sent"], False, "Default is_sent should be False")
        form_id = data["id"]
        self.log(f"  Created form with ID: {form_id}")
        
        # Verify form exists
        response = requests.get(
            f"{self.base_url}/forms/{form_id}",
            headers=headers
        )
        self.assert_equal(response.status_code, 200, "Failed to read created form")
        self.log(f"  ✓ Verified form exists in database")
    
    def test_read_forms_by_animal(self):
        """Test reading forms by animal ID"""
        headers = {"Authorization": f"Bearer {self.regular_token}"}
        
        # Get TestKedi
        response = requests.get(f"{self.base_url}/animals/", headers=headers)
        animals = response.json()
        test_animal = next((a for a in animals if a["name"] == "TestKedi"), None)
        animal_id = test_animal["id"]
        
        # Get forms for animal
        response = requests.get(
            f"{self.base_url}/forms/animal/{animal_id}",
            headers=headers
        )
        self.assert_equal(response.status_code, 200, "Failed to read animal's forms")
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) > 0, "Animal should have at least one form"
        self.log(f"  Found {len(data)} forms for animal")
    
    def test_read_forms_by_ids(self):
        """Test reading multiple forms by IDs"""
        headers = {"Authorization": f"Bearer {self.regular_token}"}
        
        # Get all animals and collect some form IDs
        response = requests.get(f"{self.base_url}/animals/", headers=headers)
        animals = response.json()
        form_ids = []
        for animal in animals[:2]:  # Take first 2 animals
            if animal["form_ids"]:
                form_ids.extend(animal["form_ids"][:1])  # Take 1 form from each
        
        # Get forms by IDs
        response = requests.post(
            f"{self.base_url}/forms/by-ids",
            json=form_ids,
            headers=headers
        )
        self.assert_equal(response.status_code, 200, "Failed to read forms by IDs")
        data = response.json()
        self.assert_equal(len(data), len(form_ids), "Form count mismatch")
        self.log(f"  Retrieved {len(data)} forms by IDs")

    def test_generate_periodic_forms(self):
        """Test periodic form generation creates a form for an animal"""
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

        # Get admin user id
        response = requests.get(f"{self.base_url}/users/", headers=admin_headers)
        users = response.json()
        admin_user = next(u for u in users if u["role"] == "admin")

        new_animal = {
            "name": "PeriodicKediSmoke",
            "responsible_user_id": admin_user["id"],
            "owner_name": "Periodic Sahibi",
            "owner_contact_number": "+90 555 000 0000",
            "owner_contact_email": "periodic@example.com",
            "form_generation_period": 1
        }

        # Create animal dedicated for periodic test
        response = requests.post(
            f"{self.base_url}/animals/",
            json=new_animal,
            headers=admin_headers
        )
        self.assert_equal(response.status_code, 201, "Periodic animal creation failed")
        animal_id = response.json()["id"]

        try:
            # Trigger periodic generation
            response = requests.post(
                f"{self.base_url}/forms/generate-periodic",
                headers=admin_headers
            )
            self.assert_equal(response.status_code, 200, "Periodic form generation failed")

            # Verify a new form exists for this animal
            response = requests.get(
                f"{self.base_url}/forms/animal/{animal_id}",
                headers=admin_headers
            )
            self.assert_equal(response.status_code, 200, "Failed to read periodic forms for animal")
            forms = response.json()
            assert len(forms) >= 1, "Periodic generation should create at least one form"
            form_id = forms[0]["id"]

            # Verify animal's form_ids updated
            response = requests.get(
                f"{self.base_url}/animals/{animal_id}",
                headers=admin_headers
            )
            animal = response.json()
            self.assert_in(form_id, animal["form_ids"], "Generated form ID not in animal.form_ids")
            self.log(f"  ✓ Periodic generation created form {form_id} for animal {animal_id}")
        finally:
            # Cleanup the test animal to avoid polluting dataset
            requests.delete(
                f"{self.base_url}/animals/{animal_id}",
                headers=admin_headers
            )
    
    def test_update_form(self):
        """Test updating form information"""
        headers = {"Authorization": f"Bearer {self.regular_token}"}
        
        # Get a form
        response = requests.get(f"{self.base_url}/animals/", headers=headers)
        animals = response.json()
        test_animal = next((a for a in animals if a["name"] == "TestKedi"), None)
        animal_id = test_animal["id"]
        
        response = requests.get(
            f"{self.base_url}/forms/animal/{animal_id}",
            headers=headers
        )
        forms = response.json()
        form_id = forms[0]["id"]
        
        # Update form
        update_data = {
            "is_sent": True,
            "is_controlled": True,
            "need_review": True
        }
        response = requests.put(
            f"{self.base_url}/forms/{form_id}",
            json=update_data,
            headers=headers
        )
        self.assert_equal(response.status_code, 200, "Form update failed")
        
        # Verify update
        response = requests.get(
            f"{self.base_url}/forms/{form_id}",
            headers=headers
        )
        data = response.json()
        self.assert_equal(data["is_sent"], True, "is_sent not updated")
        self.assert_equal(data["is_controlled"], True, "is_controlled not updated")
        self.assert_equal(data["need_review"], True, "need_review not updated")
        assert data["send_date"] is not None, "send_date should be set when sent"
        assert data["control_due_date"] is not None, "control_due_date should be set when sent"
        assert data["controlled_date"] is not None, "controlled_date should be set when controlled"
        self.log(f"  ✓ Verified form fields updated")

        # Verify animal status reflects latest form
        response = requests.get(
            f"{self.base_url}/animals/{animal_id}",
            headers=headers
        )
        animal = response.json()
        self.assert_equal(animal["is_sent"], True, "Animal is_sent not synced from form")
        self.assert_equal(animal["is_controlled"], True, "Animal is_controlled not synced from form")
        self.assert_equal(animal["need_review"], True, "Animal need_review not synced from form")
        assert animal["last_form_sent_date"] is not None, "Animal last_form_sent_date should be set"
        self.log(f"  ✓ Verified animal status synced from latest form")
    
    def test_delete_form(self):
        """Test deleting a form"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get TestKedi and its forms
        response = requests.get(f"{self.base_url}/animals/", headers=headers)
        animals = response.json()
        test_animal = next((a for a in animals if a["name"] == "TestKedi"), None)
        animal_id = test_animal["id"]
        
        response = requests.get(
            f"{self.base_url}/forms/animal/{animal_id}",
            headers=headers
        )
        forms = response.json()
        form_id = forms[0]["id"]
        
        # Delete form
        response = requests.delete(
            f"{self.base_url}/forms/{form_id}",
            headers=headers
        )
        self.assert_equal(response.status_code, 204, "Form deletion failed")
        
        # Verify deletion
        response = requests.get(
            f"{self.base_url}/forms/{form_id}",
            headers=headers
        )
        self.assert_equal(response.status_code, 404, "Deleted form still exists")
        
        # Verify form removed from animal's form_ids
        response = requests.get(
            f"{self.base_url}/animals/{animal_id}",
            headers=headers
        )
        animal = response.json()
        assert form_id not in animal["form_ids"], "Form ID still in animal's form_ids"
        self.log(f"  ✓ Verified form deleted and removed from animal")
    
    def test_delete_animal(self):
        """Test deleting an animal (should cascade delete forms)"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get TestKedi
        response = requests.get(f"{self.base_url}/animals/", headers=headers)
        animals = response.json()
        test_animal = next((a for a in animals if a["name"] == "TestKedi"), None)
        animal_id = test_animal["id"]
        
        # Get form IDs before deletion
        response = requests.get(
            f"{self.base_url}/forms/animal/{animal_id}",
            headers=headers
        )
        forms = response.json()
        form_ids = [f["id"] for f in forms]
        self.log(f"  Animal has {len(form_ids)} forms before deletion")
        
        # Delete animal
        response = requests.delete(
            f"{self.base_url}/animals/{animal_id}",
            headers=headers
        )
        self.assert_equal(response.status_code, 204, "Animal deletion failed")
        
        # Verify animal deleted
        response = requests.get(
            f"{self.base_url}/animals/{animal_id}",
            headers=headers
        )
        self.assert_equal(response.status_code, 404, "Deleted animal still exists")
        
        # Verify forms also deleted (cascade)
        for form_id in form_ids:
            response = requests.get(
                f"{self.base_url}/forms/{form_id}",
                headers=headers
            )
            self.assert_equal(response.status_code, 404, f"Form {form_id} should be deleted")
        
        self.log(f"  ✓ Verified animal and all {len(form_ids)} forms deleted (cascade)")
    
    # ========== Run All Tests ==========
    
    def run_all_tests(self):
        """Run all tests in order"""
        self.log("\n" + "="*60, YELLOW)
        self.log("  SMOKE TESTS - Animal Tracking API", YELLOW)
        self.log("="*60 + "\n", YELLOW)
        
        # Check if server is running
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            if response.status_code != 200:
                self.log("✗ Server health check failed!", RED)
                return False
        except requests.exceptions.RequestException:
            self.log("✗ Cannot connect to server. Is it running?", RED)
            self.log(f"  Expected URL: {self.base_url}", RED)
            return False
        
        self.log("✓ Server is running\n", GREEN)
        
        # Authentication Tests
        self.log("=" * 60, YELLOW)
        self.log("AUTHENTICATION TESTS", YELLOW)
        self.log("=" * 60, YELLOW)
        self.test("Admin Login", self.test_admin_login)
        self.test("Regular User Login", self.test_regular_user_login)
        self.test("Invalid Login", self.test_invalid_login)
        
        # User CRUD Tests
        self.log("\n" + "=" * 60, YELLOW)
        self.log("USER CRUD TESTS", YELLOW)
        self.log("=" * 60, YELLOW)
        self.test("Create User", self.test_create_user)
        self.test("Read Users", self.test_read_users)
        self.test("Update User", self.test_update_user)
        self.test("Delete User", self.test_delete_user)
        self.test("Regular User Cannot Create User", self.test_regular_user_cannot_create_user)
        
        # Animal CRUD Tests
        self.log("\n" + "=" * 60, YELLOW)
        self.log("ANIMAL CRUD TESTS", YELLOW)
        self.log("=" * 60, YELLOW)
        self.test("Create Animal", self.test_create_animal)
        self.test("Read Animals", self.test_read_animals)
        self.test("Update Animal", self.test_update_animal)
        self.test("Create Form for Animal", self.test_create_form_for_animal)
        
        # Form CRUD Tests
        self.log("\n" + "=" * 60, YELLOW)
        self.log("FORM CRUD TESTS", YELLOW)
        self.log("=" * 60, YELLOW)
        self.test("Create Form", self.test_create_form)
        self.test("Read Forms by Animal", self.test_read_forms_by_animal)
        self.test("Read Forms by IDs", self.test_read_forms_by_ids)
        self.test("Generate Periodic Forms", self.test_generate_periodic_forms)
        self.test("Update Form", self.test_update_form)
        self.test("Delete Form", self.test_delete_form)
        
        # Cleanup Tests
        self.log("\n" + "=" * 60, YELLOW)
        self.log("CASCADE DELETE TESTS", YELLOW)
        self.log("=" * 60, YELLOW)
        self.test("Delete Animal (Cascade)", self.test_delete_animal)
        
        # Summary
        self.print_summary()
        
        # Return success status
        failed_tests = [t for t in self.test_results if not t[1]]
        return len(failed_tests) == 0
    
    def print_summary(self):
        """Print test summary"""
        total = len(self.test_results)
        passed = sum(1 for t in self.test_results if t[1])
        failed = total - passed
        
        self.log("\n" + "="*60, YELLOW)
        self.log("TEST SUMMARY", YELLOW)
        self.log("="*60, YELLOW)
        self.log(f"Total Tests: {total}")
        self.log(f"Passed: {passed}", GREEN)
        if failed > 0:
            self.log(f"Failed: {failed}", RED)
            self.log("\nFailed Tests:", RED)
            for name, success, error in self.test_results:
                if not success:
                    self.log(f"  ✗ {name}", RED)
                    if error:
                        self.log(f"    {error}", RED)
        else:
            self.log(f"Failed: {failed}", GREEN)
        
        self.log("="*60 + "\n", YELLOW)
        
        if failed == 0:
            self.log("🎉 ALL TESTS PASSED! 🎉", GREEN)
        else:
            self.log("⚠️  SOME TESTS FAILED", RED)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run smoke tests for Animal Tracking API")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    args = parser.parse_args()
    
    tester = APITester(args.url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)
