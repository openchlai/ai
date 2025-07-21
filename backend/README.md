# Helpline/Call Center REST API Documentation

## Overview

This API provides functionality for a helpline/call center system including call management, case tracking, messaging, and reporting.

## Table of Contents

- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [Agent Operations](#agent-operations)
  - [Call Control](#call-control)
  - [Case Management](#case-management)
  - [Messaging](#messaging)
  - [Reporting](#reporting)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)

## Authentication

### Login

```http
POST /auth
```

Authenticates user and establishes session

### Verify OTP

```http
POST /verifyOTP
```

Verifies one-time password for two-factor auth

### Logout

```http
GET /auth?logout=1
```

Terminates user session

### Reset Password

```http
POST /resetAuth
```

Initiates password reset process

## API Endpoints

### Agent Operations

#### Agent State Management

```http
POST /agent
```

Parameters:

- action=0 - Get channel ID
- action=1 - Login agent
- action=4 - Enable auto-answer
- action=5 - Disable auto-answer

### Call Control

#### Call Routing

```http
POST /chan
```

Handles call routing and transfers

Parameters:

- action=0 - Hangup call
- action=1 - Invite to call
- action=2 - Dial call
- action=3 - Transfer call
- action=4 - Conference call
- action=5 - Resume call

#### Supervisor Functions

```http
POST /sup
```

Supervisor call monitoring and control

Parameters:

- action - Supervisor action type
- exten - Agent extension to monitor

### Case Management

#### Create/Update Case

```http
POST /cases
```

Creates or updates a case record

#### Get Cases

```http
GET /cases
```

Retrieves case records with optional filters:

Filters:

- _title=my_cases - Only cases created by current user
- _title=esca_by_me - Cases escalated by current user
- _title=esca_to_me - Cases escalated to current user
- _title=all_cases_today - All cases created today

### Messaging

#### Inbound Messages

```http
POST /msg
```

Processes incoming messages from various channels

#### Outbound Messages

```http
POST /messages
```

Sends outgoing messages

### Reporting

#### Dashboard Data

```http
GET /dash
```

Returns dashboard metrics

Filters:

- dash_period - Time period (today, this_month, etc.)
- dash_gbv - Filter by GBV cases (both, vac, gbv)
- dash_src - Filter by source (all, call, sms, etc.)

#### Wallboard Data

```http
GET /wallonly
```

Returns data for wallboard displays

Parameters:

- metrics=1 - System metrics
- stats=1 - Agent statistics

## Data Models

### Case

```json
{
  "id": "string",
  "case_id": "string",
  "status": "number",
  "gbv_related": "boolean",
  "src": "string",
  "created_by_id": "string",
  "assigned_to_id": "string", 
  "escalated_to_id": "string",
  "escalated_by_id": "string",
  "created_on": "timestamp"
}
```

### Message

```json
{
  "id": "string",
  "src": "string",
  "src_uid": "string",
  "src_callid": "string",
  "src_address": "string",
  "src_msg": "string",
  "src_ts": "timestamp",
  "src_vector": "string"
}
```

## Error Handling

### Status Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 201  | Created |
| 202  | Accepted |
| 203  | Async processing |
| 400  | Bad request |
| 401  | Unauthorized |
| 403  | Forbidden |
| 404  | Not found |
| 412  | Precondition failed |
| 500  | Server error |

### Error Response Format

```json
{
  "errors": [
    ["error_code", "error_message"]
  ]
}
```

## Configuration

### Key Configuration Variables

```php
// Database
define("THE_DB_USN", "db_username");
define("THE_DB_NAME", "db_name"); 
define("THE_DB_SOCK", "db_socket_path");

// Recording Storage
define("RECORDING_ARCHIVE_URL", "http://archive-server/");

// Messaging Gateway
define("API_GATEWAY_USN", "gateway_user");
define("API_GATEWAY_PASS", "gateway_pass");
define("API_GATEWAY_AUTH", "http://gateway/auth");
define("API_GATEWAY_SEND_MSG", "http://gateway/send");
define("API_GATEWAY_CLOSE_MSG", "http://gateway/close/");

// System
define("VA_SIP_USER_PREFIX", "SIP/");
define("CASE_ID_PREFIX", "CASE-");
define("AGE_GROUP_ROOT_ID", "root_id_value");
```

### Permission Levels

```php
$RIGHTS_2 = [ /* Supervisor */ ];
$RIGHTS_6 = [ /* Agent */ ]; 
$RIGHTS_99 = [ /* Admin */ ];
```

## Usage Examples

### Agent Login

```bash
curl -X POST "http://api.example.com/agent" \
  -H "Content-Type: application/json" \
  -d '{"action":"1","exten":"101"}'
```

### Create Case

```bash
curl -X POST "http://api.example.com/cases" \
  -H "Content-Type: application/json" \
  -d '{"src":"call","src_address":"254712345678","case_category_id":"123"}'
```

### Get Dashboard Data

```bash
curl "http://api.example.com/dash?dash_period=this_month&dash_gbv=gbv"
```

### Get Call Recording

```bash
curl "http://api.example.com/recordings/abc123-def456"
```

### Send Message

```bash
curl -X POST "http://api.example.com/messages" \
  -H "Content-Type: application/json" \
  -d '{"src_address":"254712345678","src_msg":"Hello, how can we help?"}'
```

## Notes

- All API responses are in JSON format
- Authentication is session-based via cookies
- Timestamps are in UNIX epoch format
- Error responses include both code and human-readable message


## TEST COVERAGE

## Test Coverage

This test suite covers:

### Core Functions:

- `copy_from_pabx()` - Audio file retrieval
- `muu()` - Microservice communication
- `notify()` - Notification system
- `message_out()` - Outbound messaging

### Agent Operations:

- Login/logout
- Call control states

### Call Control:

- Call routing
- Transfers and conferences

### API Endpoints:

- Home/dashboard request
- Basic request routing

### Error Cases:

- Failed requests
- Invalid parameters

## Key Testing Approaches

### Function Mocking:

- Database connections
- External HTTP requests (cURL)
- Session handling

### Output Verification:

- Headers and content type
- JSON response structure
- Status codes

### Parameter Validation:

- Required parameters
- Parameter formats
- Business logic constraints

### State Verification:

- Session changes
- Database updates (via mocks)
- External system interactions

## Additional Test Cases to Consider

### Authentication Tests:

- Successful login
- Failed authentication
- Session timeout

### Error Condition Tests:

- Database failures
- External service outages
- Invalid input data

### Security Tests:

- SQL injection attempts
- XSS vulnerabilities
- CSRF protection

### Performance Tests:

- Response time benchmarks
- Concurrent request handling

## Running Tests

1. Save as `HelplineApiTest.php`
2. Install PHPUnit: `composer require phpunit/phpunit`
3. Run tests: `./vendor/bin/phpunit HelplineApiTest`

*Note: You may need to adjust paths and some function mocks based on your actual implementation details and dependencies.*