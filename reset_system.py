import init_db
import seed_data


def reset():
    print("--- Resetting Forensic System ---")
    init_db.initialize_database()
    seed_data.seed_database()
    print("--- System Ready for Testing ---")


if __name__ == "__main__":
    reset()
