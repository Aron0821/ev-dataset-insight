CREATE OR REPLACE PROCEDURE load_vehicle()
LANGUAGE plpgsql
AS $$
BEGIN
    TRUNCATE TABLE vehicle RESTART IDENTITY;
    
    INSERT INTO vehicle (
        vin, model_year, ev_type, electric_range,
        cafv_eligibility, dol_vehicle_id, electric_utility,
        model_id, location_id
    )
    SELECT
        ev.vin,
        ev.model_year,
        ev.ev_type,
        ev.electric_range,
        ev.cafv_eligibility,
        ev.dol_vehicle_id,
        ev.electric_utility,
        m.model_id,
        l.location_id
    FROM std_electric_vehicles ev
    JOIN model m
      ON ev.model = m.model
     AND ev.make = m.make
    JOIN location l
      ON ev.city = l.city
     AND ev.county = l.county
     AND ev.state = l.state
     AND ev.postal_code = l.postal_code
    WHERE ev.vin IS NOT NULL;
END;
$$;