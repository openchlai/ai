# 📂 Case Creation API – Helpline CMS

## ✅ Overview

- **Endpoint**: `POST /api/webhook/webform/`
- **Purpose**: Creates a new case in the Helpline Case Management System.
- **Authentication**: Required (Bearer Token)
- **Content-Type**: `application/json`

---

## 🔐 Authentication and Authorization

### Token Generation API (Live Environment Only)

To obtain an authentication token, use the following endpoint (available only in the live environment):

```
POST /api/webhook/webform/auth/token/
Content-Type: application/json
```

**Request Body:**
```json
{
  "organization_name": "CPMIS System",
  "organization_email": "admin@cpmis.org"
}
```

**Example Response:**
```json
{
  "status": "success",
  "message": "Authentication token generated successfully.",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "organization_id": "12345",
  "expires": "2026-04-03T11:09:50.554Z"
}
```

### Using the Token

Use the obtained Bearer Token in the `Authorization` header for subsequent API calls:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

⚠️ **Important Note**: The token generation API is only available in the live environment, not in testing or staging environments.

---

## 📤 Request Body

### 📘 Example Payload

```json
{
  "src": "webform", # or CMIS
  "src_uid": "walkin-100-1741960667824",
  "src_address": "",
  "src_uid2": "walkin-100-1741960667824-2",
  "src_usr": "100",
  "src_vector": "2",
  "src_callid": "walkin-100-1741960667824",
  "src_ts": "1741960667.824",
  "reporter": {
    "fname": "Ras Singh",  /* MANDATORY */
    "age_t": "0",
    "age": "22",
    "dob": "1046120400",
    "age_group_id": "361953",
    "location_id": "258783",
    "sex_id": "",
    "landmark": "",
    "nationality_id": "",
    "national_id_type_id": "",
    "national_id": "",
    "lang_id": "",
    "tribe_id": "",
    "phone": "",
    "phone2": "",
    "email": "",
    ".id": "86164"
  },
  "clients_case": [
    {
      "fname": "Ras Singh",
      "age_t": "0",
      "age": "22",
      "dob": "1046120400",
      "age_group_id": "361953",
      "location_id": "258783",
      "sex_id": "",
      "landmark": "",
      "nationality_id": "",
      "national_id_type_id": "",
      "national_id": "",
      "lang_id": "",
      "tribe_id": "",
      "phone": "",
      "phone2": "",
      "email": "",
      ".id": "86164"
    }
  ],
  "perpetrators_case": [
    {
      "fname": "Patel",
      "age_t": "0",
      "age": "44",
      "dob": "353365200",
      "age_group_id": "361955",
      "age_group": "31-45",
      "location_id": "",
      "sex_id": "121",
      "sex": "^Male",
      "landmark": "",
      "nationality_id": "",
      "national_id_type_id": "",
      "national_id": "",
      "lang_id": "",
      "tribe_id": "",
      "phone": "",
      "phone2": "",
      "email": "",
      "relationship_id": "",
      "shareshome_id": "",
      "health_id": "",
      "employment_id": "",
      "marital_id": "",
      "guardian_fullname": "",
      "notes": "",
      ".id": ""
    }
  ],
  "attachments_case": [],
  "services": [],
  "knowabout116_id": "",
  "gbv_related": true,  /* MANDATORY */
  "case_category_id": "362484",  /* MANDATORY */
  "narrative": "---",  /* MANDATORY */
  "plan": "---",  /* MANDATORY */
  "justice_id": "",
  "assessment_id": "",
  "priority": "1",  /* MANDATORY */
  "status": "1",  /* MANDATORY */
  "escalated_to_id": "0"
}
```

---

## 📑 Field Descriptions

### 🧾 Metadata

| Field         | Type   | Description | Required |
|---------------|--------|-------------|----------|
| `src`         | string | Case intake source (e.g., `walkin`, `phone`, `CMIS`). | No |
| `src_uid`     | string | Unique ID combining source, user ID, timestamp. | No |
| `src_address` | string | Address related to intake (blank for walk-ins). | No |
| `src_uid2`    | string | Alternate session/case ID. | No |
| `src_usr`     | string | User ID of agent/staff creating the case. | No |
| `src_vector`  | string | Source vector or terminal/device used. | No |
| `src_callid`  | string | Session or source call ID. | No |
| `src_ts`      | string | Case creation timestamp (Unix epoch with ms). | No |

---

### 👤 Reporter

