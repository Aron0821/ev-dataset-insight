from src.scripts.util.db_connection import db_connect

conn = db_connect()
cur = conn.cursor()


def transform():
    print("-----------------------------------------------\n")
    print("Transforming data into std_electric_vehicles ... ")

    cur.execute("Truncate table std_electric_vehicles")
    conn.commit()

    cur.execute("CALL transform_electric_vehicles()")
    conn.commit()

    conn.close()
    print("\n✅ Data Transformation complete!")
    print("-----------------------------------------------\n")


if __name__ == "__main__":
    transform()
