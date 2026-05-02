-- Capa marts: resumen diario listo para dashboards en Looker

with staging as (
    select * from {{ ref('stg_weather') }}
),

daily as (
    select
        city,
        country,
        date(extracted_at)              as date,
        round(avg(temperature_c), 2)    as avg_temperature_c,
        round(min(temp_min_c), 2)       as min_temperature_c,
        round(max(temp_max_c), 2)       as max_temperature_c,
        round(avg(humidity_pct), 1)     as avg_humidity_pct,
        round(avg(wind_speed_ms), 2)    as avg_wind_speed_ms,
        round(avg(cloudiness_pct), 1)   as avg_cloudiness_pct,
        count(*)                        as total_readings

    from staging
    group by city, country, date(extracted_at)
)

select * from daily