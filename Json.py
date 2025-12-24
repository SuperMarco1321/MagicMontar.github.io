import os
import json

# Pastas principais (ajuste se mudar o nome)
categorias = {
    "body": "Corpo",
    "armor": "Armaduras",
    "amuleto": "Amuleto",
    "pet": "Pet",
    "head": "Cabeça",
    "eye": "Olho",
    "weapon": "Arma/Png"  # arma é só PNG, sem Xml
}

catalog = {}

for key, pasta in categorias.items():
    png_path = os.path.join(pasta, "Png")
    itens = []
    if os.path.exists(png_path):
        for arquivo in os.listdir(png_path):
            if arquivo.lower().endswith(".png"):
                nome = os.path.splitext(arquivo)[0]  # remove .png
                itens.append(nome)
        itens.sort()  # ordem alfabética
    catalog[key] = itens

# Salva o JSON
with open("catalog.json", "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=4, ensure_ascii=False)

print("catalog.json gerado com sucesso!")
print(f"Itens encontrados:")
for cat, lista in catalog.items():
    print(f"  {cat}: {len(lista)} itens")