| Field                 | Type   | Description | Required |
|-----------------------|--------|-------------|----------|
| `fname`               | string | Reporter's full name. | **YES** |
| `age_t`               | string | Age type (`0` = years, `1` = months). | No |
| `age`                 | string | Age value. | No |
| `dob`                 | string | Date of birth (Unix timestamp). | No |
| `age_group_id`        | string | ID for age group category. | No |
| `location_id`         | string | Geographical location ID. | No |
| `sex_id`              | string | Gender ID. | No |
| `landmark`            | string | Additional location landmark. | No |
| `nationality_id`      | string | Nationality ID. | No |
| `national_id_type_id` | string | Type of ID provided. | No |
| `national_id`         | string | National ID number. | No |
| `lang_id`             | string | Language ID. | No |
| `tribe_id`            | string | Tribe/ethnicity ID. | No |
| `phone`, `phone2`     | string | Contact numbers. | No |
| `email`               | string | Email address. | No |
| `.id`                 | string | Internal system reporter ID. | No |

---

### 👧 Clients Case

Array of clients with same fields as reporter. Multiple affected persons can be listed.

---

### 🚨 Perpetrators Case

Array of alleged perpetrators.

| Field             | Type   | Description | Required |
|------------------|--------|-------------|----------|
| `fname`, `age_t`, `age`, `dob` | string | Personal details. | No |
| `age_group_id`, `age_group`   | string | Age group ID and label. | No |
| `location_id`, `landmark`     | string | Location info. | No |
| `sex_id`, `sex`               | string | Gender info. | No |
| `relationship_id`             | string | Relationship to client. | No |
| `shareshome_id`               | string | Shared residence flag. | No |
| `health_id`, `employment_id`, `marital_id` | string | Socio-demographic indicators. | No |
| `guardian_fullname`          | string | Guardian name if minor. | No |
| `notes`                      | string | Notes or additional info. | No |
| `.id`                        | string | Internal system ID. | No |

---

### 📎 Attachments

- `attachments_case`: Array for any uploaded documents, photos, etc. (Empty in example).

---

### 🛠️ Services

- `services`: Array of service referrals or responses (counseling, police, etc.).

---

### 🧠 Other Fields

| Field               | Type   | Description | Required |
|---------------------|--------|-------------|----------|
| `gbv_related`       | boolean| Indicates if case is gender-based violence related. | **YES** |
| `knowabout116_id`   | string | How reporter found out about helpline. | No |
| `case_category_id`  | string | Category/type of the case. | **YES** |
| `narrative`         | string | Description/story of the case. | **YES** |
| `plan`              | string | Initial action plan. | **YES** |
| `justice_id`        | string | Legal or justice system involvement. | No |
| `assessment_id`     | string | Associated assessments. | No |
| `priority`          | string | `"1"` = High, `"2"` = Medium, etc. | **YES** |
| `status`            | string | `"1"` = Open; other values may vary. | **YES** |
| `escalated_to_id`   | string | ID of the person or group case is escalated to. | No |

---

## ✅ Response

### 📘 Success (201 Created)

```json
{
  "id": "case_987654",
  "status": "open",
  "created_at": "2025-04-05T10:30:02Z",
  "assigned_to": "agent_001",
  "reference_number": "HL-CMS-000123"
}
```

### ❌ Error Responses

**400 Bad Request**
```json
{
  "error": "Missing required field: [field_name]"
}
```

**401 Unauthorized**
```json
{
  "status": "error",
  "message": "Invalid or expired authentication token"
}
```

**403 Forbidden**
```json
{
  "status": "error",
  "message": "Organization not authorized to access this resource"
}
```

---

## 🧪 Test Cases

- ✅ **Create Case - Valid Walk-in**
- ⚠️ **Create Case - Missing mandatory field**
- ❌ **Create Case - Invalid timestamp**
- 🔒 **Create Case - Unauthorized request (invalid or expired token)**

---

## 📌 Notes

### Mandatory Fields with Default Values

All mandatory fields can be pre-populated with default values of your choosing:

| Mandatory Field      | Possible Default Value | Notes |
|----------------------|------------------------|-------|
| `reporter.fname`     | "Client" | Default for anonymous cases |
| `gbv_related`        | | Can be set based on your use case |
| `case_category_id`   |  | Default to a general category ID |
| `narrative`          |  | Placeholder until case details are added |
| `plan`               | "Initial assessment required" | Standard starting action |
| `priority`           | "2" | Default to medium priority |
| `status`             | "1" | Default to open status |

### Minimal Valid Payload

Below is an example of a minimal valid payload containing only the mandatory fields with sample default values:

```json
{
  "reporter": {
    "fname": "jasson"
  },
  "gbv_related": false,
  "case_category_id": "362484",
  "narrative": "I was asulted",
  "plan": "Initial assessment required",
  "priority": "2",
  "status": "1"
}
```

These default values can be customized according to your organization's needs and automatically included in your API implementation.
