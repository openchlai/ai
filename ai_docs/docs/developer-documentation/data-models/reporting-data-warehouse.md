# Reporting Data Warehouse

## Overview

The reporting data warehouse provides optimized data structures for analytics, dashboards, and reports. It aggregates data from operational tables to enable fast queries and complex analysis without impacting the production system.

## Architecture

```
┌──────────────────────────────────────────────────────┐
│         Operational Database (helpline)              │
│   (kase, contact, kase_activity, auth, etc.)        │
└────────────────────┬─────────────────────────────────┘
                     │
                     │ ETL Process (Nightly)
                     ▼
┌──────────────────────────────────────────────────────┐
│          Reporting Data Warehouse                     │
│   (Aggregated tables, materialized views, metrics)   │
└──────────────────────────────────────────────────────┘
```

## Warehouse Tables

### `fact_case_daily` - Daily Case Metrics

Aggregated daily statistics for cases.

```sql
CREATE TABLE fact_case_daily (
  id INT PRIMARY KEY AUTO_INCREMENT,
  metric_date DATE NOT NULL,
  
  -- Case counts
  total_cases INT DEFAULT 0,
  new_cases INT DEFAULT 0,
  open_cases INT DEFAULT 0,
  assigned_cases INT DEFAULT 0,
  in_progress_cases INT DEFAULT 0,
  resolved_cases INT DEFAULT 0,
  closed_cases INT DEFAULT 0,
  
  -- By priority
  critical_cases INT DEFAULT 0,
  high_priority_cases INT DEFAULT 0,
  medium_priority_cases INT DEFAULT 0,
  low_priority_cases INT DEFAULT 0,
  
  -- By category
  abuse_cases INT DEFAULT 0,
  neglect_cases INT DEFAULT 0,
  mental_health_cases INT DEFAULT 0,
  education_cases INT DEFAULT 0,
  other_cases INT DEFAULT 0,
  
  -- AI metrics
  ai_processed_cases INT DEFAULT 0,
  high_risk_ai_cases INT DEFAULT 0,
  avg_ai_confidence DECIMAL(3,2),
  
  -- Performance metrics
  avg_response_time_minutes INT,
  avg_resolution_time_hours INT,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE KEY unique_date (metric_date),
  INDEX idx_date (metric_date)
);
```

### `fact_communication_daily` - Daily Communication Metrics

Tracks communication volumes and outcomes.

```sql
CREATE TABLE fact_communication_daily (
  id INT PRIMARY KEY AUTO_INCREMENT,
  metric_date DATE NOT NULL,
  
  -- Communication counts
  total_communications INT DEFAULT 0,
  inbound_calls INT DEFAULT 0,
  outbound_calls INT DEFAULT 0,
  sms_messages INT DEFAULT 0,
  emails INT DEFAULT 0,
  web_forms INT DEFAULT 0,
  whatsapp_messages INT DEFAULT 0,
  
  -- Call outcomes
  answered_calls INT DEFAULT 0,
  missed_calls INT DEFAULT 0,
  prank_calls INT DEFAULT 0,
  silent_calls INT DEFAULT 0,
  
  -- Call durations
  total_call_minutes INT DEFAULT 0,
  avg_call_duration_seconds INT,
  
  -- Cases created from communications
  cases_created_from_calls INT DEFAULT 0,
  cases_created_from_sms INT DEFAULT 0,
  cases_created_from_web INT DEFAULT 0,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE KEY unique_date (metric_date),
  INDEX idx_date (metric_date)
);
```

### `fact_user_activity` - User Performance Metrics

Tracks individual user performance and activity.

```sql
CREATE TABLE fact_user_activity (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  metric_date DATE NOT NULL,
  
  -- Activity counts
  login_count INT DEFAULT 0,
  total_active_time_minutes INT DEFAULT 0,
  
  -- Case handling
  cases_created INT DEFAULT 0,
  cases_updated INT DEFAULT 0,
  cases_assigned INT DEFAULT 0,
  cases_resolved INT DEFAULT 0,
  
  -- Communication handling
  calls_handled INT DEFAULT 0,
  total_call_time_minutes INT DEFAULT 0,
  
  -- Performance metrics
  avg_case_resolution_time_hours INT,
  avg_response_time_minutes INT,
  
  -- Quality metrics
  cases_escalated INT DEFAULT 0,
  cases_reopened INT DEFAULT 0,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (user_id) REFERENCES auth(id),
  UNIQUE KEY unique_user_date (user_id, metric_date),
  INDEX idx_user_id (user_id),
  INDEX idx_date (metric_date)
);
```

