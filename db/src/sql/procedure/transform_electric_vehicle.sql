CREATE OR REPLACE PROCEDURE transform_electric_vehicles() 
LANGUAGE plpgsql AS $$ 
BEGIN 
    INSERT INTO std_electric_vehicles ( 
        vin, county, city, state, postal_code, model_year, make, model, 
        ev_type, cafv_eligibility, electric_range, legislative_district, 
        dol_vehicle_id, vehicle_location, electric_utility 
    ) 
    SELECT DISTINCT 
        vin, 
        county, 
        city, 
        state, 
        postal_code, 
        CASE 
            WHEN model_year IS NOT NULL AND model_year != '' 
            THEN model_year::FLOAT::SMALLINT 
            ELSE NULL 
        END, 
        make, 
        model, 
        ev_type, 
        cafv_eligibility, 
        CASE 
            WHEN electric_range IS NOT NULL AND electric_range != '' 
            THEN electric_range::FLOAT::SMALLINT 
            ELSE NULL 
        END, 
        CASE 
            WHEN legislative_district IS NOT NULL AND legislative_district != '' 
            THEN legislative_district::FLOAT::SMALLINT 
            ELSE NULL 
        END, 
        CASE 
            WHEN dol_vehicle_id IS NOT NULL AND dol_vehicle_id != '' 
            THEN dol_vehicle_id::FLOAT::BIGINT 
            ELSE NULL 
        END, 
        ST_SetSRID(
            ST_Point(
                split_part(replace(replace(vehicle_location, 'POINT (', ''), ')', ''), ' ', 1)::FLOAT,
                split_part(replace(replace(vehicle_location, 'POINT (', ''), ')', ''), ' ', 2)::FLOAT
            ), 
            4326
        ),
        electric_utility 
    FROM electric_vehicles 
    WHERE vin IS NOT NULL 
        AND vehicle_location IS NOT NULL 
        AND vehicle_location LIKE 'POINT (%)'; 
END; 
$$;