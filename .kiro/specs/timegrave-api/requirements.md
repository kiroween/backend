# Requirements Document

## Introduction

TimeGrave는 사용자가 디지털 타임캡슐(묘지)을 생성하고 관리할 수 있는 웹 애플리케이션입니다. 사용자는 회원가입 후 로그인하여 특정 날짜에 열리도록 설정된 타임캡슐에 기억과 메시지를 저장할 수 있습니다. 이 시스템은 신비롭고 영적인 테마로 죽음과 기억에 대한 경외감을 표현하며, 사용자에게 '기억의 사후 세계'와 같은 독특한 경험을 제공합니다.

## Glossary

- **TimeGrave System**: 타임캡슐 기반 기억 저장 및 관리 웹 애플리케이션
- **User**: TimeGrave System에 등록된 사용자 계정
- **Grave**: 특정 날짜에 열리도록 설정된 디지털 타임캡슐 (묘지)
- **Graveyard**: 사용자의 Grave들의 집합 (대시보드)
- **Unlock Date**: Grave가 열리는 날짜
- **Locked State**: Unlock Date 이전의 Grave 상태
- **Unlocked State**: Unlock Date 이후의 Grave 상태
- **Memory Content**: Grave에 저장된 텍스트, 이미지 등의 데이터
- **Session**: User의 로그인 상태를 유지하는 세션
- **API Response**: 표준 형식의 JSON 응답 (status, data 포함)

## Requirements

### Requirement 1

**User Story:** As a new user, I want to register for an account, so that I can create and manage my own graves.

#### Acceptance Criteria

1. WHEN a User submits registration data with valid email and password THEN the TimeGrave System SHALL create a new User account
2. WHEN a User submits registration data with an email that already exists THEN the TimeGrave System SHALL reject the registration and return an error with status 400
3. WHEN a User submits registration data with invalid email format THEN the TimeGrave System SHALL reject the registration and return a validation error with status 400
4. WHEN a User account is created THEN the TimeGrave System SHALL return the created User data with status 201

### Requirement 2

**User Story:** As a registered user, I want to log in to my account, so that I can access my graveyard.

#### Acceptance Criteria

1. WHEN a User submits valid email and password credentials THEN the TimeGrave System SHALL authenticate the User and create a Session
2. WHEN a User submits invalid credentials THEN the TimeGrave System SHALL reject the login and return an authentication error with status 401
3. WHEN a User successfully logs in THEN the TimeGrave System SHALL return User data and session information with status 200

### Requirement 3

**User Story:** As a logged-in user, I want to log out of my account, so that I can secure my session.

#### Acceptance Criteria

1. WHEN a User requests logout THEN the TimeGrave System SHALL invalidate the User's current Session
2. WHEN a Session is invalidated THEN the TimeGrave System SHALL return a success message with status 200

### Requirement 4

**User Story:** As a registered user, I want to delete my account, so that I can remove all my personal data.

#### Acceptance Criteria

1. WHEN a User requests account deletion THEN the TimeGrave System SHALL remove the User account from the database
2. WHEN a User account is deleted THEN the TimeGrave System SHALL delete all Graves owned by that User
3. WHEN account deletion is successful THEN the TimeGrave System SHALL return a success message with status 200

### Requirement 5

**User Story:** As a logged-in user, I want to view my graveyard dashboard, so that I can see all my graves at a glance.

#### Acceptance Criteria

1. WHEN a User requests the Graveyard dashboard THEN the TimeGrave System SHALL return a list of all Graves owned by that User
2. WHEN a Grave is in Locked State THEN the TimeGrave System SHALL include the remaining days until Unlock Date in the response
3. WHEN a Grave is in Unlocked State THEN the TimeGrave System SHALL indicate that the Grave is available to open
4. WHEN the Graveyard contains no Graves THEN the TimeGrave System SHALL return an empty list with status 200

### Requirement 6

**User Story:** As a logged-in user, I want to create a new grave, so that I can store memories to be revealed at a future date.

#### Acceptance Criteria

1. WHEN a User submits Grave creation data with valid title, content, and Unlock Date THEN the TimeGrave System SHALL create a new Grave in Locked State
2. WHEN a User submits an Unlock Date that is in the past THEN the TimeGrave System SHALL reject the creation and return a validation error with status 400
3. WHEN a Grave is created THEN the TimeGrave System SHALL associate the Grave with the creating User
4. WHEN a Grave is created THEN the TimeGrave System SHALL return the created Grave data with status 201
5. WHEN a User submits Grave creation data without required fields THEN the TimeGrave System SHALL reject the creation and return a validation error with status 400

### Requirement 7

**User Story:** As a logged-in user, I want to view details of a specific grave, so that I can see its content when it's unlocked or check its status when it's locked.

#### Acceptance Criteria

1. WHEN a User requests a Grave in Unlocked State THEN the TimeGrave System SHALL return the complete Memory Content with status 200
2. WHEN a User requests a Grave in Locked State THEN the TimeGrave System SHALL return only metadata without Memory Content with status 200
3. WHEN a User requests a non-existent Grave THEN the TimeGrave System SHALL return a not found error with status 404
4. WHEN the current date equals or exceeds the Unlock Date THEN the TimeGrave System SHALL transition the Grave from Locked State to Unlocked State

### Requirement 8

**User Story:** As a system, I want to automatically unlock graves when their unlock date arrives, so that users can access their memories at the scheduled time.

#### Acceptance Criteria

1. WHEN the current date equals the Unlock Date of a Grave THEN the TimeGrave System SHALL automatically transition that Grave from Locked State to Unlocked State
2. WHEN a Grave transitions to Unlocked State THEN the TimeGrave System SHALL make the Memory Content accessible
3. WHEN multiple Graves have the same Unlock Date THEN the TimeGrave System SHALL transition all of them to Unlocked State

### Requirement 9

**User Story:** As a developer, I want all API responses to follow a consistent format, so that client applications can handle responses predictably.

#### Acceptance Criteria

1. WHEN the TimeGrave System returns a successful response THEN the response SHALL include a status field and a data field containing the result
2. WHEN the TimeGrave System returns an error response THEN the response SHALL include a status field and an error field with a message
3. WHEN the TimeGrave System returns data THEN the response SHALL use JSON format
