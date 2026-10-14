-- Rent control caps a listing must respect, by arrondissement, zone, rooms, construction
-- period and furnished or not. Rents are per m² and EXCLUDE charges.
select
    p.code_commune,
    a.nom                                   as arrondissement,
    p.periode,
    p.zone,
    p.nb_pieces,
    p.epoque_construction,
    p.est_meuble,
    case when p.est_meuble then 'Meublé' else 'Non meublé' end as meuble,
    p.loyer_reference_m2,
    p.loyer_reference_majore_m2              as loyer_max_m2,
    p.loyer_reference_minore_m2              as loyer_min_m2,
    p.nb_iris
from {{ ref('int_encadrement__plafonds_zone') }} p
inner join {{ ref('arrondissements') }} a using (code_commune)
