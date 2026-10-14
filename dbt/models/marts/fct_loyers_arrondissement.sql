-- Market rent per arrondissement and apartment segment, latest ANIL edition.
-- Charges included, unfurnished. loyer_type is the monthly rent of the reference surface
-- the indicator was modelled for (37 m² for T1-T2, 72 m² for T3+).
with loyers as (
    select * from {{ ref('stg_anil__loyers') }}
    where millesime = (select max(millesime) from {{ ref('stg_anil__loyers') }})
)

select
    l.code_commune,
    a.nom                                               as arrondissement,
    l.millesime,
    l.segment,
    s.libelle                                           as segment_libelle,
    l.loyer_m2_cc,
    l.loyer_m2_cc_bas,
    l.loyer_m2_cc_haut,
    s.surface_reference_m2,
    round(l.loyer_m2_cc * s.surface_reference_m2)       as loyer_type_mensuel_cc,
    l.nb_annonces,
    l.r2_ajuste
from loyers l
inner join {{ ref('arrondissements') }} a using (code_commune)
inner join {{ ref('segments_loyer') }} s using (segment)
