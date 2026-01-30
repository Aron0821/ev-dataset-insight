CREATE TABLE location (
    location_id SERIAL PRIMARY KEY,
    city VARCHAR(100),
    county VARCHAR(100),
    state CHAR(2),
    postal_code VARCHAR(10),
    legislative_district SMALLINT,
    vehicle_location GEOMETRY(Point, 4326),
    census_tract_2020 VARCHAR(15),
    UNIQUE(city, county, state, postal_code)
);
