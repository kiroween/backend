-- Add share_token column to tombstones table for sharing functionality
-- PostgreSQL version

-- Add share_token column
ALTER TABLE tombstones ADD COLUMN IF NOT EXISTS share_token VARCHAR(100);

-- Create unique index on share_token
CREATE UNIQUE INDEX IF NOT EXISTS idx_tombstones_share_token ON tombstones(share_token);
