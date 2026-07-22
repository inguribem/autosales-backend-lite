-- Adds soft-delete support to the invoices table.
-- Run manually against the live database (invoices table is not in init.sql).
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP DEFAULT NULL;
