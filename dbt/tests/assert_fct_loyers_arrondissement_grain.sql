-- One row per arrondissement x segment, and every arrondissement has all 3 segments.
select code_commune, count(*) as n, count(distinct segment) as n_segments
from {{ ref('fct_loyers_arrondissement') }}
group by 1
having count(*) <> 3 or count(distinct segment) <> 3
