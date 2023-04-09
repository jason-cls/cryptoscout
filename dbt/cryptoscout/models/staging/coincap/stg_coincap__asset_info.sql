WITH

source AS (
    SELECT * FROM {{ source('coincap', 'asset_info') }}
),

asset_info AS (
    SELECT
        assetname AS asset_id,
        date,
        timestamputc AS timestamp_utc,
        rank,
        symbol,
        fullassetname AS full_name,
        supply AS available_supply,
        maxsupply AS max_supply,
        volumeusd24hr AS volume_usd_24hr,
        vwap24hr AS volume_weighted_avg_price_24hr,
        explorer AS explorer_url
    FROM source
)

SELECT * FROM asset_info
