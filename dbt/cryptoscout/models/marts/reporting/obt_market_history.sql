WITH

fct_market_history AS (
    SELECT * FROM {{ ref('fct_market_history') }}
),

dim_assets AS (
    SELECT * FROM {{ ref('dim_assets') }}
),

dim_exchanges AS (
    SELECT * FROM {{ ref('dim_exchanges') }}
),

dim_date AS (
    SELECT * FROM {{ ref('dim_date') }}
),

obt_market_history AS (
    SELECT
        {{
            dbt_utils.star(
                from=ref('fct_market_history'), 
                except=['date_id', 'base_asset_key', 'exchange_key']
            ) 
        }},
        dim_assets.asset_id,
        dim_assets.full_name AS asset_full_name,
        dim_assets.symbol AS asset_symbol,
        dim_assets.max_supply AS asset_max_supply,
        dim_assets.explorer_url AS asset_explorer_url,
        dim_assets.rank AS asset_rank,
        dim_exchanges.exchange_id,
        dim_exchanges.full_name AS exchange_full_name,
        dim_exchanges.exchange_url,
        dim_exchanges.rank AS exchange_rank,
        dim_exchanges.num_trading_pairs AS exchange_num_trading_pairs,
        {{ dbt_utils.star(from=ref('dim_date'), except=['date_id']) }}
    FROM fct_market_history
    LEFT OUTER JOIN dim_assets
        ON fct_market_history.base_asset_key = dim_assets.asset_key
    LEFT OUTER JOIN dim_exchanges
        ON fct_market_history.exchange_key = dim_exchanges.exchange_key
    LEFT OUTER JOIN dim_date
        ON fct_market_history.date_id = dim_date.date_id
    ORDER BY fct_market_history.period_id
)

SELECT * FROM obt_market_history
