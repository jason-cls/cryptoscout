/*
Keep the latest record corresponding to a day when there are multiple records
in a day. Metrics from API are pre-aggregated and cannot be re-aggregated.
*/

WITH

asset_info_deduped AS (
    SELECT * FROM {{ ref('int_asset_info_deduplicated') }}
),

asset_info_day_rowcounts AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY asset_id, date ORDER BY timestamp_utc DESC
        ) AS day_record_num
    FROM asset_info_deduped
),

asset_info_regrained AS (
    SELECT
        asset_id,
        date,
        timestamp_utc,
        rank,
        symbol,
        full_name,
        available_supply,
        max_supply,
        volume_usd_24hr,
        volume_weighted_avg_price_24hr,
        explorer_url
    FROM asset_info_day_rowcounts
    WHERE day_record_num = 1
    ORDER BY 1, 2, 3
)

SELECT * FROM asset_info_regrained
