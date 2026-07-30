# hybrid_matcher.py
# Objectif : combiner score lexical + sémantique
# pour un meilleur routing des demandes

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import pickle
import os

# ─────────────────────────────────────────
# ÉTAPE 1 : Charger les données
# ─────────────────────────────────────────
df_orgs = pd.read_csv("organisations_enriched.csv")
profils = df_orgs["profil_texte"].fillna("").tolist()
slugs   = df_orgs["slug"].tolist()
noms    = df_orgs["nom"].tolist()

# ─────────────────────────────────────────
# ÉTAPE 2 : Préparer le matcher lexical
# ─────────────────────────────────────────
print("Préparation du matcher lexical...")
vectorizer = TfidfVectorizer(
    analyzer     = "word",
    ngram_range  = (1, 2),
    sublinear_tf = True,
    min_df       = 1
)
matrice_tfidf = vectorizer.fit_transform(profils)
print("✅ Matcher lexical prêt !")

# ─────────────────────────────────────────
# ÉTAPE 3 : Préparer le matcher sémantique
# ─────────────────────────────────────────
print("Chargement du modèle sémantique...")
modele = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

FICHIER_EMBEDDINGS = "embeddings_orgs.pkl"
if os.path.exists(FICHIER_EMBEDDINGS):
    with open(FICHIER_EMBEDDINGS, "rb") as f:
        embeddings_orgs = pickle.load(f)
    print("✅ Embeddings chargés depuis le fichier !")
else:
    print("Calcul des embeddings...")
    embeddings_orgs = modele.encode(profils, show_progress_bar=True)
    with open(FICHIER_EMBEDDINGS, "wb") as f:
        pickle.dump(embeddings_orgs, f)
    print("✅ Embeddings calculés et sauvegardés !")

# ─────────────────────────────────────────
# ÉTAPE 4 : Fonction de fusion hybride
# ─────────────────────────────────────────
def matcher_hybride(demande, top_k=3, poids_lexical=0.65):
    poids_semantique = 1 - poids_lexical

    # Score lexical
    vecteur_tfidf   = vectorizer.transform([demande])
    scores_lexical  = cosine_similarity(vecteur_tfidf, matrice_tfidf)[0]

    # Score sémantique
    embedding_demande  = modele.encode([demande])
    scores_semantique  = cosine_similarity(embedding_demande, embeddings_orgs)[0]

    # Normaliser les scores lexicaux entre 0 et 1
    max_lex = scores_lexical.max()
    if max_lex > 0:
        scores_lexical = scores_lexical / max_lex

    # Fusion hybride
    scores_finaux = (poids_lexical * scores_lexical) + (poids_semantique * scores_semantique)

    # Top-K
    indices_tries = scores_finaux.argsort()[::-1][:top_k]

    resultats = []
    for i in indices_tries:
        resultats.append({
            "slug":            slugs[i],
            "nom":             noms[i],
            "score_final":     round(float(scores_finaux[i]), 4),
            "score_lexical":   round(float(scores_lexical[i]), 4),
            "score_semantique": round(float(scores_semantique[i]), 4)
        })

    return resultats

# ─────────────────────────────────────────
# ÉTAPE 5 : Décision auto_route / manual_review
# ─────────────────────────────────────────
def decider(resultats, seuil_confiance=0.40, seuil_marge=0.03):
    top1 = resultats[0]["score_final"]
    top2 = resultats[1]["score_final"] if len(resultats) > 1 else 0
    marge = top1 - top2

    if top1 >= seuil_confiance and marge >= seuil_marge:
        return "auto_route"
    else:
        return "manual_review"

# ─────────────────────────────────────────
# ÉTAPE 6 : Test
# ─────────────────────────────────────────
demandes_test = [
    "Je veux des données sur les télécommunications au Maroc",
    "Données sur les hôpitaux publics et la santé",
    "Statistiques sur l'agriculture et les céréales",
    "Informations sur les retraites et pensions"
]

print("\n=== TEST DU MATCHER HYBRIDE ===\n")

for demande in demandes_test:
    print(f"Demande : {demande}")
    resultats = matcher_hybride(demande, top_k=3)
    decision  = decider(resultats)

    for rang, r in enumerate(resultats, 1):
        print(f"  {rang}. {r['nom']}")
        print(f"     score final: {r['score_final']} "
              f"(lexical: {r['score_lexical']} | "
              f"sémantique: {r['score_semantique']})")
    print(f"  → Décision : {decision}")
    print()