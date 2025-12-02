-- Add invite_token field to tombstones table
-- Migration: add_invite_token
-- Date: 2025-12-02

-- Add invite_token column (초대 링크용 UUID)
ALTER TABLE tombstones ADD COLUMN invite_token VARCHAR(100);

-- Create unique index on invite_token
CREATE UNIQUE INDEX IF NOT EXISTS idx_tombstones_invite_token ON tombstones(invite_token);
