# Sales market overview: price per m² and volumes from DVF.
from .spec import bar_viz, card, col, columns, place, text

LATEST_YEAR = "(select max(annee) from marts.fct_prix_m2_annuel)"

prix_par_arrondissement = card(
    "Prix médian au m² par arrondissement (appartements, dernière année)",
    "row",
    f"""
select arrondissement, round(prix_m2_median) as prix_m2_median, nb_ventes
from marts.fct_prix_m2_annuel
where type_local = 'Appartement' and annee = {LATEST_YEAR}
order by prix_m2_median desc""",
    bar_viz("arrondissement", "prix_m2_median", "Arrondissement", "Prix médian (€/m²)",
            title="Prix médian", suffix=" €/m²"),
)

evolution_prix = card(
    "Évolution du prix médian au m² (appartements)",
    "line",
    """
select make_date(annee, 1, 1) as annee, arrondissement, round(prix_m2_median) as prix_m2_median
from marts.fct_prix_m2_annuel
where type_local = 'Appartement'
order by annee, arrondissement""",
    {
        "graph.dimensions": ["annee", "arrondissement"],
        "graph.metrics": ["prix_m2_median"],
        "graph.x_axis.title_text": "Année",
        "graph.y_axis.title_text": "Prix médian (€/m²)",
        **columns(prix_m2_median=col("Prix médian", " €/m²")),
    },
)

volume_mensuel = card(
    "Volume mensuel de ventes (logements)",
    "bar",
    """
select mois, sum(nb_ventes) as nb_ventes
from marts.fct_prix_m2_mensuel
group by mois
order by mois""",
    {
        "graph.dimensions": ["mois"],
        "graph.metrics": ["nb_ventes"],
        "graph.x_axis.title_text": "Mois",
        "graph.y_axis.title_text": "Nombre de ventes",
        **columns(nb_ventes=col("Ventes")),
    },
)

comparaison_types = card(
    "Appartements vs maisons (dernière année)",
    "table",
    f"""
select
    arrondissement,
    max(nb_ventes)                    filter (where type_local = 'Appartement') as ventes_appartements,
    round(max(prix_m2_median) filter (where type_local = 'Appartement'))         as prix_m2_appartement,
    round(max(surface_mediane) filter (where type_local = 'Appartement'))        as surface_appartement,
    coalesce(max(nb_ventes)           filter (where type_local = 'Maison'), 0)  as ventes_maisons,
    round(max(prix_m2_median) filter (where type_local = 'Maison'))              as prix_m2_maison,
    round(max(surface_mediane) filter (where type_local = 'Maison'))             as surface_maison
from marts.fct_prix_m2_annuel
where annee = {LATEST_YEAR}
group by code_commune, arrondissement
order by code_commune""",
    columns(
        arrondissement=col("Arrondissement"),
        ventes_appartements=col("Ventes appartements"),
        prix_m2_appartement=col("Prix médian appartement", " €/m²"),
        surface_appartement=col("Surface médiane appartement", " m²"),
        ventes_maisons=col("Ventes maisons"),
        prix_m2_maison=col("Prix médian maison", " €/m²"),
        surface_maison=col("Surface médiane maison", " m²"),
    ),
)

INSIGHT = text("""
## Ce qu'il faut retenir

**Le marché lyonnais s'est corrigé après la hausse des taux.** Le volume de ventes de logements a chuté de **29 %** entre 2021 et 2024 (8 266 → 5 894 ventes), et le prix médian des appartements a reculé d'environ **12 %** entre 2022 et 2025 (5 088 → 4 471 €/m²). 2025 montre une reprise des volumes (+16 %) sans remontée des prix.

**Lyon 6e reste l'arrondissement le plus cher** (≈ 5 470 €/m² en 2025, +22 % vs la médiane de la ville), Lyon 5e et 9e les plus accessibles (≈ 3 700 €/m²).

*Source : DVF géolocalisées 2021–2025 (Etalab). Ventes contenant un seul logement, hors VEFA ; ~1 % de prix aberrants exclus. Médianes, pas moyennes.*
""")

DASHBOARD = {
    "name": "1. Marché de la vente à Lyon",
    "description": "Prix au m² et volumes de ventes par arrondissement, DVF 2021–2025.",
    "parameters": [],
    "layout": [
        place(INSIGHT, 0, 0, 24, 7),
        place(prix_par_arrondissement, 7, 0, 12, 9),
        place(evolution_prix, 7, 12, 12, 9),
        place(volume_mensuel, 16, 0, 24, 7),
        place(comparaison_types, 23, 0, 24, 7),
    ],
}
