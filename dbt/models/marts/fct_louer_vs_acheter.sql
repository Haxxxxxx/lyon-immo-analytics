-- Buy vs rent by arrondissement: how many years of rent an apartment's purchase price is
-- worth. Joins the latest DVF year with the latest ANIL rents, both per m².
-- The rent includes charges, so the yield is slightly flattering (gross, before charges).
with prix as (
    select code_commune, annee, prix_m2_median
    from {{ ref('fct_prix_m2_annuel') }}
    where type_local = 'Appartement'
      and annee = (select max(annee) from {{ ref('fct_prix_m2_annuel') }})
),

loyers as (
    select code_commune, millesime, loyer_m2_cc
    from {{ ref('fct_loyers_arrondissement') }}
    where segment = 'tous'
)

select
    p.code_commune,
    a.nom                                                   as arrondissement,
    p.annee                                                 as annee_prix,
    l.millesime                                             as millesime_loyer,
    round(p.prix_m2_median::numeric)                        as prix_m2_median,
    l.loyer_m2_cc,
    round(p.prix_m2_median::numeric / (l.loyer_m2_cc * 12), 1) as annees_de_loyer,
    round(l.loyer_m2_cc * 12 * 100 / p.prix_m2_median::numeric, 2) as rendement_brut_pct
from prix p
inner join loyers l using (code_commune)
inner join {{ ref('arrondissements') }} a using (code_commune)
