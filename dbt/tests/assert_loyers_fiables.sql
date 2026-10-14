-- ANIL's guide: treat an indicator with caution when the adjusted R² is under 0.5 or the
-- commune has fewer than 30 listings. Every Lyon arrondissement must clear both bars.
select *
from {{ ref('fct_loyers_arrondissement') }}
where r2_ajuste < 0.5 or nb_annonces < 30
