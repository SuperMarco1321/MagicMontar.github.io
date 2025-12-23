import os
import re
from tkinter import Tk, filedialog
from PIL import Image, ImageChops, ImageOps
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import colorchooser

def argb_to_rgba(argb_int):
    a = (argb_int >> 24) & 0xFF
    r = (argb_int >> 16) & 0xFF
    g = (argb_int >> 8) & 0xFF
    b = argb_int & 0xFF
    return (r, g, b, a)

def apply_color_tint(img: Image.Image, rgba: tuple) -> Image.Image:
    base = img.convert("RGBA")
    r_t, g_t, b_t, _ = rgba
    solid = Image.new('RGB', base.size, (r_t, g_t, b_t))
    tinted_rgb = ImageChops.multiply(base.convert('RGB'), solid)
    alpha = base.split()[3]
    return Image.merge('RGBA', (*tinted_rgb.split(), alpha))

def rgba_to_argb_int(r, g, b, a=255):
    return (a << 24) + (r << 16) + (g << 8) + b

def escolher_cor_ou_pular():
    root = tk.Tk()
    root.withdraw()
    resposta = input("Pressione Enter para pular ou digite qualquer coisa para escolher uma cor: ")
    if not resposta.strip():
        return None
    rgb_color = colorchooser.askcolor(title="Escolha a cor")[0]
    if rgb_color is None:
        return None
    r, g, b = map(int, rgb_color)
    argb_int = rgba_to_argb_int(r, g, b)
    print(f"Código ARGB selecionado: {argb_int}")
    return argb_to_rgba(argb_int)

def parse_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    sprites = []
    for s in root.findall('sprite'):
        sprites.append({
            'name': s.get('n'),
            'x': int(s.get('x')),
            'y': int(s.get('y')),
            'w': int(s.get('w')),
            'h': int(s.get('h')),
            'oX': int(s.get('oX') or 0),
            'oY': int(s.get('oY') or 0),
            'oW': int(s.get('oW') or 0),
            'oH': int(s.get('oH') or 0),
            'pX': float(s.get('pX') or 0.5),
            'pY': float(s.get('pY') or 0.5),
        })
    return sprites

def natural_key(name):
    nums = re.findall(r"\d+", name)
    return tuple(map(int, nums)) if nums else (name,)

def escolher_png_e_xml(pasta_png, pasta_xml, titulo):
    root = Tk(); root.withdraw()
    arquivo = filedialog.askopenfilename(
        title=titulo,
        initialdir=pasta_png,
        filetypes=[("PNG sprites", "*.png")]
    )
    root.destroy()
    if not arquivo:
        raise Exception("Nenhum PNG selecionado.")
    base = os.path.splitext(os.path.basename(arquivo))[0]
    xml = os.path.join(pasta_xml, base + ".xml")
    if not os.path.exists(xml):
        raise FileNotFoundError(f"XML não encontrado: {xml}")
    return arquivo, xml

def choose_png(pasta_png, titulo):
    root = Tk(); root.withdraw()
    arquivo = filedialog.askopenfilename(
        title=titulo,
        initialdir=pasta_png,
        filetypes=[("PNG sprites", "*.png")]
    )
    root.destroy()
    if not arquivo:
        raise Exception("Nenhum PNG selecionado.")
    return arquivo

def calcular_posicao(pivot_x, pivot_y, sprite):
    if sprite is None:
        return None, None
    pos_x = pivot_x - (sprite['pX'] * sprite['oW'] - sprite['oX'])
    pos_y = pivot_y - (sprite['pY'] * sprite['oH'] - sprite['oY'])
    return pos_x, pos_y

