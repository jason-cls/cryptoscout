WITH

source AS (
    SELECT * FROM {{ source('coincap', 'exchange_info') }}
),

exchange_info AS (
    SELECT
        exchangename AS exchange_id,
        date AS date_updated,
        timestamputc AS timestamp_updated_utc,
        fullexchangename AS full_name,
        rank,
        percenttotalvolume AS percent_total_volume,
        volumeusd AS volume_usd,
        tradingpairs AS num_trading_pairs,
        exchangeurl AS exchange_url,
        timestamprequestutc AS timestamp_request_utc
    FROM source
)

SELECT * FROM exchange_info
