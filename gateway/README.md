# 📂 Case Creation API – Helpline CMS

## ✅ Overview

- **Endpoint**: `POST /api/webhook/webform/`
- **Purpose**: Creates a new case in the Helpline Case Management System.
- **Authentication**: Required (Bearer Token)
- **Content-Type**: `application/json`

---

## 🔐 Authentication and Authorization

### Email Verification Authentication Flow

We've implemented a secure email verification system for obtaining authentication tokens. This two-step process ensures that only authorized organizations can access the API.

#### Step 1: Request Email Verification

Send a request to initiate the email verification process:

```bash
curl -X POST https://backend.bitz-itc.com/api/webhook/webform/auth/request-verification/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-company-email@example.com",
    "organization_name": "Your Organization Name"
  }'
```

**Example Response:**
```json
{
  "status": "success",
  "message": "Verification code sent to provided email",
  "email": "your-company-email@example.com",
  "expires_at": "2025-04-24T15:30:45.123456Z"
}
```

A 6-digit OTP will be sent to the provided email address. The verification code expires after 10 minutes.

#### Step 2: Verify OTP and Obtain Token

Once you receive the verification code in your email, submit it to obtain your authentication token:

```bash
curl -X POST https://backend.bitz-itc.com/api/webhook/webform/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-company-email@example.com",
    "otp": "123456",
    "organization_name": "Your Organization Name"
  }'
```

**Example Response:**
```json
{
  "status": "success",
  "message": "Email verified successfully",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "organization_id": "550e8400-e29b-41d4-a716-446655440000",
  "expires": "2026-04-24T14:25:30.123456Z"
}
```

The JWT token is valid for 1 year from the date of issuance.

### Legacy Token Generation API

For backward compatibility, the direct token generation endpoint is still available (primarily for internal use):

```bash
curl -X POST https://backend.bitz-itc.com/api/webhook/webform/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "CPMIS System",
    "organization_email": "admin@cpmis.org"
  }'
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

```bash
curl -X POST https://backend.bitz-itc.com/api/webhook/webform/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "reporter": {
      "fname": "Reporting Person"
    },
    "gbv_related": false,
    "case_category_id": "362484",
    "narrative": "Case description here",
    "plan": "Initial assessment required",
    "priority": "2",
    "status": "1"
  }'
```

⚠️ **Important Notes**: 
- The token is valid for 1 year from issuance
- Store your token securely and treat it like a password
- If your organization is deactivated by an administrator, your token will no longer work even if it hasn't expired

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

## ✅ Ready-to-Use curl Commands

Below are ready-to-use curl commands with prefilled data for common scenarios. Simply replace the placeholder values with your actual information.

### Create a Basic Case (Minimal Fields)

```bash
curl -X POST https://backend.bitz-itc.com/api/webhook/webform/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "reporter": {
      "fname": "John Doe"
    },
    "gbv_related": false,
    "case_category_id": "362484",
    "narrative": "Client reports experiencing harassment at workplace. Needs assistance with reporting and safety planning.",
    "plan": "Initial assessment and safety planning. Refer to legal aid services.",
    "priority": "2",
    "status": "1"
  }'
```

### Create a Detailed Case (Physical Abuse)

```bash
curl -X POST https://backend.bitz-itc.com/api/webhook/webform/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "src": "webform",
    "reporter": {
      "fname": "Jane Smith",
      "age": "35",
      "sex_id": "122",
      "phone": "0712345678",
      "email": "jane.smith@example.com",
      "location_id": "258783"
    },
    "clients_case": [
      {
        "fname": "Sarah Johnson",
        "age": "28",
        "age_t": "0",
        "sex_id": "122",
        "phone": "0723456789",
        "location_id": "258783"
      }
    ],
    "perpetrators_case": [
      {
        "fname": "Robert Johnson",
        "age": "32",
        "sex_id": "121",
        "relationship_id": "363104"
      }
    ],
    "gbv_related": true,
    "case_category_id": "362485",
    "narrative": "Client reports physical abuse from spouse that has been ongoing for approximately 6 months. Most recent incident occurred yesterday resulting in visible bruising. Client fears for her safety and wants to understand her options.",
    "plan": "1. Immediate safety assessment and planning\n2. Medical referral for injury documentation\n3. Legal options counseling\n4. Shelter information provided",
    "priority": "1",
    "status": "1"
  }'
```

### Create a Child Abuse Case

```bash
curl -X POST https://backend.bitz-itc.com/api/webhook/webform/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "src": "webform",
    "reporter": {
      "fname": "Teacher Anonymous",
      "phone": "0734567890"
    },
    "clients_case": [
      {
        "fname": "Child (Anonymous)",
        "age": "9",
        "age_t": "0",
        "sex_id": "122"
      }
    ],
    "gbv_related": false,
    "case_category_id": "362487",
    "narrative": "Teacher reports concerns about potential child abuse. Student has shown behavioral changes, unexplained injuries, and expressed fear of going home. Teacher wants guidance on how to properly report and what services are available.",
    "plan": "1. Document all observations\n2. Connect with child protection services\n3. Provide guidance on mandatory reporting requirements\n4. Offer resources for child counseling",
    "priority": "1",
    "status": "1"
  }'
```

### Create a Psychosocial Support Case

```bash
curl -X POST https://backend.bitz-itc.com/api/webhook/webform/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "reporter": {
      "fname": "Self Referral"
    },
    "clients_case": [
      {
        "fname": "Self Referral",
        "age": "42",
        "age_t": "0",
        "sex_id": "121"
      }
    ],
    "gbv_related": false,
    "case_category_id": "362490",
    "narrative": "Client seeking psychosocial support. Reports experiencing depression and anxiety following job loss and family conflicts. Has expressed feelings of hopelessness and needs counseling resources.",
    "plan": "1. Initial assessment of mental health needs\n2. Provide immediate emotional support\n3. Refer to community mental health services\n4. Schedule follow-up contact",
    "priority": "2",
    "status": "1"
  }'
```

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

---

## 🛡️ Security and Authentication Troubleshooting

### OTP Email Issues

If you don't receive the verification email:
1. Check your spam/junk folder
2. Verify that the email address is correct
3. Contact support if the issue persists

### Authentication Errors

Common authentication issues and solutions:

| Error | Possible Cause | Solution |
|-------|----------------|----------|
| "Invalid verification code" | Typo in OTP entry | Double-check the code from your email |
| "Verification has expired" | OTP older than 10 minutes | Request a new verification code |
| "Invalid or expired token" | Token expired or tampered with | Obtain a new token through the verification process |
| "Organization access has been revoked" | Admin disabled your organization | Contact system administrator |

For persistent authentication issues, please contact support with your organization details.