### `dim_date` - Date Dimension

Calendar dimension table for time-based analysis.

```sql
CREATE TABLE dim_date (
  date_id INT PRIMARY KEY,
  full_date DATE NOT NULL UNIQUE,
  
  -- Date parts
  day_of_week INT,
  day_of_month INT,
  day_of_year INT,
  week_of_year INT,
  month INT,
  quarter INT,
  year INT,
  
  -- Descriptive fields
  day_name VARCHAR(20),
  month_name VARCHAR(20),
  is_weekend BOOLEAN,
  is_holiday BOOLEAN,
  holiday_name VARCHAR(100),
  
  -- Fiscal periods (if needed)
  fiscal_year INT,
  fiscal_quarter INT,
  
  INDEX idx_date (full_date),
  INDEX idx_year_month (year, month)
);
```

### `fact_ai_performance` - AI Model Performance

Tracks AI service usage and accuracy.

```sql
CREATE TABLE fact_ai_performance (
  id INT PRIMARY KEY AUTO_INCREMENT,
  metric_date DATE NOT NULL,
  
  -- Processing volumes
  total_transcriptions INT DEFAULT 0,
  total_translations INT DEFAULT 0,
  total_classifications INT DEFAULT 0,
  
  -- Processing times
  avg_transcription_time_seconds INT,
  avg_translation_time_seconds INT,
  avg_classification_time_seconds INT,
  
  -- Accuracy metrics
  avg_transcription_confidence DECIMAL(3,2),
  avg_translation_confidence DECIMAL(3,2),
  avg_classification_confidence DECIMAL(3,2),
  
  -- By language
  swahili_transcriptions INT DEFAULT 0,
  english_transcriptions INT DEFAULT 0,
  other_language_transcriptions INT DEFAULT 0,
  
  -- Risk assessment
  critical_risk_cases INT DEFAULT 0,
  high_risk_cases INT DEFAULT 0,
  medium_risk_cases INT DEFAULT 0,
  low_risk_cases INT DEFAULT 0,
  
  -- Errors
  transcription_errors INT DEFAULT 0,
  translation_errors INT DEFAULT 0,
  classification_errors INT DEFAULT 0,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE KEY unique_date (metric_date),
  INDEX idx_date (metric_date)
);
```

## Materialized Views

### `mv_case_summary` - Real-time Case Overview

```sql
CREATE VIEW mv_case_summary AS
SELECT 
    COUNT(*) as total_cases,
    SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open_cases,
    SUM(CASE WHEN status = 'assigned' THEN 1 ELSE 0 END) as assigned_cases,
    SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress_cases,
    SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved_cases,
    SUM(CASE WHEN priority = 'critical' THEN 1 ELSE 0 END) as critical_cases,
    SUM(CASE WHEN priority = 'high' THEN 1 ELSE 0 END) as high_priority_cases,
    SUM(CASE WHEN ai_risk_level = 'critical' THEN 1 ELSE 0 END) as ai_critical_cases,
    AVG(ai_confidence) as avg_ai_confidence,
    MAX(created_at) as last_case_created
FROM kase
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY);
```

### `mv_user_performance` - Current Period User Stats

```sql
CREATE VIEW mv_user_performance AS
SELECT 
    u.id,
    u.username,
    u.role,
    COUNT(DISTINCT k.id) as cases_handled,
    COUNT(DISTINCT CASE WHEN k.status = 'resolved' THEN k.id END) as cases_resolved,
    AVG(TIMESTAMPDIFF(HOUR, k.created_at, k.updated_at)) as avg_resolution_hours,
    COUNT(DISTINCT c.id) as communications_handled,
    SUM(c.duration) / 60 as total_call_minutes,
    MAX(u.last_activity) as last_active
FROM 
    auth u
    LEFT JOIN kase k ON u.id = k.assigned_user_id
    LEFT JOIN contact c ON k.id = c.kase_id
WHERE 
    k.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    AND u.is_active = TRUE
GROUP BY 
    u.id, u.username, u.role;
```

## ETL Process

### Nightly Data Aggregation

