CREATE TABLE std_electric_vehicles (
    vin VARCHAR(17),
    county VARCHAR(100),
    city VARCHAR(100),
    state CHAR(2),
    postal_code VARCHAR(20),
    model_year SMALLINT,
    make VARCHAR(100),
    model VARCHAR(100),
    ev_type VARCHAR(50),
    cafv_eligibility VARCHAR(60),
    electric_range SMALLINT,
    legislative_district SMALLINT,
    dol_vehicle_id BIGINT,
    vehicle_location GEOMETRY(Point, 4326),
    electric_utility VARCHAR(255)
);
