WITH

asset_history_regrained AS (
    SELECT * FROM {{ ref('int_asset_history_regrained_hourly') }}
),

asset_prices AS (
    SELECT
        timestamp_utc,
        asset_id,
        price_usd
    FROM asset_history_regrained
),

asset_base AS (
    SELECT
        timestamp_utc,
        asset_id,
        price_usd,
        supply,
        ROW_NUMBER() OVER (ORDER BY timestamp_utc, asset_id) AS timepoint_id,
        CAST(FORMAT_TIMESTAMP('%Y%m%d', timestamp_utc) AS INT64) AS date_id,
        price_usd * supply AS marketcap_usd,
        TIMESTAMP_SUB(
            timestamp_utc, INTERVAL 24 HOUR
        ) AS timestamp_utc_24hr_ago
    FROM asset_history_regrained
    ORDER BY timestamp_utc, asset_id
),

fct_asset_history AS (
    SELECT
        asset_base.timepoint_id,
        asset_base.timestamp_utc,
        asset_base.date_id,
        asset_base.asset_id, -- replace later with asset_key
        -- asset_key (surrogate integer asset_key joined from dim_assets)
        asset_base.price_usd,
        asset_base.supply,
        asset_base.marketcap_usd,
        ((asset_base.price_usd / asset_prices.price_usd - 1) * 100
        ) AS price_percent_change_24hr
    FROM asset_base
    LEFT OUTER JOIN asset_prices
        ON
            asset_prices.asset_id = asset_base.asset_id
            AND asset_prices.timestamp_utc = asset_base.timestamp_utc_24hr_ago
    ORDER BY asset_base.timepoint_id
)

SELECT * FROM fct_asset_history
