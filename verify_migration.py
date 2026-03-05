from gestor_alquiler import DataManager
import json

def verify_migration():
    dm = DataManager()
    dm.load_data()
    print("Data loaded.")
    
    with open("datos.json", "r") as f:
        data = json.load(f)
        print(f"File content: {json.dumps(data, indent=2)}")

    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        print("Migration SUCCESS: Data is a list of objects.")
    else:
        print("Migration FAILED or NO DATA.")

if __name__ == "__main__":
    verify_migration()
