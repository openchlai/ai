```markdown
# 📂 Case Creation API – Helpline CMS

## ✅ Overview

- **Endpoint**: `POST /api/cases/`
- **Purpose**: Creates a new case in the Helpline Case Management System.
- **Authentication**: Required (Bearer Token)
- **Content-Type**: `application/json`

---

## 🔐 Authorization

Use Bearer Token in the `Authorization` header.

```
Authorization: Bearer <your_access_token>
```

---

## 📤 Request Body

### 📘 Example Payload

```json
{
  "src": "walkin",
  "src_uid": "walkin-100-1741960667824",
  "src_address": "",
  "src_uid2": "walkin-100-1741960667824-2",
  "src_usr": "100",
  "src_vector": "2",
  "src_callid": "walkin-100-1741960667824",
  "src_ts": "1741960667.824",
  "reporter": {
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
  "case_category_id": "362484",
  "narrative": "---",
  "plan": "---",
  "justice_id": "",
  "assessment_id": "",
  "priority": "1",
  "status": "1",
  "escalated_to_id": "0"
}
```

---

## 📑 Field Descriptions

### 🧾 Metadata

| Field         | Type   | Description |
|---------------|--------|-------------|
| `src`         | string | Case intake source (e.g., `walkin`, `phone`). |
| `src_uid`     | string | Unique ID combining source, user ID, timestamp. |
| `src_address` | string | Address related to intake (blank for walk-ins). |
| `src_uid2`    | string | Alternate session/case ID. |
| `src_usr`     | string | User ID of agent/staff creating the case. |
| `src_vector`  | string | Source vector or terminal/device used. |
| `src_callid`  | string | Session or source call ID. |
| `src_ts`      | string | Case creation timestamp (Unix epoch with ms). |

---

### 👤 Reporter

| Field                 | Type   | Description |
|-----------------------|--------|-------------|
| `fname`               | string | Reporter’s full name. |
| `age_t`               | string | Age type (`0` = years, `1` = months). |
| `age`                 | string | Age value. |
| `dob`                 | string | Date of birth (Unix timestamp). |
| `age_group_id`        | string | ID for age group category. |
| `location_id`         | string | Geographical location ID. |
| `sex_id`              | string | Gender ID. |
| `landmark`            | string | Additional location landmark. |
| `nationality_id`      | string | Nationality ID. |
| `national_id_type_id` | string | Type of ID provided. |
| `national_id`         | string | National ID number. |
| `lang_id`             | string | Language ID. |
| `tribe_id`            | string | Tribe/ethnicity ID. |
| `phone`, `phone2`     | string | Contact numbers. |
| `email`               | string | Email address. |
| `.id`                 | string | Internal system reporter ID. |

---

### 👧 Clients Case

Array of clients with same fields as reporter. Multiple affected persons can be listed.

---

### 🚨 Perpetrators Case

Array of alleged perpetrators.

| Field             | Type   | Description |
|------------------|--------|-------------|
| `fname`, `age_t`, `age`, `dob` | string | Personal details. |
| `age_group_id`, `age_group`   | string | Age group ID and label. |
| `location_id`, `landmark`     | string | Location info. |
| `sex_id`, `sex`               | string | Gender info. |
| `relationship_id`             | string | Relationship to client. |
| `shareshome_id`               | string | Shared residence flag. |
| `health_id`, `employment_id`, `marital_id` | string | Socio-demographic indicators. |
| `guardian_fullname`          | string | Guardian name if minor. |
| `notes`                      | string | Notes or additional info. |
| `.id`                        | string | Internal system ID. |

---

### 📎 Attachments

- `attachments_case`: Array for any uploaded documents, photos, etc. (Empty in example).

---

### 🛠️ Services

- `services`: Array of service referrals or responses (counseling, police, etc.).

---

### 🧠 Other Fields

| Field               | Type   | Description |
|---------------------|--------|-------------|
| `knowabout116_id`   | string | How reporter found out about helpline. |
| `case_category_id`  | string | Category/type of the case. |
| `narrative`         | string | Description/story of the case. |
| `plan`              | string | Initial action plan. |
| `justice_id`        | string | Legal or justice system involvement. |
| `assessment_id`     | string | Associated assessments. |
| `priority`          | string | `"1"` = High, `"2"` = Medium, etc. |
| `status`            | string | `"1"` = Open; other values may vary. |
| `escalated_to_id`   | string | ID of the person or group case is escalated to. |

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

### ❌ Error (400 Bad Request)

```json
{
  "error": "Missing required field: caller_id"
}
```

---

## 🧪 Test Cases

- ✅ **Create Case - Valid Walk-in**
- ⚠️ **Create Case - Missing reporter**
- ❌ **Create Case - Invalid timestamp**
- 🔒 **Create Case - Unauthorized request**

---

## 📌 Notes
