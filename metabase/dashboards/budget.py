# Renting on a budget: how much space a monthly budget buys, solo or in a flatshare.
from .spec import bar_viz, card, col, columns, number_param, place, text

LOYERS = "marts.fct_loyers_arrondissement"

surface_solo = card(
    "Solo : surface louable avec mon budget (T1-T2)",
    "row",
    f"""
select arrondissement, round({{{{budget_solo}}}} / loyer_m2_cc) as surface_m2
from {LOYERS}
where segment = 't1_t2'
order by surface_m2 desc, arrondissement""",
    bar_viz("arrondissement", "surface_m2", "Arrondissement", "Surface (m²)",
            title="Surface", suffix=" m²"),
)

surface_coloc = card(
    "Colocation : m² par personne avec notre budget (T3 et plus)",
    "row",
    f"""
select arrondissement,
       round({{{{budget_coloc}}}} / loyer_m2_cc / {{{{nb_colocataires}}}}) as m2_par_personne
from {LOYERS}
where segment = 't3_plus'
order by m2_par_personne desc, arrondissement""",
    bar_viz("arrondissement", "m2_par_personne", "Arrondissement", "Surface par personne (m²)",
            title="Par personne", suffix=" m²"),
)

solo_vs_coloc = card(
    "Solo ou colocation ? Comparaison par arrondissement",
    "table",
    f"""
select
    s.arrondissement,
    round({{{{budget_solo}}}} / s.loyer_m2_cc)                                as surface_solo,
    {{{{budget_solo}}}}                                                       as loyer_solo,
    round({{{{budget_coloc}}}} / c.loyer_m2_cc)                               as surface_coloc,
    round({{{{budget_coloc}}}} / c.loyer_m2_cc / {{{{nb_colocataires}}}})     as m2_par_personne,
    round({{{{budget_coloc}}}}::numeric / {{{{nb_colocataires}}}})            as loyer_par_personne,
    round(100 * ((({{{{budget_coloc}}}} / c.loyer_m2_cc / {{{{nb_colocataires}}}}))
                 / ({{{{budget_solo}}}} / s.loyer_m2_cc) - 1))               as gain_m2_pct
from {LOYERS} s
inner join {LOYERS} c on c.code_commune = s.code_commune and c.segment = 't3_plus'
where s.segment = 't1_t2'
order by s.code_commune""",
    columns(
        arrondissement=col("Arrondissement"),
        surface_solo=col("Solo : surface", " m²"),
        loyer_solo=col("Solo : loyer", " €"),
        surface_coloc=col("Coloc : surface totale", " m²"),
        m2_par_personne=col("Coloc : m² / personne", " m²"),
        loyer_par_personne=col("Coloc : loyer / personne", " €"),
        gain_m2_pct=col("Espace gagné en coloc", " %"),
    ),
)

loyers_marche = card(
    "Loyers de marché par arrondissement (charges comprises, non meublé)",
    "table",
    f"""
select
    s.arrondissement,
    s.loyer_m2_cc                                   as t1_t2_m2,
    s.loyer_m2_cc_bas || ' – ' || s.loyer_m2_cc_haut as t1_t2_fourchette,
    s.loyer_type_mensuel_cc                         as t1_t2_loyer_37m2,
    c.loyer_m2_cc                                   as t3_m2,
    c.loyer_m2_cc_bas || ' – ' || c.loyer_m2_cc_haut as t3_fourchette,
    c.loyer_type_mensuel_cc                         as t3_loyer_72m2,
    s.nb_annonces + c.nb_annonces                   as nb_annonces
from (select arrondissement, code_commune, round(loyer_m2_cc, 1) as loyer_m2_cc,
             round(loyer_m2_cc_bas, 1) as loyer_m2_cc_bas, round(loyer_m2_cc_haut, 1) as loyer_m2_cc_haut,
             loyer_type_mensuel_cc, nb_annonces
      from {LOYERS} where segment = 't1_t2') s
inner join (select code_commune, round(loyer_m2_cc, 1) as loyer_m2_cc,
                   round(loyer_m2_cc_bas, 1) as loyer_m2_cc_bas, round(loyer_m2_cc_haut, 1) as loyer_m2_cc_haut,
                   loyer_type_mensuel_cc, nb_annonces
            from {LOYERS} where segment = 't3_plus') c using (code_commune)
order by s.code_commune""",
    columns(
        arrondissement=col("Arrondissement"),
        t1_t2_m2=col("T1-T2", " €/m²", decimals=1),
        t1_t2_fourchette=col("T1-T2 fourchette 95 % (€/m²)"),
        t1_t2_loyer_37m2=col("T1-T2 de 37 m²", " €/mois"),
        t3_m2=col("T3+", " €/m²", decimals=1),
        t3_fourchette=col("T3+ fourchette 95 % (€/m²)"),
        t3_loyer_72m2=col("T3+ de 72 m²", " €/mois"),
        nb_annonces=col("Annonces analysées"),
    ),
)

INTRO = text("""
## Louer à Lyon : que permet mon budget ?

Change les filtres en haut (budget solo, budget colocation, nombre de colocataires) : tout le tableau de bord se recalcule.

**Avec 600 €/mois seul**, on loue **30 à 33 m²** quel que soit l'arrondissement : les loyers des petites surfaces varient peu dans Lyon (18,4 à 20,3 €/m²), alors que les prix de vente varient de près de 50 %. **Choisis le quartier, pas le prix.**
**En colocation à deux avec 1 400 €**, on a **42 à 49 m² par personne**, soit environ **+45 % d'espace** pour 100 € de plus chacun.
**Un meublé coûte environ 13 % de plus** (d'après les loyers de référence de l'encadrement).

*Loyers d'annonce charges comprises, logements non meublés, 3e trimestre 2025. Ce sont des estimations par modèle : une annonce réelle peut s'écarter de la fourchette. Source : Estimations ANIL, à partir des données du Groupe SeLoger et de leboncoin.*
""")

DASHBOARD = {
    "name": "2. Louer à Lyon : mon budget",
    "description": "Surface louable par arrondissement pour un budget mensuel, seul ou en colocation.",
    "parameters": [
        number_param("budget_solo", "Budget solo (€/mois, charges comprises)", 600),
        number_param("budget_coloc", "Budget colocation total (€/mois)", 1400),
        number_param("nb_colocataires", "Nombre de colocataires", 2),
    ],
    "layout": [
        place(INTRO, 0, 0, 24, 6),
        place(surface_solo, 6, 0, 12, 8),
        place(surface_coloc, 6, 12, 12, 8),
        place(solo_vs_coloc, 14, 0, 24, 7),
        place(loyers_marche, 21, 0, 24, 7),
    ],
}
