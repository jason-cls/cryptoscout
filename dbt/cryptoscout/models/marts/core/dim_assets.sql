WITH

asset_info_regrained AS (
    SELECT * FROM {{ ref('int_asset_info_regrained_daily') }}
),

-- compute hashed dim attributes excluding timestamp
distinct_asset_attributes AS (
    SELECT DISTINCT
        asset_id,
        timestamp_utc,
        full_name,
        symbol,
        max_supply,
        explorer_url,
        rank,
        {{ 
            dbt_utils.surrogate_key(
                ['asset_id', 'full_name', 'symbol', 'max_supply',
                 'explorer_url', 'rank']
            ) 
        }} AS scd_hash
    FROM asset_info_regrained
    ORDER BY asset_id, timestamp_utc
),

-- compact for scd2: remove adjacent duplicate hashes for an asset
compacted_asset_attributes AS (
    SELECT *
    FROM (
        SELECT
            *,
            LAG(scd_hash) OVER (
                PARTITION BY asset_id ORDER BY timestamp_utc
            ) AS prev_scd_hash
        FROM distinct_asset_attributes
    )
    WHERE prev_scd_hash IS NULL OR prev_scd_hash != scd_hash
),

asset_row_activetimes AS (
    SELECT
        *,
        timestamp_utc AS row_effective_time,
        LEAD(timestamp_utc) OVER (
            PARTITION BY asset_id ORDER BY timestamp_utc
        ) AS next_effective_time,
        ROW_NUMBER() OVER (ORDER BY asset_id, timestamp_utc) AS asset_key
    FROM compacted_asset_attributes
    ORDER BY asset_id, timestamp_utc
),

dim_assets AS (
    SELECT
        asset_key,
        asset_id,
        full_name,
        symbol,
        max_supply,
        explorer_url,
        rank,
        row_effective_time,
        CASE
            WHEN
                next_effective_time IS NULL
                THEN TIMESTAMP("9999-12-31 23:59:59+00")
            ELSE TIMESTAMP_SUB(next_effective_time, INTERVAL 1 MICROSECOND)
        END AS row_expiration_time,
        next_effective_time IS NULL AS current_row_indicator
    FROM asset_row_activetimes
    ORDER BY asset_key
)

SELECT * FROM dim_assets
