CREATE TABLE vehicles (
    id SERIAL PRIMARY KEY,
    vin VARCHAR(17) UNIQUE NOT NULL,
    year INT,
    make VARCHAR(50),
    model VARCHAR(50),
    trim VARCHAR(50),
    price INT,
    miles INT,
    dealer_name VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);




# -------------------------
# COST MANAGEMENT
# -------------------------

CREATE TABLE cost_mgmt (
    id SERIAL PRIMARY KEY,
    vehicle_vin VARCHAR(50) NOT NULL UNIQUE,

    buyer_fee NUMERIC(10,2) DEFAULT 0,
    inside_fees NUMERIC(10,2) DEFAULT 0,
    floor_plan_fees NUMERIC(10,2) DEFAULT 0,
    detailing NUMERIC(10,2) DEFAULT 0,
    mechanic NUMERIC(10,2) DEFAULT 0,
    bodyshop NUMERIC(10,2) DEFAULT 0,
    grua NUMERIC(10,2) DEFAULT 0,
    parts NUMERIC(10,2) DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (vehicle_vin)
        REFERENCES vehicles(vin)
        ON DELETE CASCADE
);

CREATE TABLE cost_history (
    id SERIAL PRIMARY KEY,
    vehicle_vin VARCHAR(50) NOT NULL,

    field_name VARCHAR(50) NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (vehicle_vin)
        REFERENCES vehicles(vin)
        ON DELETE CASCADE
);


CREATE OR REPLACE FUNCTION update_cost_mgmt_from_history()
RETURNS TRIGGER AS $$
BEGIN

    -- crear fila si no existe
    INSERT INTO cost_mgmt (vehicle_vin)
    VALUES (NEW.vehicle_vin)
    ON CONFLICT (vehicle_vin) DO NOTHING;

    -- sumar dinámicamente
    CASE NEW.field_name

        WHEN 'buyer_fee' THEN
            UPDATE cost_mgmt SET buyer_fee = buyer_fee + NEW.amount WHERE vehicle_vin = NEW.vehicle_vin;

        WHEN 'inside_fees' THEN
            UPDATE cost_mgmt SET inside_fees = inside_fees + NEW.amount WHERE vehicle_vin = NEW.vehicle_vin;

        WHEN 'floor_plan_fees' THEN
            UPDATE cost_mgmt SET floor_plan_fees = floor_plan_fees + NEW.amount WHERE vehicle_vin = NEW.vehicle_vin;

        WHEN 'detailing' THEN
            UPDATE cost_mgmt SET detailing = detailing + NEW.amount WHERE vehicle_vin = NEW.vehicle_vin;

        WHEN 'mechanic' THEN
            UPDATE cost_mgmt SET mechanic = mechanic + NEW.amount WHERE vehicle_vin = NEW.vehicle_vin;

        WHEN 'bodyshop' THEN
            UPDATE cost_mgmt SET bodyshop = bodyshop + NEW.amount WHERE vehicle_vin = NEW.vehicle_vin;

        WHEN 'grua' THEN
            UPDATE cost_mgmt SET grua = grua + NEW.amount WHERE vehicle_vin = NEW.vehicle_vin;

        WHEN 'parts' THEN
            UPDATE cost_mgmt SET parts = parts + NEW.amount WHERE vehicle_vin = NEW.vehicle_vin;

    END CASE;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_update_cost_mgmt
AFTER INSERT ON cost_history
FOR EACH ROW
EXECUTE FUNCTION update_cost_mgmt_from_history();