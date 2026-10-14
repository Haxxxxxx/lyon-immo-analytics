-- Reference rents must be identical across all IRIS of a zone within an arrondissement.
select code_commune, periode, zone, nb_pieces, epoque_construction, est_meuble, count(*) as n
from {{ ref('int_encadrement__plafonds_zone') }}
group by 1, 2, 3, 4, 5, 6
having count(*) > 1
