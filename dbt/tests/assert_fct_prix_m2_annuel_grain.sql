-- The mart's grain is one row per arrondissement x year x dwelling type.
select code_commune, annee, type_local, count(*) as n
from {{ ref('fct_prix_m2_annuel') }}
group by 1, 2, 3
having count(*) > 1
