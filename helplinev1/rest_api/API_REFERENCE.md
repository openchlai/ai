# Helpline REST API Reference

This document provides a comprehensive reference for the REST API used by the Helpline Case Management System. The API is responsible for all data operations, including authentication, case management, and communication handling.

The base URL for the API is `/helpline/api/`. All responses are in JSON format.

## Authentication

Authentication is session-based. A successful login returns a `HELPLINE_SESSION_ID` cookie that must be included in subsequent requests.

- `POST /sendOTP`
  - Initiates the One-Time Password process for login.
  - **Request Body:**
    ```json
    {
      "addr_addr": "user@example.com", // or phone number
      "addr_type": "email" // or "phone"
    }
    ```
  - **Response:** Standard success or error message.

- `POST /verifyOTP`
  - Verifies the provided OTP to establish a temporary session for password changes.
  - **Request Body:**
    ```json
    {
      "addr_addr": "user@example.com",
      "otp": "123456"
    }
    ```

- `POST /changeAuth`
  - Allows a logged-in user to change their own password.

- `GET /logout`
  - Terminates the current user session.

## Common Operations

### Fetching a List of Resources

`GET /{resource-name}`

- **Query Parameters for Pagination & Filtering:**
  - `_c={count}`: Number of records per page (e.g., `_c=20`).
  - `_a={offset}`: Starting offset for pagination.
  - `{field_name}={value}`: Filter by a specific field value (e.g., `status=1`).
  - `{field_name}__i={value}`: Filter using a specific operator (e.g., `created_on__i=2023-10-27`).

### Fetching a Single Resource

`GET /{resource-name}/{id}`

### Creating a Resource

`POST /{resource-name}`

- The request body should be a JSON object containing the resource's data.

### Updating a Resource

`POST /{resource-name}/{id}`

- The API uses `POST` with an ID for updates. The request body should be a JSON object with the fields to be updated.

---

## Core Resources

Below are the primary resources with examples for POST (create/update) and GET (response) data structures.

### `/cases` - Case Management

- **Description:** Manages cases. A case is the central record for any incident or interaction.

- **POST Request Body Example (Create/Update):**
  ```json
  {
    "gbv_related": "1", // 0 for No, 1 for Yes
    "case_category_id": "123",
    "narrative": "Detailed description of the case.",
    "plan": "Action plan for the case.",
    "priority": "2", // Enum: 1=Low, 2=Medium, 3=High
    "status": "1", // Enum: 1=Open, 2=Closed, 3=Escalated
    "reporter_id": "456", // ID of the associated reporter
    "src": "call", // Source of the case (e.g., call, sms, email)
    "src_uid": "unique-call-id-12345"
  }
  ```

- **GET Response Body Example (Single Case):**
  ```json
  {
    "cases": {
      "101": [
        "101", // id
        "1672531200", // created_on (Unix Timestamp)
        "admin", // created_by
        "1", // created_by_id
        "99", // created_by_role
        "1", // gbv_related
        "123", // case_category_id
        "GBV^Physical Assault", // case_category
        // ... other category fields ...
        "Detailed description of the case.", // narrative
        "Action plan for the case.", // plan
        "2", // priority
        "1", // status
        "456", // reporter_id
        "John Doe", // reporter_fullname
        // ... other reporter fields ...
        "call", // src
        "unique-call-id-12345" // src_uid
        // ... other fields ...
      ]
    }
  }
  ```

### `/clients` - Client Management

- **Description:** Manages client records. Clients are individuals directly involved in a case.

- **POST Request Body Example (Create/Update):**
  ```json
  {
    "case_id": "101",
    "contact_fname": "Jane",
    "contact_lname": "Doe",
    "contact_phone": "256700111222",
    "contact_sex_id": "15", // Category ID for Gender
    "contact_age": "25",
    "contact_location_id": "234", // Category ID for Location
    "is_reporter": "1" // 1 if this client is also the reporter
  }
  ```

- **GET Response Body Example (Single Client):**
  ```json
  {
    "clients": {
      "789": [
        "789", // id
        "1672531200", // created_on
        "admin", // created_by
        "1", // created_by_id
        "101", // case_id
        "987", // contact_id
        "Jane Doe", // contact_fullname
        "Jane", // contact_fname
        "Doe", // contact_lname
        "256700111222", // contact_phone
        "25", // contact_age
        "15", // contact_sex_id
        "Female", // contact_sex
        "234", // contact_location_id
        "Kampala", // contact_location
        // ... other contact fields ...
        "1" // is_reporter
      ]
    }
  }
  ```

### `/reporters` - Reporter Management

- **Description:** Manages reporter records. Reporters are individuals who report a case.

- **POST Request Body Example (Create/Update):**
  ```json
  {
    "case_id": "101",
    "contact_fname": "John",
    "contact_lname": "Doe",
    "contact_phone": "256700333444",
    "contact_sex_id": "14", // Category ID for Gender
    "src": "call",
    "src_uid": "unique-call-id-12345"
  }
  ```

- **GET Response Body Example (Single Reporter):**
  ```json
  {
    "reporters": {
      "456": [
        "456", // id
        "1672531200", // created_on
        "admin", // created_by
        "1", // created_by_id
        "654", // contact_id
        "John Doe", // contact_fullname
        // ... other contact fields ...
        "call", // src
        "unique-call-id-12345", // src_uid
        "101" // case_id
      ]
    }
  }
  ```

### `/perpetrators` - Perpetrator Management

- **Description:** Manages records of alleged perpetrators in a case.

- **POST Request Body Example (Create/Update):**
  ```json
  {
    "case_id": "101",
    "contact_fname": "Perp",
    "contact_lname": "Etrator",
    "contact_sex_id": "14",
    "relationship_id": "30" // Category ID for relationship to client
  }
  ```

### `/dispositions` - Call/Communication Dispositions

- **Description:** Logs the outcome or summary of a communication event (e.g., a call).

- **POST Request Body Example (Create):**
  ```json
  {
    "src": "call",
    "src_uid": "unique-call-id-12345",
    "src_address": "256700111222",
    "disposition_id": "50", // Category ID for the disposition type
    "reporter_id": "456",
    "case_id": "101"
  }
  ```

### `/attachments` - File Attachments

- **Description:** Manages file uploads associated with cases. This is a multipart request, not pure JSON.

- **POST Request:**
  - Use `multipart/form-data`.
  - Include a file field (e.g., `<input type="file" name="attachment">`).
  - Include other data fields like `case_id`.

---

## Call Center & Agent Management

These endpoints are used for real-time call center operations and typically receive form-encoded data rather than JSON.

- **`POST /agent`**: Manages agent state.
  - **Request Body (form-encoded):** `action=1`
    - `action: '0'`: Logout
    - `action: '1'`: Login
    - `action: '4'`: Enable auto-answer
    - `action: '5'`: Disable auto-answer

- **`POST /chan`**: Manages channel/call actions.
  - **Request Body (form-encoded):** `action=1&add=102`
    - `action: '0'`: Hangup
    - `action: '1'`: Invite to conference
    - `action: '2'`: Dial

- **`POST /sup`**: Supervisor actions.
  - **Request Body (form-encoded):** `action=listen&exten=101`
    - `action`: `listen`, `whisper`, `barge`

---
*This document was regenerated based on an analysis of the API source code. It provides a more detailed view of request and response structures.*