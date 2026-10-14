-- The mart's grain is one row per arrondissement x month x dwelling type.
select code_commune, mois, type_local, count(*) as n
from {{ ref('fct_prix_m2_mensuel') }}
group by 1, 2, 3
having count(*) > 1
