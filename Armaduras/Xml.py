import os
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET

# =============== CONFIGURAÇÕES ===============
GAME_ENTITIES_FOLDER = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Magic Rampage\entities')
ARMOR_PNG_FOLDER = Path(r'C:\Users\Marco\Downloads\Montagem (1)\Armaduras\Png')
DEST_XML_FOLDER = Path(r'C:\Users\Marco\Downloads\Montagem (1)\Armaduras\Xml')
# =============================================

DEST_XML_FOLDER.mkdir(parents=True, exist_ok=True)

# Escaneia todos os PNGs (incluindo subpastas) e cria conjuntos de nomes
print("Escaneando PNGs existentes nas armaduras...")
existing_png_names = set()          # nomes completos (ex: armor_gatekeeper.png)
existing_png_stems = set()          # nomes sem extensão (ex: armor_gatekeeper)

for png_path in ARMOR_PNG_FOLDER.rglob('*.png'):
    existing_png_names.add(png_path.name.lower())
    existing_png_stems.add(png_path.stem.lower())  # stem = nome sem extensão

print(f"Encontrados {len(existing_png_names)} PNGs únicos de armadura.\n")

total_copiados = 0
total_ignorados = 0
copiados_por_imagepath = 0
copiados_por_nome = 0

print("Procurando arquivos .xml relevantes...\n")
for xml_path in GAME_ENTITIES_FOLDER.glob('*.xml'):
    try:
        deve_copiar = False
        motivo = ""

        # Critério 1: Verifica pelo imagePath (como antes)
        tree = ET.parse(xml_path)
        root = tree.getroot()
        image_path = root.get('imagePath')
        
        if image_path and image_path.lower().endswith('.png'):
            png_name = Path(image_path).name.lower()
            if png_name in existing_png_names:
                deve_copiar = True
                motivo = f"usa {image_path}"
                copiados_por_imagepath += 1

        # Critério 2: Se não achou pelo imagePath, verifica se o nome do XML (sem .xml) 
        # corresponde ao nome de algum PNG (sem .png)
        if not deve_copiar:
            xml_stem = xml_path.stem.lower()
            if xml_stem in existing_png_stems:
                deve_copiar = True
                motivo = f"nome corresponde ao PNG {xml_stem}.png"
                copiados_por_nome += 1

        # Se atender qualquer um dos critérios, copia
        if deve_copiar:
            dest_xml = DEST_XML_FOLDER / xml_path.name
            if not dest_xml.exists():
                shutil.copy2(xml_path, dest_xml)
                print(f"Copiado: {xml_path.name} ({motivo})")
                total_copiados += 1
            else:
                print(f"Já existe: {xml_path.name} ({motivo})")
        else:
            total_ignorados += 1

    except ET.ParseError:
        print(f"Erro ao ler XML: {xml_path.name}")
    except Exception as e:
        print(f"Erro inesperado em {xml_path.name}: {e}")

print("\n" + "="*60)
print(f"Concluído!")
print(f"XMLs copiados no total: {total_copiados}")
print(f"   • Por referência no imagePath: {copiados_por_imagepath}")
print(f"   • Por correspondência de nome: {copiados_por_nome}")
print(f"XMLs ignorados: {total_ignorados}")
print(f"Todos os XMLs relevantes salvos em:\n{DEST_XML_FOLDER}")