WITH

stg_market_history AS (
    SELECT * FROM {{ ref('stg_coincap__market_history') }}
),

market_history_identify_dupes AS (
    SELECT
        exchange_id,
        base_asset_id,
        period_start_utc,
        date,
        open,
        high,
        low,
        close,
        volume,
        ROW_NUMBER() OVER (
            PARTITION BY exchange_id, base_asset_id, period_start_utc, date
            ORDER BY timestamp_request_utc DESC
        ) AS dupe_cnt
    FROM stg_market_history
),

-- deduplicate by keeping rows with the most recent API request time
market_history_deduped AS (
    SELECT
        exchange_id,
        base_asset_id,
        period_start_utc,
        date,
        open,
        high,
        low,
        close,
        volume
    FROM market_history_identify_dupes
    WHERE dupe_cnt = 1
    ORDER BY 1, 2, 3
)

SELECT * FROM market_history_deduped
