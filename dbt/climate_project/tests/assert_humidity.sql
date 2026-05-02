select *
from {{ ref('stg_weather') }}
where humidity_pct < 0
   or humidity_pct > 100