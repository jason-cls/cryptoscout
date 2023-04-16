/*
Keep the latest record corresponding to a day when there are multiple records
in a day. Metrics from API are pre-aggregated and cannot be re-aggregated.
*/

WITH

exchange_info_deduped AS (
    SELECT * FROM {{ ref('int_exchange_info_deduplicated') }}
),

exchange_info_day_rowcounts AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY exchange_id, date_updated
            ORDER BY timestamp_updated_utc DESC
        ) AS day_record_num
    FROM exchange_info_deduped
),

exchange_info_regrained AS (
    SELECT
        exchange_id,
        date_updated,
        timestamp_updated_utc,
        full_name,
        rank,
        percent_total_volume,
        volume_usd,
        num_traiding_pairs,
        exchange_url
    FROM exchange_info_day_rowcounts
    WHERE day_record_num = 1
    ORDER BY 1, 2, 3
)

SELECT * FROM exchange_info_regrained
