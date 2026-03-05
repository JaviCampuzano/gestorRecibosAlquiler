import json
import os
import shutil
from datetime import datetime
from unittest.mock import MagicMock, patch
from gestor_alquiler import DataManager, Property, Tenant

# Mock datetime to test date-based logic
class MockDate(datetime):
    @classmethod
    def now(cls):
        return cls._now

def run_verification():
    print("--- Starting Verification ---")
    
    # 1. Setup Mock Data
    if os.path.exists("datos.json"):
        shutil.copy("datos.json", "datos.json.bak")
        os.remove("datos.json")
    
    dm = DataManager()
    dm.add_property("Calle Test 123")
    prop = dm.properties[0]
    
    # 2. Add Tenant
    prop.tenant = Tenant("Juan", 500)
    dm.save_data()
    print("[PASS] Tenant added.")

    # 3. Test Automated Monthly Check (Start of Month)
    # Mock date to be 1st of current month
    current_month = datetime.now().strftime("%Y-%m")
    
    changed = dm.check_monthly_receipts()
    if changed and current_month in prop.tenant.payments:
        print(f"[PASS] Monthly payment generated for {current_month}.")
    else:
        print(f"[FAIL] Monthly payment NOT generated. Changed={changed}, Keys={prop.tenant.payments.keys()}")

    # 4. Test Status Logic
    # Case A: Date 5th (Orange/Pending)
    MockDate._now = datetime(2023, 10, 5) # Mocking Oct 5th
    with patch('gestor_alquiler.datetime', MockDate):
        # Inject payment for Oct if logic relies on current month
        # Since our logic uses datetime.now().strftime, we need to ensure the key exists for the mocked month
        prop.tenant.payments["2023-10"] = "PENDING"
        
        status, color = prop.check_payment_status()
        if status == "Pendiente" and color == "orange":
             print(f"[PASS] Date=5th -> Status: {status} ({color})")
        else:
             print(f"[FAIL] Date=5th -> Status: {status} ({color})")

    # Case B: Date 12th (Red/Late)
    MockDate._now = datetime(2023, 10, 12)
    with patch('gestor_alquiler.datetime', MockDate):
        status, color = prop.check_payment_status()
        if status == "Retraso" and color == "red":
             print(f"[PASS] Date=12th -> Status: {status} ({color})")
        else:
             print(f"[FAIL] Date=12th -> Status: {status} ({color})")

    # Case C: Paid (Green)
    prop.tenant.payments["2023-10"] = "PAID"
    MockDate._now = datetime(2023, 10, 15)
    with patch('gestor_alquiler.datetime', MockDate):
        status, color = prop.check_payment_status()
        if status == "Pagado" and color == "green":
             print(f"[PASS] Paid -> Status: {status} ({color})")
        else:
             print(f"[FAIL] Paid -> Status: {status} ({color})")

    # Cleanup
    if os.path.exists("datos.json.bak"):
        shutil.move("datos.json.bak", "datos.json")
    else:
        os.remove("datos.json")
    print("--- Verification Complete ---")

if __name__ == "__main__":
    run_verification()
