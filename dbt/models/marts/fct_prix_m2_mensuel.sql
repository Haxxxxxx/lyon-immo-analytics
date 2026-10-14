-- One row per arrondissement x month x dwelling type.
-- Median is the headline metric: a few luxury or abnormal sales pull the average up.
with ventes as (
    select * from {{ ref('int_dvf__ventes_logement') }}
),

arrondissements as (
    select * from {{ ref('arrondissements') }}
)

select
    v.code_commune,
    a.nom                                                       as arrondissement,
    date_trunc('month', v.date_mutation)::date                  as mois,
    v.type_local,
    count(*)                                                    as nb_ventes,
    percentile_cont(0.5) within group (order by v.prix_m2)      as prix_m2_median,
    avg(v.prix_m2)                                              as prix_m2_moyen
from ventes v
inner join arrondissements a using (code_commune)
group by 1, 2, 3, 4
