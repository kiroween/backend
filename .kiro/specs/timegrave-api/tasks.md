# Implementation Plan

- [x] 1. Set up project structure and Docker environment
  - Create project directory structure (app/routers, app/services, app/repositories, app/models, app/schemas)
  - Create requirements.txt with FastAPI, SQLAlchemy, Pydantic, APScheduler dependencies
  - Create Dockerfile for FastAPI application
  - Create docker-compose.yml for local development
  - Create .dockerignore and .gitignore files
  - _Requirements: All_

- [x] 2. Implement database layer with SQLAlchemy
  - [x] 2.1 Create database models and configuration
    - Create SQLAlchemy Tombstone model with all required fields
    - Set up database connection and session management
    - Create database initialization script
    - Configure SQLite database path
    - _Requirements: 1.1, 2.1, 3.1_

  - [x] 2.2 Implement Tombstone repository
    - Create repository class with CRUD methods
    - Implement get_all() method for listing tombstones
    - Implement get_by_id() method for retrieving single tombstone
    - Implement create() method for inserting new tombstones
    - Implement update_unlock_status() method for batch unlocking
    - _Requirements: 1.1, 2.1, 3.1, 4.1_

  - [ ]* 2.3 Write property test for repository
    - **Property 1: Graveyard completeness**
    - **Validates: Requirements 1.1**

- [x] 3. Implement Pydantic schemas for request/response validation
  - [x] 3.1 Create Pydantic models
    - Create CreateTombstoneDto schema with field validation
    - Create TombstoneResponseDto schema
    - Create ApiSuccessResponse and ApiErrorResponse schemas
    - _Requirements: 2.1, 5.1, 5.2_

- [x] 4. Implement service layer with business logic
  - [x] 4.1 Create TombstoneService class
    - Implement list_tombstones() method with days remaining calculation
    - Implement create_tombstone() method with validation
    - Implement get_tombstone() method with content filtering
    - Implement check_and_unlock_tombstones() method for scheduler
    - _Requirements: 1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 4.1_

  - [x] 4.2 Implement date validation and utility functions
    - Create function to validate unlock date is in the future
    - Create function to calculate days remaining until unlock date
    - _Requirements: 1.2, 2.2_

  - [ ]* 4.3 Write property test for date validation
    - **Property 5: Past date rejection**
    - **Validates: Requirements 2.2**

  - [ ]* 4.4 Write property test for days remaining calculation
    - **Property 2: Locked tombstone days remaining**
    - **Validates: Requirements 1.2**

  - [ ]* 4.5 Write property test for tombstone creation
    - **Property 4: Valid tombstone creation**
    - **Validates: Requirements 2.1**

  - [ ]* 4.6 Write property test for userId assignment
    - **Property 6: Tombstone userId assignment**
    - **Validates: Requirements 2.3**

  - [ ]* 4.7 Write property test for required fields validation
    - **Property 8: Required fields validation**
    - **Validates: Requirements 2.5**

- [x] 5. Implement FastAPI routers and endpoints
  - [x] 5.1 Create tombstone router
    - Implement GET /api/graveyard endpoint
    - Implement POST /api/tombstones endpoint with Pydantic validation
    - Implement GET /api/tombstones/{id} endpoint
    - Add exception handlers for common errors
    - _Requirements: 1.1, 2.1, 3.1, 5.1, 5.2_

  - [x] 5.2 Implement response formatting utilities
    - Create success response formatter with status and data.result structure
    - Create error response formatter with status and error.message structure
    - Create user-friendly message generator for tombstone creation
    - _Requirements: 5.1, 5.2, 5.4_

  - [ ]* 5.3 Write property test for response formats
    - **Property 15: Success response format**
    - **Property 16: Error response format**
    - **Property 18: Creation response message**
    - **Validates: Requirements 5.1, 5.2, 5.4**

- [x] 6. Implement content filtering logic
  - [x] 6.1 Add content filtering to get_tombstone method
    - Check tombstone unlock status
    - Include content field only if is_unlocked is True
    - Include days_remaining field only if is_unlocked is False
    - _Requirements: 3.1, 3.2_

  - [ ]* 6.2 Write property test for content accessibility
    - **Property 9: Unlocked content accessibility**
    - **Validates: Requirements 3.1**

  - [ ]* 6.3 Write property test for content filtering
    - **Property 10: Locked content filtering**
    - **Validates: Requirements 3.2**

- [x] 7. Implement automatic unlock mechanism with APScheduler
  - [x] 7.1 Create unlock scheduler service
    - Set up APScheduler with cron trigger to run daily at midnight
    - Implement logic to find tombstones with unlock_date <= current date
    - Call service method to update is_unlocked status
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ]* 7.2 Write property test for automatic unlock
    - **Property 12: Automatic unlock on date**
    - **Validates: Requirements 3.4, 4.1**

  - [ ]* 7.3 Write property test for content accessibility after unlock
    - **Property 13: Content accessible after unlock**
    - **Validates: Requirements 4.2**

  - [ ]* 7.4 Write property test for batch unlock
    - **Property 14: Batch unlock**
    - **Validates: Requirements 4.3**

- [x] 8. Set up FastAPI application and configure middleware
  - [x] 8.1 Create main FastAPI application
    - Configure CORS middleware
    - Include API routers with /api prefix
    - Add global exception handler
    - Configure startup and shutdown events
    - _Requirements: All_

  - [x] 8.2 Create application entry point
    - Initialize database tables on startup
    - Start APScheduler on startup
    - Configure uvicorn server settings
    - _Requirements: All_

- [ ] 9. Configure Docker deployment
  - [x] 9.1 Finalize Dockerfile
    - Use Python 3.11 slim base image
    - Install dependencies from requirements.txt
    - Copy application code
    - Expose port 8000
    - Set CMD to run uvicorn
    - _Requirements: All_

  - [x] 9.2 Configure docker-compose
    - Define FastAPI service
    - Mount volume for SQLite database persistence
    - Configure environment variables
    - Set up port mapping (8000:8000)
    - _Requirements: All_

- [x] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ]* 11. Write integration tests for API endpoints
  - [ ]* 11.1 Write integration test for GET /api/graveyard
    - Test empty graveyard returns empty list
    - Test graveyard with multiple tombstones
    - Test locked vs unlocked tombstone formatting
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [ ]* 11.2 Write integration test for POST /api/tombstones
    - Test successful creation with valid data
    - Test rejection of past unlock dates
    - Test rejection of missing required fields
    - Test response format and status codes
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [ ]* 11.3 Write integration test for GET /api/tombstones/{id}
    - Test retrieval of locked tombstone (no content)
    - Test retrieval of unlocked tombstone (with content)
    - Test 404 error for non-existent tombstone
    - _Requirements: 3.1, 3.2, 3.3_

  - [ ]* 11.4 Write integration test for JSON response format
    - **Property 17: JSON response format**
    - **Validates: Requirements 5.3**

- [ ]* 12. Write remaining property tests
  - [ ]* 12.1 Write property test for unlocked tombstone indication
    - **Property 3: Unlocked tombstone indication**
    - **Validates: Requirements 1.3**

  - [ ]* 12.2 Write property test for creation response format
    - **Property 7: Creation response format**
    - **Validates: Requirements 2.4**

  - [ ]* 12.3 Write property test for non-existent tombstone error
    - **Property 11: Non-existent tombstone error**
    - **Validates: Requirements 3.3**

- [ ] 13. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
