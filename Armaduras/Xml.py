import os
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET

# =============== CONFIGURAÇÕES ===============
# Pasta onde estão os .xml originais (jogo)
GAME_ENTITIES_FOLDER = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Magic Rampage\entities')

# Pasta onde estão os PNGs das armaduras (principal + subpastas)
ARMOR_PNG_FOLDER = Path(r'C:\Users\Marco\Downloads\Montagem (1)\Armaduras\Png')

# Pasta de destino para os .xml das armaduras
DEST_XML_FOLDER = Path(r'C:\Users\Marco\Downloads\Montagem (1)\Armaduras\Xml')

# =============================================

# Cria a pasta de destino se não existir
DEST_XML_FOLDER.mkdir(parents=True, exist_ok=True)

# Lista todos os PNGs existentes na pasta de armaduras (incluindo subpastas)
print("Escaneando PNGs existentes nas armaduras...")
existing_pngs = set()
for png_path in ARMOR_PNG_FOLDER.rglob('*.png'):
    existing_pngs.add(png_path.name.lower())  # nome em minúsculo para comparação segura

print(f"Encontrados {len(existing_pngs)} PNGs únicos de armadura.\n")

total_copiados = 0
total_ignorados = 0

# Processa todos os .xml na pasta entities
print("Procurando arquivos .xml relevantes...\n")
for xml_path in GAME_ENTITIES_FOLDER.glob('*.xml'):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Pega o imagePath do TextureAtlas
        image_path = root.get('imagePath')
        
        if image_path and image_path.lower().endswith('.png'):
            png_name = Path(image_path).name.lower()
            
            if png_name in existing_pngs:
                dest_xml = DEST_XML_FOLDER / xml_path.name
                
                if not dest_xml.exists():
                    shutil.copy2(xml_path, dest_xml)
                    print(f"Copiado: {xml_path.name} (usa {image_path})")
                    total_copiados += 1
                else:
                    print(f"Já existe: {xml_path.name}")
            else:
                total_ignorados += 1
                # Opcional: descomente a linha abaixo se quiser ver os ignorados
                # print(f"Ignorado: {xml_path.name} → {image_path} não encontrado nas armaduras")
                
    except ET.ParseError:
        print(f"Erro ao ler XML: {xml_path.name}")
    except Exception as e:
        print(f"Erro inesperado em {xml_path.name}: {e}")

print("\n" + "="*60)
print(f"Concluído!")
print(f"XMLs copiados: {total_copiados}")
print(f"XMLs ignorados (PNG não encontrado): {total_ignorados}")
print(f"Todos os XMLs relevantes salvos em:\n{DEST_XML_FOLDER}")