-- Guard: no sale outside the plausible €/m² range may reach the marts.
-- The bounds live in dbt_project.yml (vars) and are applied in int_dvf__ventes_logement.
select *
from {{ ref('int_dvf__ventes_logement') }}
where prix_m2 not between {{ var('prix_m2_min') }} and {{ var('prix_m2_max') }}
