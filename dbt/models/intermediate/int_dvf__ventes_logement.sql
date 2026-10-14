-- One row per sale (id_mutation) containing exactly one dwelling.
--
-- DVF spreads a sale over several rows (one per lot or parcel) and repeats the total
-- price on each. Averaging rows naively would count one price several times, so we
-- collapse to one row per sale and keep only sales whose price belongs to one dwelling:
--   - 'Vente' only (excludes off-plan VEFA, exchanges, auctions, expropriations)
--   - exactly one distinct dwelling: a house on two parcels appears on two identical
--     rows, so we count distinct (type, surface, rooms) rather than rows
--   - no commercial premises in the sale (the price would include the shop)
--   - outbuildings (garage, cellar, parking) and land are allowed: they come with the dwelling
--   - a price and a positive built surface
--   - a plausible price per m² (vars prix_m2_min / prix_m2_max): drops ~1% of sales,
--     mostly symbolic prices (1 €, family transfers, viager) and surface/price mismatches

with ventes as (
    select *
    from {{ ref('stg_dvf__mutations') }}
    where nature_mutation = 'Vente'
),

par_vente as (
    select
        id_mutation,
        max(valeur_fonciere) as valeur_fonciere  -- identical on every row of a sale
    from ventes
    group by id_mutation
    having
        count(distinct (type_local, surface_reelle_bati, nb_pieces))
            filter (where type_local in ('Appartement', 'Maison')) = 1
        and count(*) filter (where type_local like 'Local%') = 0
),

-- Date, commune and surface come from the dwelling row itself:
-- a sale's parcels can straddle two arrondissements.
logement as (
    select distinct on (id_mutation)
        id_mutation,
        date_mutation,
        code_commune,
        type_local,
        surface_reelle_bati as surface,
        nb_pieces,
        longitude,
        latitude
    from ventes
    where type_local in ('Appartement', 'Maison')
    order by id_mutation, date_mutation
),

ventes_logement as (
    select
        l.id_mutation,
        l.date_mutation,
        l.code_commune,
        l.type_local,
        l.surface,
        l.nb_pieces,
        v.valeur_fonciere,
        round(v.valeur_fonciere / l.surface, 2) as prix_m2,
        l.longitude,
        l.latitude
    from par_vente v
    inner join logement l using (id_mutation)
    where v.valeur_fonciere > 0
      and l.surface > 0
)

select *
from ventes_logement
where prix_m2 between {{ var('prix_m2_min') }} and {{ var('prix_m2_max') }}
