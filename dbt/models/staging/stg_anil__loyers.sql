-- One row per Lyon arrondissement x listing segment, typed.
-- Segment and edition come from the file name: carte_loyers_<year>_<segment>.csv
select
    "INSEE_C"                                                   as code_commune,
    split_part(_source_file, '_', 3)::int                       as millesime,
    case replace(split_part(_source_file, '_', 4), '.csv', '')
        when 'app'   then 'tous'
        when 'app12' then 't1_t2'
        when 'app3'  then 't3_plus'
    end                                                         as segment,
    replace(loypredm2, ',', '.')::numeric                       as loyer_m2_cc,
    replace("lwr.IPm2", ',', '.')::numeric                      as loyer_m2_cc_bas,
    replace("upr.IPm2", ',', '.')::numeric                      as loyer_m2_cc_haut,
    "TYPPRED"                                                   as niveau_prediction,
    nbobs_com::int                                              as nb_annonces,
    replace("R2_adj", ',', '.')::numeric                        as r2_ajuste
from {{ source('raw', 'carte_loyers') }}
where "INSEE_C" between '69381' and '69389'
