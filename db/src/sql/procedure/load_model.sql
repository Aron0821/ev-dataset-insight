CREATE OR REPLACE PROCEDURE load_vehicle_model()
LANGUAGE plpgsql
AS $$
BEGIN
    TRUNCATE TABLE vehicle, model RESTART IDENTITY;
    
    INSERT INTO model (make, model)
    SELECT DISTINCT make, model
    FROM std_electric_vehicles
    WHERE model IS NOT NULL
      AND make IS NOT NULL
    ON CONFLICT (make, model) DO NOTHING;
END;
$$;