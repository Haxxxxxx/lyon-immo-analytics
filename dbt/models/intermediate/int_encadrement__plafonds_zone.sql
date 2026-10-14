-- One row per arrondissement x rent control zone x rooms x construction period x furnished.
-- Reference rents are set per zone; every IRIS of a zone repeats them. Grouping by the
-- values too means the grain test fails if two IRIS of one zone ever disagree.
select
    code_commune,
    periode,
    zone,
    nb_pieces,
    epoque_construction,
    est_meuble,
    loyer_reference_m2,
    loyer_reference_majore_m2,
    loyer_reference_minore_m2,
    count(*) as nb_iris
from {{ ref('stg_grandlyon__encadrement') }}
group by 1, 2, 3, 4, 5, 6, 7, 8, 9
