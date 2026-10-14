# Check a listing against Lyon's rent control caps (encadrement des loyers).
from .spec import ARRONDISSEMENTS, card, col, columns, list_param, number_param, place, text

PLAFONDS = "marts.dim_plafonds_loyer"

# Optional filters: when epoque or arrondissement is left empty, every value is kept
FILTRES = f"""
from {PLAFONDS}
where nb_pieces = {{{{nb_pieces}}}}
  and meuble = {{{{meuble}}}}
  [[and arrondissement = {{{{arrondissement}}}}]]
  [[and epoque_construction = {{{{epoque}}}}]]"""

verdict = card(
    "Verdict : ce loyer respecte-t-il l'encadrement ?",
    "table",
    f"""
with plafonds as (
    select code_commune, arrondissement,
           min(loyer_max_m2) as plafond_m2_bas,
           max(loyer_max_m2) as plafond_m2_haut
    {FILTRES}
    group by code_commune, arrondissement
)

select
    arrondissement,
    round({{{{loyer_hc}}}}::numeric / {{{{surface}}}}, 1)               as loyer_annonce_m2,
    round(plafond_m2_bas * {{{{surface}}}})                             as loyer_max_bas,
    round(plafond_m2_haut * {{{{surface}}}})                            as loyer_max_haut,
    case
        when {{{{loyer_hc}}}} <= plafond_m2_bas * {{{{surface}}}} then '✅ Légal dans toutes les zones'
        when {{{{loyer_hc}}}} > plafond_m2_haut * {{{{surface}}}} then '❌ Au-dessus du plafond partout'
        else '⚠️ Dépend de la zone et de l''époque de construction'
    end                                                                 as verdict,
    greatest(0, round({{{{loyer_hc}}}} - plafond_m2_haut * {{{{surface}}}})) as depassement_mensuel_min
from plafonds
order by code_commune""",
    columns(
        arrondissement=col("Arrondissement"),
        loyer_annonce_m2=col("Loyer de l'annonce", " €/m²", decimals=1),
        loyer_max_bas=col("Loyer max légal (zone la moins chère)", " €"),
        loyer_max_haut=col("Loyer max légal (zone la plus chère)", " €"),
        verdict=col("Verdict"),
        depassement_mensuel_min=col("Dépassement certain", " €/mois"),
    ),
)

plafonds_detail = card(
    "Plafonds détaillés par zone et époque de construction",
    "table",
    f"""
select
    arrondissement,
    'Zone ' || zone                                     as zone,
    epoque_construction,
    loyer_reference_m2,
    loyer_max_m2,
    round(loyer_max_m2 * {{{{surface}}}})               as loyer_max_pour_ma_surface
{FILTRES}
order by code_commune, zone,
    case epoque_construction
        when 'avant 1946' then 1 when '1946-1970' then 2 when '1971-1990' then 3
        when '1991-2005' then 4 else 5
    end""",
    columns(
        arrondissement=col("Arrondissement"),
        zone=col("Zone"),
        epoque_construction=col("Construit"),
        loyer_reference_m2=col("Loyer de référence", " €/m²", decimals=1),
        loyer_max_m2=col("Loyer max (référence + 20 %)", " €/m²", decimals=1),
        loyer_max_pour_ma_surface=col("Loyer max pour ma surface", " €/mois"),
    ),
)

MODE_EMPLOI = text("""
## Vérifier une annonce

Depuis novembre 2021, les loyers de Lyon sont **encadrés** : un loyer **hors charges** ne peut pas dépasser le **loyer de référence majoré** (référence + 20 %), qui dépend de la zone, du nombre de pièces, de l'époque de construction et du meublé.

**Mode d'emploi :** renseigne en haut le **loyer hors charges** (pas charges comprises !), la **surface**, le **nombre de pièces** et **meublé ou non**. Si tu connais l'arrondissement et l'année de construction, ajoute-les : le verdict devient plus précis. Chaque arrondissement contient plusieurs zones ; pour connaître la zone exacte d'une adresse, utilise la carte officielle de la Métropole de Lyon.

**Si le loyer dépasse le plafond :** le propriétaire ne peut le justifier que par un *complément de loyer* pour des caractéristiques exceptionnelles, qui doit figurer dans le bail. Sinon, le locataire peut demander une mise en conformité. Le bail doit aussi mentionner le loyer de référence.

*Plafonds 2025–2026 (en vigueur jusqu'à la publication de la période suivante). Source : Métropole de Lyon, data.grandlyon.com. Cet outil donne une indication, pas un avis juridique.*
""")

DASHBOARD = {
    "name": "3. Vérifier une annonce (encadrement des loyers)",
    "description": "Compare le loyer d'une annonce aux plafonds légaux de l'encadrement des loyers à Lyon.",
    "parameters": [
        number_param("loyer_hc", "Loyer hors charges (€/mois)", 550),
        number_param("surface", "Surface (m²)", 25),
        list_param("nb_pieces", "Nombre de pièces", ["1", "2", "3", "4 et plus"], "1"),
        list_param("meuble", "Meublé ?", ["Meublé", "Non meublé"], "Meublé"),
        list_param("arrondissement", "Arrondissement (facultatif)", ARRONDISSEMENTS),
        list_param("epoque", "Construit (facultatif)",
                   ["avant 1946", "1946-1970", "1971-1990", "1991-2005", "après 2005"]),
    ],
    "layout": [
        place(MODE_EMPLOI, 0, 0, 24, 7),
        place(verdict, 7, 0, 24, 7),
        place(plafonds_detail, 14, 0, 24, 9),
    ],
}
