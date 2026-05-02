-- Capa staging: limpia y tipifica los datos crudos de BigQuery

with source as (
    select * from {{ source('climate_data_raw', 'weather_raw') }}
),

staged as (
    select
        city,
        country,
        cast(temperature    as FLOAT64)  as temperature_c,
        cast(feels_like     as FLOAT64)  as feels_like_c,
        cast(temp_min       as FLOAT64)  as temp_min_c,
        cast(temp_max       as FLOAT64)  as temp_max_c,
        cast(humidity       as INT64)    as humidity_pct,
        cast(pressure       as INT64)    as pressure_hpa,
        cast(wind_speed     as FLOAT64)  as wind_speed_ms,
        cast(wind_deg       as INT64)    as wind_direction_deg,
        weather_main,
        weather_desc,
        cast(cloudiness     as INT64)    as cloudiness_pct,
        cast(visibility     as INT64)    as visibility_m,
        cast(extracted_at   as TIMESTAMP) as extracted_at,
        cast(loaded_at      as TIMESTAMP) as loaded_at

    from source
)

select * from staged