WITH

stg_asset_info AS (
    SELECT * FROM {{ ref('stg_coincap__asset_info') }}
),

-- Deduplicate by selecting unique rows only. 
-- There is only one column indicating a row's timestamp.
asset_info_deduped AS (
    SELECT DISTINCT * FROM stg_asset_info
)

SELECT * FROM asset_info_deduped
