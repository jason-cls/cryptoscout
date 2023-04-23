WITH

asset_info_regrained AS (
    SELECT * FROM {{ ref('int_asset_info_regrained_daily') }}
),

dim_assets AS (
    SELECT * FROM {{ ref('dim_assets') }}
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
        asset_info_base.timepoint_id,
        asset_info_base.date_id,
        dim_assets.asset_key,
        asset_info_base.timestamp_utc,
        asset_info_base.available_supply,
        asset_info_base.volume_usd_24hr,
        asset_info_base.volume_weighted_avg_price_24hr
    FROM asset_info_base
    LEFT OUTER JOIN dim_assets
        ON
            dim_assets.asset_id = asset_info_base.asset_id
            AND asset_info_base.timestamp_utc
            BETWEEN dim_assets.row_effective_time
            AND dim_assets.row_expiration_time
    ORDER BY asset_info_base.timepoint_id
)

SELECT * FROM fct_asset_dailystats
