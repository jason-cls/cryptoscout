WITH

fct_exchange_dailystats AS (
    SELECT * FROM {{ ref('fct_exchange_dailystats') }}
),

dim_exchanges AS (
    SELECT * FROM {{ ref('dim_exchanges') }}
),

dim_date AS (
    SELECT * FROM {{ ref('dim_date') }}
),

obt_exchange_dailystats AS (
    SELECT
        {{
            dbt_utils.star(
                from=ref('fct_exchange_dailystats'),
                except=['date_updated_id', 'exchange_key']
            )
        }},
        {{
            dbt_utils.star(
                from=ref('dim_exchanges'),
                except=[
                    'exchange_key','row_effective_time',
                    'row_expiration_time', 'current_row_indicator'
                ]
            )
        }},
        {{ dbt_utils.star(from=ref('dim_date'), except=['date_id']) }}
    FROM fct_exchange_dailystats
    LEFT OUTER JOIN dim_exchanges
        ON fct_exchange_dailystats.exchange_key = dim_exchanges.exchange_key
    LEFT OUTER JOIN dim_date
        ON fct_exchange_dailystats.date_updated_id = dim_date.date_id
    ORDER BY fct_exchange_dailystats.dailystat_id
)

SELECT * FROM obt_exchange_dailystats
