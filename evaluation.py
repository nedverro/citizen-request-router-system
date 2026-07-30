# evaluation.py
# Objectif : créer le fichier de labels et évaluer le système
#Partie 1 : créer le fichier feedbacks_eval.csv avec 25 demandes et leurs labels manuels
#Partie 2 : évaluer le système et créer rapport_evaluation.csv

import pandas as pd
import csv

# ─────────────────────────────────────────
# Labels manuels (25 demandes)
# ─────────────────────────────────────────
labels = [
    {"titre": "Etude de l'impact fiscal de l'appréhension des revenus des influenceurs",
     "organisme_correct": "ministere-de-l-economie-et-des-finances"},

    {"titre": "étude de marché de la gestion hôtelière 2025",
     "organisme_correct": "ministere-du-tourisme"},

    {"titre": "Demande d'accès aux données de l'Enquête Panel des ménages de l'ONDH",
     "organisme_correct": "haut-commissariat-au-plan"},

    {"titre": "Jurisprudence",
     "organisme_correct": "ministere-de-la-justice-et-des-libertes"},

    {"titre": "Statistique de nombre de TPE / PME au Maroc",
     "organisme_correct": "ministere-de-l-industrie-du-commerce-de-l-investissement-et-de-l-economie-numerique"},

    {"titre": "Statistiques liées à la consommation d'énergie et à l'éclairage public commune sidi ghanem région essaouira",
     "organisme_correct": "ministere-de-l-equipement-et-de-l-eau"},

    {"titre": "Publication données énergie",
     "organisme_correct": "ministere-de-l-equipement-et-de-l-eau"},

    {"titre": "Demande des données : l'ensembles des écoles supérieures marocaines publics et les filières qui'elles offrent",
     "organisme_correct": "ministere-de-l-enseignement-superieur-de-la-recherche-scientifique-et-de-la-formation-des-cadres"},

    {"titre": "Base données statistiques Dette interieur",
     "organisme_correct": "ministere-de-l-economie-et-des-finances"},

    {"titre": "données de vaccination covid 19",
     "organisme_correct": "ministere-de-la-sante"},

    {"titre": "BD densité de téléphone par region",
     "organisme_correct": "anrt"},

    {"titre": "BD d'assurance santé",
     "organisme_correct": "caisse-nationale-des-organismes-de-prevoyance-sociale"},

    {"titre": "Demande des données concernant les Diabetes",
     "organisme_correct": "ministere-de-la-sante"},

    {"titre": "Demande de données sur le Réseau routier revêtu",
     "organisme_correct": "ministere-de-l-equipement-et-de-l-eau"},

    {"titre": "Données de l'emploi et l'insertion professionnelle",
     "organisme_correct": "ministere-de-l-emploi-et-des-affaires-sociales"},

    {"titre": "Demende des donnees sur la balance de paiments de 2022 et2023",
     "organisme_correct": "ministere-de-l-economie-et-des-finances"},

    {"titre": "Demande de données d'enquête relative au recensement des agriculteurs ayant reçu des aides d'aménagement hydro-agricole. (Donnée au niveau microéconomique)",
     "organisme_correct": "departement-de-l-agriculture"},

    {"titre": "Situation journalière des principaux grands barrages",
     "organisme_correct": "ministere-de-l-equipement-et-de-l-eau"},

    {"titre": "Prix marchés agricoles",
     "organisme_correct": "departement-de-l-agriculture"},

    {"titre": "le taux de chômage et le PIB trimestriel",
     "organisme_correct": "haut-commissariat-au-plan"},

    {"titre": "Liste des universités privées et semi-privée",
     "organisme_correct": "ministere-de-l-enseignement-superieur-de-la-recherche-scientifique-et-de-la-formation-des-cadres"},

    {"titre": "Données ouvertes sur chaque établissement scolaire",
     "organisme_correct": "ministere-de-l-education-nationale-et-de-la-formation-professionnelle"},

    {"titre": "Géolocalisation des centres de soin / cliniques / cabinets des médecins",
     "organisme_correct": "ministere-de-la-sante"},

    {"titre": "DEMANDE LISTES DES MEDECINS MAROC /  TOUTES CATEGORIES",
     "organisme_correct": "ministere-de-la-sante"},

    {"titre": "Base de données relative aux exportations industrielles",
     "organisme_correct": "ministere-de-l-industrie-du-commerce-de-l-investissement-et-de-l-economie-numerique"},
]

# Sauvegarder les labels
df_labels = pd.DataFrame(labels)
df_labels.to_csv("feedbacks_eval.csv", index=False, encoding="utf-8-sig")
print(f"✅ {len(df_labels)} demandes labelisées sauvegardées dans feedbacks_eval.csv")

# ─────────────────────────────────────────
# Évaluation du système
# ─────────────────────────────────────────
from hybrid_matcher import matcher_hybride

print("\nÉvaluation en cours...\n")

top1_correct = 0
top3_correct = 0
total        = len(labels)

resultats_detail = []

for item in labels:
    titre    = item["titre"]
    correct  = item["organisme_correct"]

    # Lancer le matcher
    resultats = matcher_hybride(titre, top_k=3)

    # Vérifier Top-1
    top1_slug = resultats[0]["slug"]
    top1_ok   = (top1_slug == correct)

    # Vérifier Top-3
    top3_slugs = [r["slug"] for r in resultats]
    top3_ok    = (correct in top3_slugs)

    if top1_ok:
        top1_correct += 1
    if top3_ok:
        top3_correct += 1

    resultats_detail.append({
        "titre":            titre[:50],
        "organisme_correct": correct,
        "top1_predit":      top1_slug,
        "top1_ok":          "✅" if top1_ok else "❌",
        "top3_ok":          "✅" if top3_ok else "❌",
        "score":            resultats[0]["score_final"]
    })

    print(f"{'✅' if top1_ok else '❌'} {titre[:50]}")
    print(f"   Prédit : {top1_slug}")
    print(f"   Correct: {correct}\n")

# ─────────────────────────────────────────
# Résultats finaux
# ─────────────────────────────────────────
top1_accuracy = (top1_correct / total) * 100
top3_accuracy = (top3_correct / total) * 100

print("=" * 50)
print(f"RÉSULTATS D'ÉVALUATION")
print("=" * 50)
print(f"Total demandes testées : {total}")
print(f"Top-1 Accuracy         : {top1_correct}/{total} = {top1_accuracy:.1f}%")
print(f"Top-3 Accuracy         : {top3_correct}/{total} = {top3_accuracy:.1f}%")
print("=" * 50)

# Sauvegarder le rapport
df_rapport = pd.DataFrame(resultats_detail)
df_rapport.to_csv("rapport_evaluation.csv", index=False, encoding="utf-8-sig")
print(f"\n✅ Rapport détaillé sauvegardé dans rapport_evaluation.csv")