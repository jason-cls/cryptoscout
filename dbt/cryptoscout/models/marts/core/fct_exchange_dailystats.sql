WITH

exchange_info_regrained AS (
    SELECT * FROM {{ ref('int_exchange_info_regrained_daily') }}
),

dim_exchanges AS (
    SELECT * FROM {{ ref('dim_exchanges') }}
),

exchange_info_base AS (
    SELECT
        timestamp_updated_utc,
        exchange_id,
        volume_usd,
        percent_total_volume,
        ROW_NUMBER() OVER (
            ORDER BY timestamp_updated_utc, exchange_id
        ) AS dailystat_id,
        CAST(
            FORMAT_TIMESTAMP('%Y%m%d', timestamp_updated_utc) AS INT64
        ) AS date_updated_id
    FROM exchange_info_regrained
    ORDER BY timestamp_updated_utc, exchange_id
),

fct_exchange_dailystats AS (
    SELECT
        exchange_info_base.dailystat_id,
        exchange_info_base.date_updated_id,
        dim_exchanges.exchange_key,
        exchange_info_base.timestamp_updated_utc,
        exchange_info_base.volume_usd,
        exchange_info_base.percent_total_volume
    FROM exchange_info_base
    LEFT OUTER JOIN dim_exchanges
        ON
            dim_exchanges.exchange_id = exchange_info_base.exchange_id
            AND exchange_info_base.timestamp_updated_utc
            BETWEEN dim_exchanges.row_effective_time
            AND dim_exchanges.row_expiration_time
)

SELECT * FROM fct_exchange_dailystats
ORDER BY dailystat_id
