import shutil
import os
from datetime import datetime
from models import Property, Tenant, Expense
from data_manager import DataManager

def verify_v2():
    print("--- Starting V2 Verification ---")
    
    # Setup clean environment
    if os.path.exists("datos_v2.json"):
        os.remove("datos_v2.json")

    # 1. Models & Persistence
    dm = DataManager("datos_v2.json")
    dm.add_property("Avenida Libertad 10")
    dm.set_user("Admin", "123456", "pass")
    
    prop = dm.properties[0]
    prop.mortgage_monthly = 500.0
    prop.tenant = Tenant("Inquilino V2", 1000.0)
    
    dm.save_data()
    print("[PASS] Helper data created and saved.")

    # 2. Verify Profit Calculation
    # Profit = Rent (1000) - Mortgage (500) = 500
    profit = prop.calculate_profit([])
    if profit == 500.0:
        print("[PASS] Basic Profit Calc: 1000 - 500 = 500")
    else:
        print(f"[FAIL] Basic Profit Calc: Expected 500, got {profit}")

    # 3. Verify Expense Deduction
    # Add an expense for this property for current month
    exp = Expense(100.0, "REPAIR", "Reparación Grifo", property_id=prop.id)
    dm.expenses.append(exp)
    
    profit_after_expense = prop.calculate_profit(dm.expenses)
    # Profit = 500 - 100 = 400
    if profit_after_expense == 400.0:
         print("[PASS] Profit with Expense: 500 - 100 = 400")
    else:
         print(f"[FAIL] Profit with Expense: Expected 400, got {profit_after_expense}")

    # 4. Verify File Path persistence
    prop.electricity_contract_path = "/tmp/test.pdf"
    dm.save_data()
    
    dm2 = DataManager("datos_v2.json")
    dm2.load_data()
    if dm2.properties[0].electricity_contract_path == "/tmp/test.pdf":
        print("[PASS] File path persistence valid.")
    else:
        print("[FAIL] File path persistence failed.")

    print("--- V2 Verification Complete ---")

if __name__ == "__main__":
    verify_v2()