def montar_frame(body_sprite, layers, imgs, colors, weapon_info):
    pivot_x = body_sprite['pX'] * body_sprite['oW']
    pivot_y = body_sprite['pY'] * body_sprite['oH']

    crops = {}
    positions = {}

    # Corpo
    crop_body = imgs['body'].crop((body_sprite['x'], body_sprite['y'], body_sprite['x']+body_sprite['w'], body_sprite['y']+body_sprite['h']))
    if colors['body']:
        crop_body = apply_color_tint(crop_body, colors['body'])
    crops['body'] = crop_body
    positions['body'] = calcular_posicao(pivot_x, pivot_y, body_sprite)

    # Camadas variáveis normais
    for key in ['armor', 'amuleto', 'pet', 'head']:
        sprite = layers.get(key)
        if sprite and key in imgs and imgs[key]:
            crop = imgs[key].crop((sprite['x'], sprite['y'], sprite['x']+sprite['w'], sprite['y']+sprite['h']))
            crops[key] = crop
            positions[key] = calcular_posicao(pivot_x, pivot_y, sprite)

    # Olhos com blend additive
    crop_eye = None
    if 'eye' in layers and layers['eye'] and imgs['eye']:
        sprite = layers['eye']
        crop_eye = imgs['eye'].crop((sprite['x'], sprite['y'], sprite['x']+sprite['w'], sprite['y']+sprite['h']))
        if colors['eye']:
            crop_eye = apply_color_tint(crop_eye, colors['eye'])
        # Preparar para additive: preto vira transparente, resto vira brilho
        crop_eye = crop_eye.convert("RGBA")
        crops['eye'] = crop_eye
        positions['eye'] = calcular_posicao(pivot_x, pivot_y, sprite)

    # Arma
    if weapon_info['png'] and imgs['weapon']:
        rotated = imgs['weapon'].rotate(weapon_info['angle'], expand=True, resample=Image.BILINEAR)
        crops['weapon'] = rotated
        offset_x, offset_y = weapon_info['offset']
        positions['weapon'] = (pivot_x + offset_x - rotated.width / 2, pivot_y + offset_y - rotated.height / 2)

    # Bounding box
    all_x = [p[0] for p in positions.values() if p[0] is not None]
    all_y = [p[1] for p in positions.values() if p[1] is not None]
    all_w = [crops[k].width for k in crops if k in crops]
    all_h = [crops[k].height for k in crops if k in crops]

    if not all_x:
        return Image.new('RGBA', (1, 1), (0,0,0,0))

    left = min(all_x)
    top = min(all_y)
    right = max(x + w for x, w in zip(all_x, all_w))
    bottom = max(y + h for y, h in zip(all_y, all_h))

    final = Image.new('RGBA', (int(right - left), int(bottom - top)), (0,0,0,0))

    # Ordem de colagem (olhos por último com blend additive)
    normal_order = ['weapon', 'body', 'armor', 'amuleto', 'pet', 'head']
    for layer in normal_order:
        if layer in crops and crops[layer]:
            px, py = positions[layer]
            final.paste(crops[layer], (int(px - left), int(py - top)), crops[layer])

    # Olhos com Additive Blend
    if crop_eye:
        px, py = positions['eye']
        pos = (int(px - left), int(py - top))
        
        # Criar camada temporária para additive
        eye_layer = Image.new('RGBA', final.size, (0,0,0,0))
        eye_layer.paste(crop_eye, pos, crop_eye)
        
        # Converter para RGB temporariamente para o add
        final_rgb = final.convert('RGB')
        eye_rgb = eye_layer.convert('RGB')
        
        # Additive blend
        added = ImageChops.add(final_rgb, eye_rgb)
        
        # Manter alpha original do final (exceto onde olhos adicionam brilho)
        final = Image.merge('RGBA', (*added.split(), final.split()[3]))

    return final

# As funções combine_first_sprite e gerar_montagens_completas permanecem iguais às da versão anterior
# (apenas copiei para manter o arquivo completo)

def combine_first_sprite(body_xml, body_png, output_dir, **kwargs):
    body_data = sorted(parse_xml(body_xml), key=lambda d: natural_key(d['name']))
    b = body_data[0]

    layers = {k: sorted(parse_xml(v), key=lambda d: natural_key(d['name']))[0] if v else None
              for k, v in [('armor', kwargs.get('armor_xml')), ('amuleto', kwargs.get('amuleto_xml')),
                           ('pet', kwargs.get('pet_xml')), ('head', kwargs.get('head_xml')), ('eye', kwargs.get('eye_xml'))]}

    imgs = {k: Image.open(v).convert('RGBA') if v else None for k, v in
            [('body', body_png), ('armor', kwargs.get('armor_png')), ('amuleto', kwargs.get('amuleto_png')),
             ('pet', kwargs.get('pet_png')), ('head', kwargs.get('head_png')), ('eye', kwargs.get('eye_png')),
             ('weapon', kwargs.get('weapon_png'))]}

    colors = {'body': kwargs.get('body_color'), 'eye': kwargs.get('eye_color')}

    weapon_info = {'png': kwargs.get('weapon_png'), 'angle': kwargs.get('weapon_angle', 0),
                   'offset': kwargs.get('weapon_offset', (0, 0))}

    final = montar_frame(b, layers, imgs, colors, weapon_info)

    layers_names = [os.path.splitext(os.path.basename(p))[0] for p in
                    [body_png, kwargs.get('armor_png'), kwargs.get('amuleto_png'), kwargs.get('pet_png'),
                     kwargs.get('head_png'), kwargs.get('eye_png'), kwargs.get('weapon_png')] if p]
    label = os.path.splitext(b['name'])[0]
    out_name = "_".join(layers_names + [label]) + ".png"
    final.save(os.path.join(output_dir, out_name))
    print(f"Preview salvo: {out_name}")

