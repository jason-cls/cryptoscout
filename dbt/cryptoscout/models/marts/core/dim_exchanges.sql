WITH

exchange_info_regrained AS (
    SELECT * FROM {{ ref('int_exchange_info_regrained_daily') }}
),

-- compute hashed dim attributes excluding timestamp
distinct_exchange_attributes AS (
    SELECT DISTINCT
        exchange_id,
        timestamp_updated_utc,
        full_name,
        exchange_url,
        rank,
        num_trading_pairs,
        {{
            dbt_utils.surrogate_key(
                ['exchange_id', 'full_name', 'exchange_url',
                 'rank', 'num_trading_pairs']
            )
        }} AS scd_hash
    FROM exchange_info_regrained
    ORDER BY exchange_id, timestamp_updated_utc
),

-- compact for scd2: remove adjacent duplicate hashes for an exchange
compacted_exchange_attributes AS (
    SELECT *
    FROM (
        SELECT
            *,
            LAG(scd_hash) OVER (
                PARTITION BY exchange_id ORDER BY timestamp_updated_utc
            ) AS prev_scd_hash
        FROM distinct_exchange_attributes
    )
    WHERE prev_scd_hash IS NULL OR prev_scd_hash != scd_hash
),

exchanges_tmp AS (
    SELECT
        *,
        MIN(timestamp_updated_utc) OVER (
            PARTITION BY exchange_id
        ) AS min_row_effective_time,
        LEAD(timestamp_updated_utc) OVER (
            PARTITION BY exchange_id ORDER BY timestamp_updated_utc
        ) AS next_effective_time,
        ROW_NUMBER() OVER (
            ORDER BY exchange_id, timestamp_updated_utc
        ) AS exchange_key
    FROM compacted_exchange_attributes
    ORDER BY exchange_id, timestamp_updated_utc
),

dim_exchanges AS (
    SELECT
        exchange_key,
        exchange_id,
        full_name,
        exchange_url,
        rank,
        num_trading_pairs,
        CASE
            WHEN
                timestamp_updated_utc = min_row_effective_time
                THEN TIMESTAMP("1970-01-01 00:00:00+00")
            ELSE timestamp_updated_utc
        END AS row_effective_time,
        CASE
            WHEN
                next_effective_time IS NULL
                THEN TIMESTAMP("9999-12-31 23:59:59+00")
            ELSE TIMESTAMP_SUB(next_effective_time, INTERVAL 1 MICROSECOND)
        END AS row_expiration_time,
        next_effective_time IS NULL AS current_row_indicator
    FROM exchanges_tmp
)

SELECT * FROM dim_exchanges
ORDER BY exchange_key
