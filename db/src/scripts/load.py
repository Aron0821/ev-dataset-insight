from src.scripts.util.db_connection import db_connect

conn = db_connect()
cur = conn.cursor()


def load():
    print("-----------------------------------------------\n")
    # Load into model
    print("Loading into model ...")
    cur.execute("CALL load_vehicle_model()")
    conn.commit()
    print("Done!")

    # Load into location
    print("\nLoading into location ...")
    cur.execute("CALL load_location()")
    conn.commit()
    print("Done!")

    # Load into vehicle
    print("\nLoading into vehicle ...")
    cur.execute("CALL load_vehicle()")
    conn.commit()
    print("Done!")

    conn.close()
    print("\n✅ Data Load completed!")
    print("-----------------------------------------------\n")


if __name__ == "__main__":
    load()
