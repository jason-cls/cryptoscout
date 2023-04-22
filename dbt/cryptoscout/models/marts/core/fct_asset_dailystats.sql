WITH

asset_info_regrained AS (
    SELECT * FROM {{ ref('int_asset_info_regrained_daily') }}
),

asset_info_base AS (
    SELECT
        timestamp_utc,
        asset_id,
        available_supply,
        volume_usd_24hr,
        volume_weighted_avg_price_24hr,
        ROW_NUMBER() OVER (ORDER BY timestamp_utc, asset_id) AS timepoint_id,
        CAST(FORMAT_TIMESTAMP('%Y%m%d', timestamp_utc) AS INT64) AS date_id
    FROM asset_info_regrained
    ORDER BY timestamp_utc, asset_id
),

fct_asset_dailystats AS (
    SELECT
        timepoint_id,
        date_id,
        asset_id, -- replace later with asset_key
        -- asset_key (surrogate integer asset_key joined from dim_assets)
        timestamp_utc,
        available_supply,
        volume_usd_24hr,
        volume_weighted_avg_price_24hr
    FROM asset_info_base
    ORDER BY timepoint_id
)

SELECT * FROM fct_asset_dailystats
