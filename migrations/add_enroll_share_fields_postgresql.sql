-- Add enroll and share fields to tombstones table (PostgreSQL)
-- Migration: add_enroll_share_fields_postgresql
-- Date: 2025-12-02

-- Add enroll column (작성자 userId)
ALTER TABLE tombstones ADD COLUMN IF NOT EXISTS enroll INTEGER;

-- Add share column (쓰기 권한 있는 친구들 JSON array)
ALTER TABLE tombstones ADD COLUMN IF NOT EXISTS share TEXT;

-- Create index on enroll for faster queries
CREATE INDEX IF NOT EXISTS idx_tombstones_enroll ON tombstones(enroll);

-- Update existing records: set enroll to user_id (기존 묘비는 본인이 작성한 것으로 설정)
UPDATE tombstones SET enroll = user_id WHERE enroll IS NULL;

-- Add comment for documentation
COMMENT ON COLUMN tombstones.enroll IS '작성자 userId (본인 또는 친구)';
COMMENT ON COLUMN tombstones.share IS '쓰기 권한 있는 친구들 (JSON array of userIds)';
