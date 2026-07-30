# matcher.py
# Objectif : calculer le score lexical (TF-IDF) entre une demande
# et les profils des organisations, puis retourner le top-K

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ─────────────────────────────────────────
# ÉTAPE 1 : Charger les données
# ─────────────────────────────────────────
df_orgs = pd.read_csv("organisations_enriched.csv")
profils = df_orgs["profil_texte"].fillna("").tolist()
slugs   = df_orgs["slug"].tolist()
noms    = df_orgs["nom"].tolist()

# ─────────────────────────────────────────
# ÉTAPE 2 : Construire la matrice TF-IDF
# ─────────────────────────────────────────
vectorizer = TfidfVectorizer(
    analyzer   = "word",       # découper par mots
    ngram_range = (1, 2),      # unigrammes + bigrammes
    sublinear_tf = True,       # log(TF) au lieu de TF brut
    min_df      = 1            # garder tous les mots
)

# On vectorise les profils des organisations
matrice_orgs = vectorizer.fit_transform(profils)

# ─────────────────────────────────────────
# ÉTAPE 3 : Fonction de matching
# ─────────────────────────────────────────
def matcher_lexical(demande, top_k=3):
    # Vectoriser la demande avec le même vectorizer
    vecteur_demande = vectorizer.transform([demande])
    
    # Calculer la similarité cosinus entre la demande et chaque profil
    scores = cosine_similarity(vecteur_demande, matrice_orgs)[0]
    
    # Trier par score décroissant et prendre les top_k
    indices_tries = scores.argsort()[::-1][:top_k]
    
    # Construire le résultat
    resultats = []
    for i in indices_tries:
        resultats.append({
            "slug":  slugs[i],
            "nom":   noms[i],
            "score": round(float(scores[i]), 4)
        })
    
    return resultats

# ─────────────────────────────────────────
# ÉTAPE 4 : Tester avec des demandes réelles
# ─────────────────────────────────────────
demandes_test = [
    "Je veux des données sur les télécommunications au Maroc",
    "Données sur les hôpitaux publics et la santé",
    "Statistiques sur l'agriculture et les céréales",
    "Informations sur les retraites et pensions"
]

print("=== TEST DU MATCHER LEXICAL ===\n")

for demande in demandes_test:
    print(f"Demande : {demande}")
    resultats = matcher_lexical(demande, top_k=3)
    for rang, r in enumerate(resultats, 1):
        print(f"  {rang}. {r['nom']} [{r['slug']}] → score: {r['score']}")
    print()