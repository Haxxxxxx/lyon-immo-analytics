-- Rent control: minimum <= reference <= maximum, all positive.
select *
from {{ ref('dim_plafonds_loyer') }}
where not (0 < loyer_min_m2 and loyer_min_m2 <= loyer_reference_m2
           and loyer_reference_m2 <= loyer_max_m2)
