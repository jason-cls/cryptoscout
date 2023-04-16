WITH

asset_history_deduped AS (
    SELECT * FROM {{ ref('int_asset_history_deduplicated') }}
),

asset_history_hourstamp AS (
    SELECT
        *,
        EXTRACT(HOUR FROM timestamp_utc) AS hour_utc
    FROM asset_history_deduped
),

-- Aggregate metrics in the same hour
asset_history_regrained AS (
    SELECT
        asset_id,
        date,
        hour_utc,
        MIN(timestamp_utc) AS timestamp_utc,
        AVG(price_usd) AS price_usd,
        AVG(supply) AS supply
    FROM asset_history_hourstamp
    GROUP BY 1, 2, 3
    ORDER BY 1, 2, 3
)

SELECT * FROM asset_history_regrained
