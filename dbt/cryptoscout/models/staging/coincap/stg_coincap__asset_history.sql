WITH

source AS (
    SELECT * FROM {{ source('coincap', 'asset_history') }}
),

asset_history AS (
    SELECT
        assetname AS asset_id,
        date,
        timestamputc AS timestamp_utc,
        priceusd AS price_usd,
        circulatingsupply AS supply,
        timestamprequestutc AS timestamp_request_utc
    FROM source
)

SELECT * FROM asset_history
