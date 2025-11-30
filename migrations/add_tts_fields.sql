-- Add audio_url column to tombstones table
-- Run this migration to add TTS support

ALTER TABLE tombstones ADD COLUMN audio_url VARCHAR(500);
