import os
import pandas as pd
from io import StringIO
from dotenv import load_dotenv

from src.scripts.util.db_connection import db_connect

load_dotenv()


def extract():
    try:
        limit = 5000
        offset = 0
        total_rows = 0

        # Truncate table before insertion
        # DB connection
        conn = db_connect()
        cur = conn.cursor()

        print("-----------------------------------------------\n")
        print("[+] Extracting table electric_vehicles ... ")
        cur.execute("TRUNCATE TABLE electric_vehicles")

        while True:
            # fetch data
            url = f"{os.getenv('API_URL')}?$limit={limit}&$offset={offset}"
            df = pd.read_csv(url)

            if df.empty:
                break

            # convert DataFrame → CSV buffer
            buffer = StringIO()
            df.to_csv(buffer, index=False, header=False)
            buffer.seek(0)

            rows = len(df)
            total_rows += rows

            # COPY into PostgreSQL
            cur.copy_expert(
                """
                COPY electric_vehicles (
                    vin, county, city, state,
                    postal_code, model_year, make, model,
                    ev_type, cafv_eligibility, electric_range,
                    legislative_district, dol_vehicle_id,
                    vehicle_location, electric_utility, _2020_census_tract
                )
                FROM STDIN WITH CSV
                """,
                buffer,
            )
            conn.commit()
            print(f"Inserted total rows: {total_rows}")

            offset += limit

        cur.close()
        conn.close()
        print("\n✅ Data Extraction complete!")
        print("-----------------------------------------------\n")
    except Exception as e:
        print("[-] Error occured:", e)


if __name__ == "__main__":
    extract()
