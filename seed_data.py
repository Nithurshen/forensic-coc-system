import db_manager


def seed_database():
    print("Seeding Storage Locations...")

    db_manager.insert_storage_location(
        "LOC-F1", "Main Lab", "Room 10", "Deep Freezer", True
    )
    db_manager.insert_storage_location(
        "LOC-B1", "Main Lab", "Room 10", "Biohazard Refrigerator", True
    )
    db_manager.insert_storage_location(
        "LOC-T1", "Toxicology", "Room 11", "Chemical Fridge", True
    )

    db_manager.insert_storage_location(
        "LOC-S1", "Main Lab", "Room 12", "Secure Shelf", False
    )
    db_manager.insert_storage_location(
        "LOC-H1", "Intake Bay", "Room 1", "Temporary Holding Locker", False
    )
    db_manager.insert_storage_location(
        "LOC-L1", "Evidence Vault", "Room 20", "Long-Term Bin", False
    )

    db_manager.insert_storage_location(
        "LOC-G1", "Ballistics", "Room 15", "Weapons Lockbox", False
    )
    db_manager.insert_storage_location(
        "LOC-D1", "Cyber Forensics", "Room 30", "Faraday Locker", False
    )
    db_manager.insert_storage_location(
        "LOC-V1", "Annex", "Garage B", "Vehicle Impound", False
    )

    print("Database seeded successfully! Expanded storage locations are ready.")


if __name__ == "__main__":
    seed_database()
