-- One row per Lyon IRIS x rooms x construction period x furnished, typed.
-- The source stores the reference rents as a JSON tree; this flattens it.
with source as (
    select
        codeiris,
        zonage,
        insee,
        valeurs::jsonb as valeurs,
        replace(replace(_source_file, 'encadrement_', ''), '.csv', '') as periode
    from {{ source('raw', 'encadrement_loyers') }}
    where insee between '69381' and '69389'
)

select
    s.codeiris                                          as code_iris,
    s.insee                                             as code_commune,
    s.periode,
    s.zonage::int                                       as zone,
    pieces.key                                          as nb_pieces,
    epoque.key                                          as epoque_construction,
    meuble.key = 'meuble'                               as est_meuble,
    (meuble.value ->> 'loyer_reference')::numeric        as loyer_reference_m2,
    (meuble.value ->> 'loyer_reference_majore')::numeric as loyer_reference_majore_m2,
    (meuble.value ->> 'loyer_reference_minore')::numeric as loyer_reference_minore_m2
from source s
cross join lateral jsonb_each(s.valeurs) as pieces
cross join lateral jsonb_each(pieces.value) as epoque
cross join lateral jsonb_each(epoque.value) as meuble
