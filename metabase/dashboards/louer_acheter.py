# Buy vs rent: price-to-rent ratio, joining DVF sale prices with ANIL rents.
from .spec import bar_viz, card, col, columns, place, text

ratio = card(
    "Combien d'années de loyer pour acheter le même appartement ?",
    "row",
    """
select arrondissement, annees_de_loyer
from marts.fct_louer_vs_acheter
order by annees_de_loyer desc""",
    bar_viz("arrondissement", "annees_de_loyer", "Arrondissement", "Années de loyer",
            title="Années de loyer", suffix=" ans", decimals=1),
)

detail = card(
    "Prix d'achat vs loyer par arrondissement",
    "table",
    """
select arrondissement, prix_m2_median, loyer_m2_cc, annees_de_loyer, rendement_brut_pct
from marts.fct_louer_vs_acheter
order by code_commune""",
    columns(
        arrondissement=col("Arrondissement"),
        prix_m2_median=col("Prix d'achat médian", " €/m²"),
        loyer_m2_cc=col("Loyer mensuel", " €/m²", decimals=1),
        annees_de_loyer=col("Années de loyer", " ans", decimals=1),
        rendement_brut_pct=col("Rendement locatif brut", " %", decimals=1),
    ),
)

INSIGHT = text("""
## Louer ou acheter ?

Le **ratio prix / loyer** compare le prix d'achat médian d'un appartement au loyer annuel de la même surface. Plus il est élevé, plus louer est avantageux par rapport à acheter.

À Lyon, acheter coûte **19 à 26 ans de loyer** selon l'arrondissement. **Lyon 6e** est le plus cher à l'achat par rapport à ses loyers (≈ 26 ans) ; **Lyon 5e et 9e** sont les plus favorables à l'achat (≈ 19–20 ans, rendement brut ≈ 5 %). Les loyers varient peu d'un arrondissement à l'autre, alors que les prix de vente varient beaucoup : c'est le prix qui fait le ratio.

*Prix : médiane DVF des appartements, dernière année disponible. Loyers : ANIL, charges comprises (le rendement brut est donc légèrement surestimé). Hors frais de notaire, crédit et charges de copropriété.*
""")

DASHBOARD = {
    "name": "4. Louer ou acheter ?",
    "description": "Ratio prix d'achat / loyer annuel par arrondissement (DVF × Carte des loyers).",
    "parameters": [],
    "layout": [
        place(INSIGHT, 0, 0, 24, 5),
        place(ratio, 5, 0, 12, 9),
        place(detail, 5, 12, 12, 9),
    ],
}
