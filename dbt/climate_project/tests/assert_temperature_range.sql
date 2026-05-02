-- Test custom: la temperatura debe estar entre -50 y 70 grados
-- Si la query devuelve filas, el test falla

select *
from  {{ref('stg_weather')}}
where temperature_c < -50
or temperature_c > 70