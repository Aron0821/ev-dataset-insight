CREATE OR REPLACE PROCEDURE load_location()
LANGUAGE plpgsql
AS $$
BEGIN
    TRUNCATE TABLE vehicle, location RESTART IDENTITY;
    
    INSERT INTO location (
        city, county, state, postal_code,
        legislative_district, vehicle_location
    )
    SELECT DISTINCT
        city,
        county,
        state,
        postal_code,
        legislative_district,
        vehicle_location
    FROM std_electric_vehicles
    WHERE city IS NOT NULL
    ON CONFLICT (city, county, state, postal_code) DO NOTHING;
END;
$$;