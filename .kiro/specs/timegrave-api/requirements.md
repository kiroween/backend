# Requirements Document

## Introduction

TimeGrave는 사용자가 디지털 타임캡슐(묘지)을 생성하고 관리할 수 있는 웹 애플리케이션입니다. 사용자는 특정 날짜에 열리도록 설정된 타임캡슐에 기억과 메시지를 저장할 수 있습니다. 이 시스템은 신비롭고 영적인 테마로 죽음과 기억에 대한 경외감을 표현하며, 사용자에게 '기억의 사후 세계'와 같은 독특한 경험을 제공합니다. MVP 버전에서는 단일 사용자(userId=1)만 지원합니다.

## Glossary

- **TimeGrave System**: 타임캡슐 기반 기억 저장 및 관리 웹 애플리케이션
- **Tombstone**: 특정 날짜에 열리도록 설정된 디지털 타임캡슐 (묘지)
- **Graveyard**: Tombstone들의 집합 (대시보드)
- **Unlock Date**: Tombstone이 열리는 날짜
- **Locked State**: Unlock Date 이전의 Tombstone 상태
- **Unlocked State**: Unlock Date 이후의 Tombstone 상태
- **Memory Content**: Tombstone에 저장된 텍스트, 이미지 등의 데이터
- **API Response**: 표준 형식의 JSON 응답 (status, data 포함)

## Requirements

### Requirement 1

**User Story:** As a user, I want to view my graveyard dashboard, so that I can see all my tombstones at a glance.

#### Acceptance Criteria

1. WHEN the user requests the Graveyard dashboard THEN the TimeGrave System SHALL return a list of all Tombstones for userId 1
2. WHEN a Tombstone is in Locked State THEN the TimeGrave System SHALL include the remaining days until Unlock Date in the response
3. WHEN a Tombstone is in Unlocked State THEN the TimeGrave System SHALL indicate that the Tombstone is available to open
4. WHEN the Graveyard contains no Tombstones THEN the TimeGrave System SHALL return an empty list with status 200

### Requirement 2

**User Story:** As a user, I want to create a new tombstone, so that I can store memories to be revealed at a future date.

#### Acceptance Criteria

1. WHEN the user submits Tombstone creation data with valid title, content, and Unlock Date THEN the TimeGrave System SHALL create a new Tombstone in Locked State
2. WHEN the user submits an Unlock Date that is in the past THEN the TimeGrave System SHALL reject the creation and return a validation error with status 400
3. WHEN a Tombstone is created THEN the TimeGrave System SHALL associate the Tombstone with userId 1
4. WHEN a Tombstone is created THEN the TimeGrave System SHALL return the created Tombstone data with status 201
5. WHEN the user submits Tombstone creation data without required fields THEN the TimeGrave System SHALL reject the creation and return a validation error with status 400

### Requirement 3

**User Story:** As a user, I want to view details of a specific tombstone, so that I can see its content when it's unlocked or check its status when it's locked.

#### Acceptance Criteria

1. WHEN the user requests a Tombstone in Unlocked State THEN the TimeGrave System SHALL return the complete Memory Content with status 200
2. WHEN the user requests a Tombstone in Locked State THEN the TimeGrave System SHALL return only metadata without Memory Content with status 200
3. WHEN the user requests a non-existent Tombstone THEN the TimeGrave System SHALL return a not found error with status 404
4. WHEN the current date equals or exceeds the Unlock Date THEN the TimeGrave System SHALL transition the Tombstone from Locked State to Unlocked State

### Requirement 4

**User Story:** As a system, I want to automatically unlock tombstones when their unlock date arrives, so that users can access their memories at the scheduled time.

#### Acceptance Criteria

1. WHEN the current date equals the Unlock Date of a Tombstone THEN the TimeGrave System SHALL automatically transition that Tombstone from Locked State to Unlocked State
2. WHEN a Tombstone transitions to Unlocked State THEN the TimeGrave System SHALL make the Memory Content accessible
3. WHEN multiple Tombstones have the same Unlock Date THEN the TimeGrave System SHALL transition all of them to Unlocked State

### Requirement 5

**User Story:** As a developer, I want all API responses to follow a consistent format, so that client applications can handle responses predictably.

#### Acceptance Criteria

1. WHEN the TimeGrave System returns a successful response THEN the response SHALL include a status field and a data field containing the result
2. WHEN the TimeGrave System returns an error response THEN the response SHALL include a status field and an error field with a message
3. WHEN the TimeGrave System returns data THEN the response SHALL use JSON format
4. WHEN a Tombstone is created THEN the response SHALL include a response message field with a user-friendly message
