WITH

stg_exchange_info AS (
    SELECT * FROM {{ ref('stg_coincap__exchange_info') }}
),

exchange_info_identify_dupes AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY exchange_id, date_updated, timestamp_updated_utc
            ORDER BY timestamp_request_utc DESC
        ) AS dupe_cnt
    FROM stg_exchange_info
),

-- deduplicate by keeping rows with the most recent API request time
exchange_info_deduped AS (
    SELECT
        exchange_id,
        date_updated,
        timestamp_updated_utc,
        full_name,
        rank,
        percent_total_volume,
        volume_usd,
        num_trading_pairs,
        exchange_url
    FROM exchange_info_identify_dupes
    WHERE dupe_cnt = 1
    ORDER BY 1, 2, 3
)

SELECT * FROM exchange_info_deduped
