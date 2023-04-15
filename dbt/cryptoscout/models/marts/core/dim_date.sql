WITH

datespine AS (
    SELECT * FROM {{ ref('all_dates') }}
),

dates AS (
    SELECT
        CAST(FORMAT_DATETIME('%Y%m%d', date_day) AS INT64) AS date_id,
        DATE(date_day) AS datestamp,
        EXTRACT(YEAR FROM date_day) AS year,
        EXTRACT(MONTH FROM date_day) AS month,
        EXTRACT(DAY FROM date_day) AS day_of_month,
        FORMAT_DATETIME('%A', date_day) AS day_of_week,
        FORMAT_DATETIME('%A', date_day) IN ('Saturday', 'Sunday') AS is_weekend,
        EXTRACT(WEEK FROM date_day) AS week_of_year,
        EXTRACT(QUARTER FROM date_day) AS calendar_quarter,
        FORMAT_DATETIME('%Y-Q%Q', date_day) AS year_quarter,
        FORMAT_DATETIME('%Y-%b', date_day) AS year_month
    FROM datespine
    ORDER BY 1 ASC
)

SELECT * FROM dates
