WITH

market_history_deduped AS (
    SELECT * FROM {{ ref('int_market_history_deduplicated') }}
),

market_history_hourstamp AS (
    SELECT
        *,
        EXTRACT(HOUR FROM period_start_utc) AS hour_utc
    FROM market_history_deduped
),

hourly_interval_counts AS (
    SELECT
        exchange_id,
        base_asset_id,
        date,
        hour_utc,
        period_start_utc,
        open,
        close,
        ROW_NUMBER() OVER (
            PARTITION BY exchange_id, base_asset_id, date, hour_utc
            ORDER BY period_start_utc
        ) AS hourly_open_cnt,
        ROW_NUMBER() OVER (
            PARTITION BY exchange_id, base_asset_id, date, hour_utc
            ORDER BY period_start_utc DESC
        ) AS hourly_close_cnt
    FROM market_history_hourstamp
    ORDER BY 1, 2, 3, 4
),

-- first open value in an hour for each exchange and asset pair
hourly_opens AS (
    SELECT
        exchange_id,
        base_asset_id,
        date,
        hour_utc,
        open
    FROM hourly_interval_counts
    WHERE hourly_open_cnt = 1
),

-- last close value in an hour for each exchange and asset pair
hourly_closes AS (
    SELECT
        exchange_id,
        base_asset_id,
        date,
        hour_utc,
        close
    FROM hourly_interval_counts
    WHERE hourly_close_cnt = 1
),

-- Aggregate high, low, volume metrics in the same hour
hlv_regrained AS (
    SELECT
        exchange_id,
        base_asset_id,
        date,
        hour_utc,
        MIN(period_start_utc) AS period_start_utc,
        MAX(high) AS high,
        MIN(low) AS low,
        SUM(volume) AS volume
    FROM market_history_hourstamp
    GROUP BY 1, 2, 3, 4
    ORDER BY 1, 2, 3, 4
),

-- Aggregate open, high, low, close, volume metrics in the same hour
market_history_regrained AS (
    SELECT
        hlv_regrained.exchange_id,
        hlv_regrained.base_asset_id,
        hlv_regrained.date,
        hlv_regrained.hour_utc,
        hlv_regrained.period_start_utc,
        hourly_opens.open,
        hlv_regrained.high,
        hlv_regrained.low,
        hourly_closes.close,
        hlv_regrained.volume
    FROM hlv_regrained
    INNER JOIN hourly_opens
        ON
            hourly_opens.exchange_id = hlv_regrained.exchange_id
            AND hourly_opens.base_asset_id = hlv_regrained.base_asset_id
            AND hourly_opens.date = hlv_regrained.date
            AND hourly_opens.hour_utc = hlv_regrained.hour_utc
    INNER JOIN hourly_closes
        ON
            hourly_closes.exchange_id = hlv_regrained.exchange_id
            AND hourly_closes.base_asset_id = hlv_regrained.base_asset_id
            AND hourly_closes.date = hlv_regrained.date
            AND hourly_closes.hour_utc = hlv_regrained.hour_utc
    ORDER BY 1, 2, 3, 4
)

SELECT * FROM market_history_regrained
