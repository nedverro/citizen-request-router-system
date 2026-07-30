import pandas as pd

df = pd.read_csv("organisations_enriched.csv")

df["longueur_profil"] = df["profil_texte"].fillna("").apply(lambda x: len(x.split()))

print("=== Organisations avec profil le plus PAUVRE ===")
print(df[["slug", "nb_datasets", "longueur_profil"]].sort_values("longueur_profil").head(10).to_string())

print("\n=== Organisations avec profil le plus RICHE ===")
print(df[["slug", "nb_datasets", "longueur_profil"]].sort_values("longueur_profil", ascending=False).head(5).to_string())