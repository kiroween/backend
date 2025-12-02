-- Add invite_token field to tombstones table (PostgreSQL)
-- Migration: add_invite_token_postgresql
-- Date: 2025-12-02

-- Add invite_token column (초대 링크용 UUID)
ALTER TABLE tombstones ADD COLUMN IF NOT EXISTS invite_token VARCHAR(100);

-- Create unique index on invite_token
CREATE UNIQUE INDEX IF NOT EXISTS idx_tombstones_invite_token ON tombstones(invite_token);

-- Add comment for documentation
COMMENT ON COLUMN tombstones.invite_token IS '초대 링크용 UUID 토큰 (쓰기 권한)';
