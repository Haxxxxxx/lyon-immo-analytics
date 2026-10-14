-- One row per arrondissement x year x dwelling type.
-- Medians aren't additive: a yearly median can't be rebuilt from monthly medians,
-- so it's computed here from the sales themselves rather than in the BI tool.
with ventes as (
    select * from {{ ref('int_dvf__ventes_logement') }}
),

arrondissements as (
    select * from {{ ref('arrondissements') }}
)

select
    v.code_commune,
    a.nom                                                       as arrondissement,
    extract(year from v.date_mutation)::int                     as annee,
    v.type_local,
    count(*)                                                    as nb_ventes,
    percentile_cont(0.5) within group (order by v.prix_m2)      as prix_m2_median,
    avg(v.prix_m2)                                              as prix_m2_moyen,
    percentile_cont(0.5) within group (order by v.surface)      as surface_mediane,
    percentile_cont(0.5) within group (order by v.valeur_fonciere) as prix_median
from ventes v
inner join arrondissements a using (code_commune)
group by 1, 2, 3, 4
