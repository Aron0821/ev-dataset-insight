CREATE TABLE model (
    model_id SERIAL PRIMARY KEY,
    model VARCHAR(100),
    make VARCHAR(100),
    UNIQUE (model, make)
);
