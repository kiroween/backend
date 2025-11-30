-- Add audio_url column to tombstones table (PostgreSQL)
-- Run this migration to add TTS support

ALTER TABLE tombstones ADD COLUMN IF NOT EXISTS audio_url VARCHAR(500);

-- 선택사항: 인덱스 추가 (audio_url로 검색이 필요한 경우)
-- CREATE INDEX idx_tombstones_audio_url ON tombstones(audio_url);

-- 확인
SELECT column_name, data_type, character_maximum_length, is_nullable
FROM information_schema.columns
WHERE table_name = 'tombstones' AND column_name = 'audio_url';
