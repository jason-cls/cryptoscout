WITH

fct_asset_dailystats AS (
    SELECT * FROM {{ ref('fct_asset_dailystats') }}
),

dim_assets AS (
    SELECT * FROM {{ ref('dim_assets') }}
),

dim_date AS (
    SELECT * FROM {{ ref('dim_date') }}
),

obt_asset_dailystats AS (
    SELECT
        {{
            dbt_utils.star(
                from=ref('fct_asset_dailystats'), except=['date_id', 'asset_key']
            )
        }},
        {{
            dbt_utils.star(
                from=ref('dim_assets'), 
                except=[
                    'asset_key', 'row_effective_time',
                    'row_expiration_time', 'current_row_indicator'
                ]
            ) 
        }},
        {{ dbt_utils.star(from=ref('dim_date'), except=['date_id']) }}
    FROM fct_asset_dailystats
    LEFT OUTER JOIN dim_assets
        ON fct_asset_dailystats.asset_key = dim_assets.asset_key
    LEFT OUTER JOIN dim_date
        ON fct_asset_dailystats.date_id = dim_date.date_id
)

SELECT * FROM obt_asset_dailystats
ORDER BY dailystat_id
