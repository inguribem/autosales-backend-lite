-- Switches invoices timestamp defaults from UTC to Eastern time (America/New_York,
-- handles EST/EDT automatically), matching received_at which is already written in
-- Eastern by the ingestion pipeline. Forward-only: existing rows are left as-is.
ALTER TABLE invoices ALTER COLUMN created_at SET DEFAULT (now() AT TIME ZONE 'America/New_York');
ALTER TABLE invoices ALTER COLUMN updated_at SET DEFAULT (now() AT TIME ZONE 'America/New_York');
ALTER TABLE invoices ALTER COLUMN processed_at SET DEFAULT (now() AT TIME ZONE 'America/New_York');