```sql
-- ETL procedure run nightly
DELIMITER $$

CREATE PROCEDURE sp_aggregate_daily_metrics(IN target_date DATE)
BEGIN
    -- Case metrics
    INSERT INTO fact_case_daily (
        metric_date,
        new_cases,
        total_cases,
        open_cases,
        resolved_cases,
        critical_cases,
        high_priority_cases,
        ai_processed_cases,
        avg_ai_confidence
    )
    SELECT 
        target_date,
        COUNT(CASE WHEN DATE(created_at) = target_date THEN 1 END),
        COUNT(*),
        COUNT(CASE WHEN status = 'open' THEN 1 END),
        COUNT(CASE WHEN status = 'resolved' AND DATE(updated_at) = target_date THEN 1 END),
        COUNT(CASE WHEN priority = 'critical' THEN 1 END),
        COUNT(CASE WHEN priority = 'high' THEN 1 END),
        COUNT(CASE WHEN ai_transcript IS NOT NULL THEN 1 END),
        AVG(ai_confidence)
    FROM kase
    WHERE created_at <= DATE_ADD(target_date, INTERVAL 1 DAY)
    ON DUPLICATE KEY UPDATE
        new_cases = VALUES(new_cases),
        total_cases = VALUES(total_cases),
        open_cases = VALUES(open_cases),
        resolved_cases = VALUES(resolved_cases);
    
    -- Communication metrics
    INSERT INTO fact_communication_daily (
        metric_date,
        total_communications,
        inbound_calls,
        answered_calls,
        total_call_minutes,
        cases_created_from_calls
    )
    SELECT 
        target_date,
        COUNT(*),
        COUNT(CASE WHEN contact_type = 'call' AND direction = 'inbound' THEN 1 END),
        COUNT(CASE WHEN call_status = 'answered' THEN 1 END),
        SUM(duration) / 60,
        COUNT(DISTINCT CASE WHEN kase_id IS NOT NULL THEN kase_id END)
    FROM contact
    WHERE DATE(created_at) = target_date
    ON DUPLICATE KEY UPDATE
        total_communications = VALUES(total_communications),
        inbound_calls = VALUES(inbound_calls);
    
    -- User activity metrics
    INSERT INTO fact_user_activity (
        user_id,
        metric_date,
        cases_created,
        cases_updated,
        calls_handled
    )
    SELECT 
        u.id,
        target_date,
        COUNT(DISTINCT CASE WHEN k.created_by = u.id AND DATE(k.created_at) = target_date THEN k.id END),
        COUNT(DISTINCT CASE WHEN k.updated_by = u.id AND DATE(k.updated_at) = target_date THEN k.id END),
        COUNT(DISTINCT CASE WHEN c.created_by = u.id AND DATE(c.created_at) = target_date THEN c.id END)
    FROM 
        auth u
        LEFT JOIN kase k ON u.id IN (k.created_by, k.updated_by)
        LEFT JOIN contact c ON u.id = c.created_by
    WHERE u.is_active = TRUE
    GROUP BY u.id
    ON DUPLICATE KEY UPDATE
        cases_created = VALUES(cases_created),
        cases_updated = VALUES(cases_updated);
END$$

DELIMITER ;
```

### Schedule ETL Job

```bash
# Cron job to run nightly at 2 AM
0 2 * * * mysql -e "CALL helpline.sp_aggregate_daily_metrics(CURDATE() - INTERVAL 1 DAY);"
```

## Reporting Queries

### Monthly Performance Report

```sql
SELECT 
    DATE_FORMAT(metric_date, '%Y-%m') as month,
    SUM(new_cases) as total_new_cases,
    SUM(resolved_cases) as total_resolved_cases,
    SUM(critical_cases) as critical_cases,
    AVG(avg_response_time_minutes) as avg_response_time,
    AVG(avg_resolution_time_hours) as avg_resolution_time,
    SUM(ai_processed_cases) as ai_processed,
    AVG(avg_ai_confidence) as avg_ai_confidence
FROM 
    fact_case_daily
WHERE 
    metric_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
GROUP BY 
    DATE_FORMAT(metric_date, '%Y-%m')
ORDER BY 
    month DESC;
```

### Top Performing Users

```sql
SELECT 
    u.username,
    u.role,
    u.organization,
    SUM(fa.cases_resolved) as total_cases_resolved,
    AVG(fa.avg_case_resolution_time_hours) as avg_resolution_hours,
    SUM(fa.calls_handled) as total_calls,
    SUM(fa.total_call_time_minutes) as total_call_minutes
FROM 
    auth u
    INNER JOIN fact_user_activity fa ON u.id = fa.user_id
WHERE 
    fa.metric_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY 
    u.id, u.username, u.role, u.organization
HAVING 
    total_cases_resolved > 0
ORDER BY 
    total_cases_resolved DESC
LIMIT 10;
```

### Case Category Trends

```sql
SELECT 
    metric_date,
    abuse_cases,
    neglect_cases,
    mental_health_cases,
    education_cases,
    other_cases,
    (abuse_cases + neglect_cases + mental_health_cases) as critical_categories
FROM 
    fact_case_daily
WHERE 
    metric_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
ORDER BY 
    metric_date DESC;
```

