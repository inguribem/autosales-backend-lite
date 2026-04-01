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


# -------------------------
# LOCATION MANAGEMENT
# -------------------------

CREATE TABLE movement_inventory (
    id SERIAL PRIMARY KEY, -- ID numérico autoincremental
    vin VARCHAR(50), -- Ahora puede ser nulo o repetirse si fuera necesario
    year INTEGER,
    make VARCHAR(50),
    model VARCHAR(50),
    trim VARCHAR(20),
    color VARCHAR(30),
    tag VARCHAR(50),
    status VARCHAR(30),
    current_location TEXT,
    price_purchase DECIMAL(12, 2) DEFAULT 0,
    price_sell DECIMAL(12, 2) DEFAULT 0,
    last_responsible_name VARCHAR(100),
    last_responsible_phone VARCHAR(20),
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE movement_history (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES movement_inventory(id), -- Relación por ID numérico
    vin_reported VARCHAR(50),
    location_reported TEXT,
    reported_by VARCHAR(100),
    original_message TEXT,
    message_type VARCHAR(20),
    voice_link TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



CREATE OR REPLACE FUNCTION set_vin_on_movement()
RETURNS TRIGGER AS
$$
BEGIN
    -- Solo actuar cuando el status sea 'received'
    IF NEW.status = 'received' THEN

        -- Intentar asignar VIN (solo si está vacío)
        IF NEW.vin IS NULL THEN
            SELECT v.vin
            INTO NEW.vin
            FROM vehicles v
            WHERE v.tag = NEW.tag
              AND TRIM(LOWER(v.make)) = TRIM(LOWER(NEW.make))
              AND TRIM(LOWER(v.model)) = TRIM(LOWER(NEW.model))
            LIMIT 1;
        END IF;

        -- Cambiar status a 'checked' SIEMPRE
        NEW.status := 'checked';

    END IF;

    RETURN NEW;
END;
$$
LANGUAGE plpgsql;


