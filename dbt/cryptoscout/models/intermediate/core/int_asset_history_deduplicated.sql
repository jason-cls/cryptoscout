WITH

stg_asset_history AS (
    SELECT * FROM {{ ref('stg_coincap__asset_history') }}
),

asset_history_identify_dupes AS (
    SELECT
        asset_id,
        timestamp_utc,
        date,
        price_usd,
        supply,
        ROW_NUMBER() OVER (
            PARTITION BY asset_id, timestamp_utc, date
            ORDER BY timestamp_request_utc DESC
        ) AS dupe_cnt
    FROM stg_asset_history
),

-- deduplicate by keeping rows with the most recent API request time
asset_history_deduped AS (
    SELECT
        asset_id,
        timestamp_utc,
        date,
        price_usd,
        supply
    FROM asset_history_identify_dupes
    WHERE dupe_cnt = 1
    ORDER BY 1, 2
)

SELECT * FROM asset_history_deduped