### AI Performance Metrics

```sql
SELECT 
    metric_date,
    total_transcriptions,
    avg_transcription_time_seconds,
    avg_transcription_confidence,
    critical_risk_cases,
    high_risk_cases,
    ROUND((critical_risk_cases + high_risk_cases) * 100.0 / total_classifications, 2) as high_risk_percentage
FROM 
    fact_ai_performance
WHERE 
    metric_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
ORDER BY 
    metric_date DESC;
```

### Weekly Communication Pattern

```sql
SELECT 
    DAYNAME(d.full_date) as day_of_week,
    AVG(fc.inbound_calls) as avg_calls,
    AVG(fc.answered_calls) as avg_answered,
    AVG(fc.total_call_minutes) as avg_minutes
FROM 
    dim_date d
    INNER JOIN fact_communication_daily fc ON d.full_date = fc.metric_date
WHERE 
    d.full_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
GROUP BY 
    DAYOFWEEK(d.full_date), DAYNAME(d.full_date)
ORDER BY 
    DAYOFWEEK(d.full_date);
```

## Dashboard Metrics

### Real-Time Dashboard

```sql
-- Current active cases
SELECT COUNT(*) FROM kase WHERE status IN ('open', 'assigned', 'in_progress');

-- Cases requiring attention
SELECT COUNT(*) FROM kase 
WHERE priority IN ('critical', 'high') 
  AND status NOT IN ('resolved', 'closed');

-- Today's activity
SELECT 
    COUNT(CASE WHEN DATE(created_at) = CURDATE() THEN 1 END) as cases_today,
    COUNT(CASE WHEN DATE(updated_at) = CURDATE() AND status = 'resolved' THEN 1 END) as resolved_today
FROM kase;

-- Active users now
SELECT COUNT(DISTINCT user_id) 
FROM session 
WHERE last_activity >= DATE_SUB(NOW(), INTERVAL 30 MINUTE);
```

### Historical Performance

```sql
-- Compare this month vs last month
SELECT 
    'This Month' as period,
    SUM(new_cases) as new_cases,
    SUM(resolved_cases) as resolved_cases,
    AVG(avg_resolution_time_hours) as avg_resolution_hours
FROM fact_case_daily
WHERE metric_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')

UNION ALL

SELECT 
    'Last Month' as period,
    SUM(new_cases),
    SUM(resolved_cases),
    AVG(avg_resolution_time_hours)
FROM fact_case_daily
WHERE metric_date >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01')
  AND metric_date < DATE_FORMAT(CURDATE(), '%Y-%m-01');
```

## Data Retention Policy

### Warehouse Data Retention

```sql
-- Keep detailed daily metrics for 2 years
DELETE FROM fact_case_daily 
WHERE metric_date < DATE_SUB(CURDATE(), INTERVAL 2 YEAR);

DELETE FROM fact_communication_daily 
WHERE metric_date < DATE_SUB(CURDATE(), INTERVAL 2 YEAR);

-- Keep user activity for 1 year
DELETE FROM fact_user_activity 
WHERE metric_date < DATE_SUB(CURDATE(), INTERVAL 1 YEAR);

-- Archive older data to monthly summaries
INSERT INTO fact_case_monthly (year, month, ...)
SELECT YEAR(metric_date), MONTH(metric_date), SUM(...)
FROM fact_case_daily
WHERE metric_date < DATE_SUB(CURDATE(), INTERVAL 2 YEAR)
GROUP BY YEAR(metric_date), MONTH(metric_date);
```

## Integration with BI Tools

### Connection Details

For tools like Tableau, Power BI, or Metabase:

```
Host: localhost
Port: 3306
Database: helpline
Tables: fact_*, dim_*, mv_*
Read-only user recommended
```

### Sample Power BI DAX Measures

```dax
Total Cases = COUNT(fact_case_daily[new_cases])

Resolution Rate = 
DIVIDE(
    SUM(fact_case_daily[resolved_cases]),
    SUM(fact_case_daily[new_cases]),
    0
)

Avg Response Time (Hours) = 
AVERAGE(fact_case_daily[avg_response_time_minutes]) / 60
```

## Contributing to Reporting

When adding new metrics:

1. Update relevant fact tables
2. Modify ETL procedures
3. Add indexes for query performance
4. Document new metrics in this file
5. Update dashboard queries
6. Test with production-sized data

For complex analytics needs, consider adding new materialized views rather than running expensive queries on operational tables.