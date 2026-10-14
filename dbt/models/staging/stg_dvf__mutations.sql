-- One row per raw DVF line, Lyon only, typed. No business logic here.
select
    id_mutation,
    date_mutation::date                         as date_mutation,
    nature_mutation,
    nullif(valeur_fonciere, '')::numeric        as valeur_fonciere,
    code_commune,
    nullif(type_local, '')                      as type_local,
    nullif(surface_reelle_bati, '')::numeric    as surface_reelle_bati,
    nullif(nombre_pieces_principales, '')::int  as nb_pieces,
    nullif(longitude, '')::numeric              as longitude,
    nullif(latitude, '')::numeric               as latitude
from {{ source('raw', 'dvf') }}
where code_commune between '69381' and '69389'
