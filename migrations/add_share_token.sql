-- Add share_token column to tombstones table for sharing functionality
-- SQLite version

-- Add share_token column
ALTER TABLE tombstones ADD COLUMN share_token VARCHAR(100);

-- Create unique index on share_token
CREATE UNIQUE INDEX idx_tombstones_share_token ON tombstones(share_token);
