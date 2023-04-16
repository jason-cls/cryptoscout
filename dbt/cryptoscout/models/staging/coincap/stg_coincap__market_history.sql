WITH

source AS (
    SELECT * FROM {{ source('coincap', 'market_history') }}
),

market_history AS (
    SELECT
        exchangename AS exchange_id,
        assetname AS base_asset_id,
        date,
        timestamputc AS period_start_utc,
        open,
        high,
        low,
        close,
        volume,
        timestamprequestutc AS timestamp_request_utc
    FROM source
)

SELECT * FROM market_history
