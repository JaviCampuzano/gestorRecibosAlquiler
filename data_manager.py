import json
import os
from typing import List, Optional
from models import Property, User, Expense

class DataManager:
    def __init__(self, filepath="datos_v2.json"):
        self.filepath = filepath
        self.properties: List[Property] = []
        self.user: Optional[User] = None
        self.expenses: List[Expense] = []

    def load_data(self):
        if not os.path.exists(self.filepath):
            # Check for V1 migration
            if os.path.exists("datos.json"):
                self.migrate_v1_data()
            return

        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
                
            # Users
            self.user = None
            if data.get("user"):
                u = data["user"]
                self.user = User(u["name"], u["client_code"], u["password"])
                
            # Properties & Tenants
            self.properties = []
            for p_data in data.get("properties", []):
                # Property.from_dict now handles "tenant" -> "tenants" migration
                prop = Property.from_dict(p_data)
                self.properties.append(prop)

            # Expenses
            self.expenses = []
            for e_data in data.get("expenses", []):
                self.expenses.append(Expense.from_dict(e_data))
                
            # Migration V1 -> V2 Check (If V1 data exists and V2 is empty properties)
            if not self.properties and os.path.exists("datos.json"):
                self.migrate_v1_data()

            self.check_monthly_receipts()

        except Exception as e:
            print(f"Error loading data: {e}") 
            # In a real app we might want to backup the corrupt file
            

    def migrate_v1_data(self):
        # Load V1
        try:
            with open("datos.json", "r") as f:
                old_data = json.load(f)
            # Create V2 structure
            # V1 was list of dicts (Properties)
            if old_data and isinstance(old_data, list):
                if isinstance(old_data[0], str): # Very old format
                     self.properties = [Property(a) for a in old_data]
                else: 
                     self.properties = [Property.from_dict(p) for p in old_data]
            
            self.save_data()
        except Exception as e:
            print(f"Migration error: {e}")

    def save_data(self):
        data = {
            "user": self.user.to_dict() if self.user else None,
            "properties": [p.to_dict() for p in self.properties],
            "expenses": [e.to_dict() for e in self.expenses]
        }
        with open(self.DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def check_monthly_receipts(self):
        current_month = datetime.datetime.now().strftime("%Y-%m")
        
        for prop in self.properties:
            # Check for each tenant
            for tenant in prop.tenants:
                if current_month not in tenant.payments:
                    tenant.payments[current_month] = "PENDING"
        
        self.save_data()

    def add_property(self, address):
        if not any(p.address == address for p in self.properties):
            self.properties.append(Property(address))
            self.save_data()
            return True
        return False
    
    def set_user(self, name, code, password):
        self.user = User(name, code, password)
        self.save_data()
