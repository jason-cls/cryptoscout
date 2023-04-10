-- Start date is inclusive. End date is exclusive.
{% set startdate = '2022-01-01' %}
{% set endyear = run_started_at.year + 1 %}
{% set enddate = endyear ~ '-01-01' %}

{{
    dbt_utils.date_spine(
        datepart="day",
        start_date="CAST('" ~ startdate ~ "' AS DATE)",
        end_date="CAST('" ~ enddate ~ "' AS DATE)"
    )
}}
