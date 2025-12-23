import shutil
from pathlib import Path

# =============== CONFIGURAÇÕES ===============
# Pasta original do jogo
GAME_ENTITIES_FOLDER = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Magic Rampage\entities')

# Pastas de destino
DEST_PNG_FOLDER = Path(r'C:\Users\Marco\Downloads\Montagem (1)\Cabeça\Png\Skins')
DEST_XML_FOLDER = Path(r'C:\Users\Marco\Downloads\Montagem (1)\Cabeça\Xml')

# Mapeamento: classname → Nome da pasta em português
CLASS_TO_FOLDER = {
    'witchdoctor': 'Feiticeiro',
    'warrior': 'Guerreiro',
    'ranger': 'Guardião',
    'druid': 'Druida',
    'priest': 'Sacerdote',
    'paladin': 'Paladino',
    'black-mage': 'Mago Sombrio',
    'elite-warrior': 'Guerreiro de Elite',
    'high-mage': 'Alto Mago',
    'mage': 'Mago',
    'warlock': 'Bruxo',
    'rogue': 'Ladino',
    'thief': 'Ladrão',
}

# =============================================

# Cria as pastas de destino
DEST_PNG_FOLDER.mkdir(parents=True, exist_ok=True)
DEST_XML_FOLDER.mkdir(parents=True, exist_ok=True)

# Cria subpastas para cada classe
for folder_name in CLASS_TO_FOLDER.values():
    (DEST_PNG_FOLDER / folder_name).mkdir(exist_ok=True)

total_png_copiados = 0
total_xml_copiados = 0

print("Procurando skins (PNG e XML)...\n")

# Percorre todos os arquivos na pasta entities
for file_path in GAME_ENTITIES_FOLDER.iterdir():
    if not file_path.is_file():
        continue
    
    filename = file_path.name.lower()
    
    # Verifica se é um PNG de skin: skin-qualquercoisa.png
    if filename.startswith('skin-') and filename.endswith('.png'):
        # Extrai a parte da classe: ex: skin-witchdoctor8.png → witchdoctor8
        classname_part = filename[5:-4]  # remove "skin-" e ".png"
        
        # Encontra qual classe corresponde (procura a mais longa que casa no início)
        matched_class = None
        for class_key in sorted(CLASS_TO_FOLDER.keys(), key=len, reverse=True):
            if classname_part.startswith(class_key):
                matched_class = class_key
                break
        
        if matched_class:
            folder_name_pt = CLASS_TO_FOLDER[matched_class]
            dest_folder = DEST_PNG_FOLDER / folder_name_pt
            dest_file = dest_folder / file_path.name
            
            if not dest_file.exists():
                shutil.copy2(file_path, dest_file)
                print(f"PNG Copiado: {file_path.name} → {folder_name_pt}/")
                total_png_copiados += 1
            # else: já existe, pula silenciosamente
        else:
            print(f"PNG Ignorado (classe desconhecida): {file_path.name}")
    
    # Verifica se é um XML de skin: skin-qualquercoisa.xml
    elif filename.startswith('skin-') and filename.endswith('.xml'):
        dest_file = DEST_XML_FOLDER / file_path.name
        
        if not dest_file.exists():
            shutil.copy2(file_path, dest_file)
            print(f"XML Copiado: {file_path.name}")
            total_xml_copiados += 1
        # else: já existe, pula

print("\n" + "="*60)
print("Concluído!")
print(f"PNGs copiados: {total_png_copiados} → organizados em subpastas")
print(f"XMLs copiados: {total_xml_copiados} → todos na mesma pasta")
print(f"\nPNGs salvos em: {DEST_PNG_FOLDER}")
print(f"XMLs salvos em: {DEST_XML_FOLDER}")