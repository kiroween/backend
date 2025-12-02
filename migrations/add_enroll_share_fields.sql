-- Add enroll and share fields to tombstones table
-- Migration: add_enroll_share_fields
-- Date: 2025-12-02

-- Add enroll column (작성자 userId)
ALTER TABLE tombstones ADD COLUMN enroll INTEGER;

-- Add share column (쓰기 권한 있는 친구들 JSON array)
ALTER TABLE tombstones ADD COLUMN share TEXT;

-- Create index on enroll for faster queries
CREATE INDEX IF NOT EXISTS idx_tombstones_enroll ON tombstones(enroll);

-- Update existing records: set enroll to user_id (기존 묘비는 본인이 작성한 것으로 설정)
UPDATE tombstones SET enroll = user_id WHERE enroll IS NULL;
