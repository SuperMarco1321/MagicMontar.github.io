import os
from tkinter import Tk, Listbox, Button, Scrollbar, Frame, END, LEFT, RIGHT, Y, MULTIPLE, filedialog, simpledialog, messagebox
from PIL import Image

# Janela principal
root = Tk()
root.title("Gerador de GIF - Definir Ordem das Frames")
root.geometry("700x600")
root.resizable(True, True)

# Frame principal
frame = Frame(root)
frame.pack(fill="both", expand=True, padx=10, pady=10)

# Lista de imagens selecionadas
listbox = Listbox(frame, selectmode=MULTIPLE, font=("Arial", 10))
listbox.pack(side=LEFT, fill="both", expand=True)

# Scrollbar
scrollbar = Scrollbar(frame)
scrollbar.pack(side=RIGHT, fill=Y)
listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

imagens_paths = []  # Armazena os caminhos reais das imagens

def adicionar_imagens():
    arquivos = filedialog.askopenfilenames(
        title="Selecione as imagens para o GIF (PNG com transparência recomendado)",
        filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp *.gif")]
    )
    if arquivos:
        for caminho in arquivos:
            if caminho not in imagens_paths:
                imagens_paths.append(caminho)
                nome = os.path.basename(caminho)
                listbox.insert(END, nome)
        atualizar_contador()

def remover_selecionadas():
    selecionados = listbox.curselection()
    if not selecionados:
        return
    for i in sorted(selecionados, reverse=True):
        listbox.delete(i)
        imagens_paths.pop(i)
    atualizar_contador()

def mover_para_cima():
    selecionados = listbox.curselection()
    if not selecionados or 0 in selecionados:
        return
    for i in selecionados:
        texto = listbox.get(i)
        caminho = imagens_paths[i]
        listbox.delete(i)
        listbox.insert(i-1, texto)
        imagens_paths.pop(i)
        imagens_paths.insert(i-1, caminho)
    listbox.selection_clear(0, END)
    for novo_i in [i-1 for i in selecionados]:
        listbox.selection_set(novo_i)

def mover_para_baixo():
    selecionados = listbox.curselection()
    if not selecionados or listbox.size()-1 in selecionados:
        return
    for i in sorted(selecionados, reverse=True):
        texto = listbox.get(i)
        caminho = imagens_paths[i]
        listbox.delete(i)
        listbox.insert(i+1, texto)
        imagens_paths.pop(i)
        imagens_paths.insert(i+1, caminho)
    listbox.selection_clear(0, END)
    for novo_i in [i+1 for i in selecionados]:
        listbox.selection_set(novo_i)

def atualizar_contador():
    root.title(f"Gerador de GIF - {len(imagens_paths)} frames selecionadas")

def gerar_gif():
    if len(imagens_paths) < 2:
        messagebox.showwarning("Aviso", "Selecione pelo menos 2 imagens para criar um GIF!")
        return
    
    # Pergunta a duração por frame
    duracao_str = simpledialog.askstring("Velocidade do GIF", "Duração por frame em milissegundos (ex: 80 para rápido, 100 para médio):", initialvalue="80")
    try:
        duracao = int(duracao_str) if duracao_str and duracao_str.isdigit() else 80
    except:
        duracao = 80
    
    # Pergunta nome do arquivo
    nome_arquivo = simpledialog.askstring("Nome do GIF", "Nome do arquivo de saída (sem extensão):", initialvalue="personagem_animado")
    if not nome_arquivo:
        nome_arquivo = "gif_gerado"
    
    # Pasta onde o script está
    pasta_saida = os.path.dirname(os.path.abspath(__file__))
    arquivo_saida = os.path.join(pasta_saida, f"{nome_arquivo}.gif")
    
    try:
        print("Carregando imagens (mantendo tamanho original e transparência)...")
        imagens = []
        for path in imagens_paths:
            img = Image.open(path).convert("RGBA")  # Força RGBA para preservar transparência
            imagens.append(img)
        
        print(f"Gerando GIF com transparência perfeita e limpeza de frames: {arquivo_saida}")
        imagens[0].save(
            arquivo_saida,
            save_all=True,
            append_images=imagens[1:],
            duration=duracao,
            loop=0,
            optimize=True,
            disposal=2  # Limpa frame anterior (sem resíduos)
            # transparency removido para evitar perda de alpha em alguns casos
        )
        messagebox.showinfo("Sucesso!", f"GIF gerado com sucesso!\nTransparência e tamanho original preservados.\nSalvo em:\n{arquivo_saida}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar GIF:\n{str(e)}")

# Botões
btn_frame = Frame(root)
btn_frame.pack(pady=10)

Button(btn_frame, text="Adicionar Imagens", command=adicionar_imagens, width=18).pack(side=LEFT, padx=5)
Button(btn_frame, text="Remover Selecionadas", command=remover_selecionadas, width=20).pack(side=LEFT, padx=5)
Button(btn_frame, text="↑ Mover para Cima", command=mover_para_cima, width=18).pack(side=LEFT, padx=5)
Button(btn_frame, text="↓ Mover para Baixo", command=mover_para_baixo, width=18).pack(side=LEFT, padx=5)
Button(btn_frame, text="GERAR GIF", command=gerar_gif, bg="green", fg="white", font=("Arial", 12, "bold"), width=25).pack(side=LEFT, padx=20)

# Instruções
from tkinter import Label
Label(root, text="Adicione imagens → Ajuste ordem → GERAR GIF (transparência e tamanho corrigidos!)", fg="blue", font=("Arial", 10, "bold")).pack(pady=10)

atualizar_contador()
root.mainloop()