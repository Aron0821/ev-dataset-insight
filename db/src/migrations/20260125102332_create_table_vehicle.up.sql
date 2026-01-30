CREATE TABLE vehicle (
    vehicle_id SERIAL PRIMARY KEY,
    vin VARCHAR(17),
    model_year SMALLINT,
    ev_type VARCHAR(50),
    electric_range SMALLINT,
    cafv_eligibility VARCHAR(60),
    dol_vehicle_id BIGINT,
    electric_utility VARCHAR(255),
    model_id INT REFERENCES model(model_id),
    location_id INT REFERENCES location(location_id)
);

