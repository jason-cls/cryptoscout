WITH

market_history_regrained AS (
    SELECT * FROM {{ ref('int_market_history_regrained_hourly') }}
),

dim_exchanges AS (
    SELECT * FROM {{ ref('dim_exchanges') }}
),

dim_assets AS (
    SELECT * FROM {{ ref('dim_assets') }}
),

market_base AS (
    SELECT
        period_start_utc,
        exchange_id,
        base_asset_id,
        open,
        high,
        low,
        close,
        volume,
        ROW_NUMBER() OVER (
            ORDER BY period_start_utc, exchange_id, base_asset_id
        ) AS period_id,
        CAST(FORMAT_TIMESTAMP('%Y%m%d', period_start_utc) AS INT64) AS date_id
    FROM market_history_regrained
    ORDER BY period_start_utc, exchange_id, base_asset_id
),

fct_market_history AS (
    SELECT
        market_base.period_id,
        market_base.date_id,
        dim_exchanges.exchange_key,
        dim_assets.asset_key AS base_asset_key,
        market_base.period_start_utc,
        market_base.open,
        market_base.high,
        market_base.low,
        market_base.close,
        market_base.volume
    FROM market_base
    LEFT OUTER JOIN dim_exchanges
        ON
            dim_exchanges.exchange_id = market_base.exchange_id
            AND market_base.period_start_utc
            BETWEEN dim_exchanges.row_effective_time
            AND dim_exchanges.row_expiration_time
    LEFT OUTER JOIN dim_assets
        ON
            dim_assets.asset_id = market_base.base_asset_id
            AND market_base.period_start_utc
            BETWEEN dim_assets.row_effective_time
            AND dim_assets.row_expiration_time
)

SELECT * FROM fct_market_history
ORDER BY period_id