def gerar_montagens_completas(body_xml, body_png, output_dir, **kwargs):
    body_data = sorted(parse_xml(body_xml), key=lambda d: natural_key(d['name']))

    layer_data = {}
    for key, xml_path in [('armor', kwargs.get('armor_xml')), ('amuleto', kwargs.get('amuleto_xml')),
                          ('pet', kwargs.get('pet_xml')), ('head', kwargs.get('head_xml')), ('eye', kwargs.get('eye_xml'))]:
        if xml_path:
            data = sorted(parse_xml(xml_path), key=lambda d: natural_key(d['name']))
            if len(data) != len(body_data):
                print(f"Aviso: {key} tem {len(data)} sprites, mas corpo tem {len(body_data)}. Usará até o limite.")
            layer_data[key] = data

    imgs = {k: Image.open(v).convert('RGBA') if v else None for k, v in
            [('body', body_png), ('armor', kwargs.get('armor_png')), ('amuleto', kwargs.get('amuleto_png')),
             ('pet', kwargs.get('pet_png')), ('head', kwargs.get('head_png')), ('eye', kwargs.get('eye_png')),
             ('weapon', kwargs.get('weapon_png'))]}

    colors = {'body': kwargs.get('body_color'), 'eye': kwargs.get('eye_color')}

    weapon_info = {'png': kwargs.get('weapon_png'), 'angle': kwargs.get('weapon_angle', 0),
                   'offset': kwargs.get('weapon_offset', (0, 0))}

    os.makedirs(output_dir, exist_ok=True)
    total = len(body_data)
    print(f"Gerando {total} frames...")

    for i, b in enumerate(body_data):
        layers = {k: data[min(i, len(data)-1)] for k, data in layer_data.items()}
        final = montar_frame(b, layers, imgs, colors, weapon_info)
        nome = b['name'].replace('/', '_').replace('\\', '_')
        out_path = os.path.join(output_dir, f"{nome}.png")
        final.save(out_path)

    print(f"Todos os {total} frames foram salvos em: {output_dir}")

if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    dirs = {
        'corpo': ("Corpo/Png", "Corpo/Xml"),
        'armor': ("Armaduras/Png", "Armaduras/Xml"),
        'amuleto': ("Amuleto/Png", "Amuleto/Xml"),
        'pet': ("Pet/Png", "Pet/Xml"),
        'head': ("Cabeça/Png", "Cabeça/Xml"),
        'eye': ("Olho/Png", "Olho/Xml"),
        'weapon': ("Arma/Png", None),
    }

    corpo_png, corpo_xml = escolher_png_e_xml(os.path.join(base, dirs['corpo'][0]),
                                              os.path.join(base, dirs['corpo'][1]), "Escolher Corpo")
    body_color = escolher_cor_ou_pular()

    kwargs = {'body_xml': corpo_xml, 'body_png': corpo_png, 'body_color': body_color}

    for key, pergunta in [('armor', "armadura"), ('amuleto', "amuleto"), ('pet', "pet"), ('head', "cabeça"), ('eye', "olho")]:
        if input(f"Incluir {pergunta}? (s/n): ").strip().lower().startswith('s'):
            png_dir = os.path.join(base, dirs[key][0])
            xml_dir = os.path.join(base, dirs[key][1])
            png, xml = escolher_png_e_xml(png_dir, xml_dir, f"Escolher {pergunta.capitalize()}")
            kwargs[f'{key}_png'] = png
            kwargs[f'{key}_xml'] = xml
            if key == 'eye':
                kwargs['eye_color'] = escolher_cor_ou_pular()

    if input("Incluir arma? (s/n): ").strip().lower().startswith('s'):
        weapon_png = choose_png(os.path.join(base, dirs['weapon'][0]), "Escolher Arma PNG")
        angulos_path = os.path.join(base, "Arma", "Angulos.txt")
        equippedAngle = 0
        weapon_offset = (0, 0)
        if os.path.exists(angulos_path):
            with open(angulos_path, encoding="utf-8") as f:
                txt = f.read()
            nome_sprite = os.path.basename(weapon_png)
            bloco = re.search(rf"\{{[^}}]*sprite\s*=\s*{re.escape(nome_sprite)};\s*[^}}]*\}}", txt)
            if bloco:
                try:
                    equippedAngle = float(re.search(r"equippedAngle\s*=\s*([-\d\.]+);", bloco.group(0)).group(1))
                    equipOffsetX = int(re.search(r"equipOffsetX\s*=\s*([-\d]+);", bloco.group(0)).group(1))
                    equipOffsetY = int(re.search(r"equipOffsetY\s*=\s*([-\d]+);", bloco.group(0)).group(1))
                    weapon_offset = (equipOffsetX, equipOffsetY)
                except:
                    print("Erro ao ler Angulos.txt. Usando valores padrão.")
            else:
                print(f"Configuração para '{nome_sprite}' não encontrada. Usando valores padrão.")
        else:
            print("Angulos.txt não encontrado. Usando valores padrão.")
        kwargs['weapon_png'] = weapon_png
        kwargs['weapon_offset'] = weapon_offset
        kwargs['weapon_angle'] = equippedAngle

    usar_todas = input("Gerar todas as montagens? (s/n): ").strip().lower().startswith('s')
    if usar_todas:
        gerar_montagens_completas(output_dir=base, **kwargs)
    else:
        combine_first_sprite(output_dir=base, **kwargs)