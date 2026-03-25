import db_manager

def seed_database():
    print("Seeding Personnel...")
    db_manager.insert_personnel("B-101", "Olivia", "Benson", "Homicide", 5)
    db_manager.insert_personnel("B-102", "Dexter", "Morgan", "Lab Tech", 3)
    db_manager.insert_personnel("B-103", "James", "Gordon", "Major Crimes", 4)

    print("Seeding Storage Locations...")
    db_manager.insert_storage_location("LOC-F1", "Main Lab", "Room 10", "Deep Freezer", True)
    db_manager.insert_storage_location("LOC-S1", "Main Lab", "Room 12", "Secure Shelf", False)
    
    print("Database seeded successfully! Dev 3 can now build dropdown menus.")

if __name__ == "__main__":
    seed_database()