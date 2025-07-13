# === IMPORTAÇÕES ===
import os
import pygame
import pandas as pd
import random
from PIL import Image
import customtkinter as ctk
from customtkinter import CTkImage, CTkFont
from tkinter import filedialog, messagebox
import tkinter as tk
import tkinter.font as tkFont  # Adicionado para fontes

# === CONFIGURAÇÃO DO APP ===
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
app = ctk.CTk()
screen_w, screen_h = app.winfo_screenwidth(), app.winfo_screenheight()
app.geometry(f"{screen_w}x{screen_h}")
app.title("Adepti Teahouse")

# === CANVAS DE PARTÍCULAS (FUNDO) ===
canvas = tk.Canvas(app, width=screen_w, height=screen_h, bg=None, highlightthickness=0)
canvas.place(x=0, y=0)
canvas.tk.call('raise', str(canvas))  # Para frente
canvas.tk.call('lower', str(canvas))  # Para trás


particles = []
for _ in range(50):
    x = random.randint(0, screen_w)
    y = random.randint(0, screen_h)
    r = random.randint(2, 6)
    color = "#ffffff"
    particle = canvas.create_oval(x, y, x + r, y + r, fill=color, outline="", width=0)
    particles.append((particle, x, y, r))

def animar_particulas():
    for i, (p, x, y, r) in enumerate(particles):
        dy = random.randint(0, 2)
        dx = random.choice([-1, 0, 1])
        x = (x + dx) % screen_w
        y = (y - dy) % screen_h
        canvas.coords(p, x, y, x + r, y + r)
        particles[i] = (p, x, y, r)
    canvas.after(80, animar_particulas)

animar_particulas()

# === CAMINHOS DO PROJETO ===
ICON_PATH = r"C:\meu_projeto\assets\icons_wanderer"
MATERIAL_PATH = r"C:\meu_projeto\assets\materials"
FUNDO_PATH = r"C:\meu_projeto\assets\fundos\green_xiao.jpg"

# === FUNDO ORIGINAL DO XIAO ===
if os.path.exists(FUNDO_PATH):
    fundo = Image.open(FUNDO_PATH).resize((screen_w, screen_h))
    bg_image = CTkImage(light_image=fundo, size=fundo.size)
    ctk.CTkLabel(app, image=bg_image, text="").place(x=0, y=0, relwidth=1, relheight=1)




# === FONTES ===
try:
    genshin_font = CTkFont("SDK_SC_Web", size=16)
    material_font = CTkFont("SDK_SC_Web", size=18)
except:
    genshin_font = CTkFont("Arial", size=16)
    material_font = CTkFont("Arial", size=18)

# === FRAMES PRINCIPAIS ===
frame_esq = ctk.CTkScrollableFrame(app, width=500, height=screen_h-40, fg_color="transparent")
frame_esq.place(x=20, y=20)

frame_ctr = ctk.CTkFrame(app, width=600, height=700, fg_color="transparent")
frame_ctr.place_forget()  # Oculto ao iniciar

frame_dir = ctk.CTkScrollableFrame(app, width=450, height=screen_h - 150, fg_color="#1e1e1e", corner_radius=12)
frame_dir.place_forget()  # Oculto ao iniciar

# === VARIÁVEIS ===
personagens_data = []
catalogo_data = {}
lista_pedidos = []

def carregar_imagem(path, tamanho=(64, 64)):
    if not os.path.exists(path):
        return None
    try:
        img = Image.open(path).resize(tamanho)
        return CTkImage(light_image=img, size=tamanho)
    except:
        return None

def carregar_personagens_locais():
    arquivos = os.listdir(ICON_PATH)
    nomes = []
    for f in arquivos:
        if f.startswith("ui-avataricon-") and f.endswith(".png"):
            nome = f.replace("ui-avataricon-", "").replace(".png", "")
            nomes.append(nome.capitalize())
    return sorted(nomes)

def carregar_dados():
    global personagens_data, catalogo_data
    personagens_data = []
    for nome in carregar_personagens_locais():
        icon_path = os.path.join(ICON_PATH, f"ui-avataricon-{nome.lower()}.png")
        if os.path.exists(icon_path):
            personagens_data.append({
                "name": nome,
                "icon": icon_path,
                "card": icon_path
            })

    catalogo_data = {}
    for categoria in os.listdir(MATERIAL_PATH):
        cat_path = os.path.join(MATERIAL_PATH, categoria)
        if not os.path.isdir(cat_path):
            continue
        for f in os.listdir(cat_path):
            if f.endswith(".png"):
                nome = f.replace(".png", "").replace("_", " ").title()
                catalogo_data[nome] = {
                    "name": nome,
                    "icon": os.path.join(cat_path, f),
                    "sources": [categoria.replace("-", " ").title()]
                }

def calcular_exp():
    return {"EXP Total": 250000, "Mora": 400000, "Hero's Wit": 12}

def gerar_planilha(df):
    path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
    if path:
        df.to_excel(path, index=False)
        messagebox.showinfo("Exportado", f"Planilha salva em:\n{path}")

class HoverButton(ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_fg = kwargs.get("fg_color", "#FFD700")
        self.bind("<Enter>", lambda e: self.configure(fg_color="#FFF3AA"))
        self.bind("<Leave>", lambda e: self.configure(fg_color=self.default_fg))

def atualizar_resumo():
    for w in frame_dir.winfo_children():
        w.destroy()
    if not lista_pedidos:
        return

    df = pd.DataFrame(lista_pedidos)
    df_total = df.drop(columns=["personagem", "lv_atual", "lv_destino"]).fillna(0).sum().reset_index()
    df_total.columns = ["Item", "Quantidade"]

    ctk.CTkLabel(frame_dir, text="Resumo de Materiais:", font=material_font, text_color="white").pack(pady=10)

    for _, row in df_total.iterrows():
        item = row["Item"]
        qtd = int(row["Quantidade"])
        mat = catalogo_data.get(item)
        nome = f"{item} × {qtd}"
        fonte = ", ".join(mat.get("sources", [])) if mat else "Desconhecido"
        img = carregar_imagem(mat["icon"]) if mat else None

        bloco = ctk.CTkFrame(frame_dir, fg_color="#2a2a2a", corner_radius=12)
        bloco.pack(pady=6, padx=10, fill="x")

        if img:
            ctk.CTkLabel(bloco, image=img, text="").pack(side="left", padx=10)

        texto = ctk.CTkFrame(bloco, fg_color="transparent")
        texto.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(texto, text=nome, font=material_font, text_color="#FFD700", anchor="w").pack(anchor="w")
        ctk.CTkLabel(texto, text=f"Fonte: {fonte}", font=genshin_font, text_color="white", anchor="w").pack(anchor="w")

    HoverButton(
        frame_dir,
        text="✔ Gerar Planilha",
        font=material_font,
        corner_radius=12,
        fg_color="#FFD700",
        text_color="black",
        hover_color="#FFF3AA",
        command=lambda: gerar_planilha(df_total)
    ).pack(pady=20)

def on_adicionar(nome):
    try:
        lv_at = int(entry_atual.get())
        lv_dest = int(entry_destino.get())
    except:
        messagebox.showerror("Erro", "Nível inválido")
        return

    dados = {
        "personagem": nome,
        "lv_atual": lv_at,
        "lv_destino": lv_dest,
        "Slime Condensate": 18,
        "Firm Arrowhead": 12,
        "Cecilia": 6,
    }
    dados.update(calcular_exp())
    lista_pedidos.append(dados)
    atualizar_resumo()

def selecionar_personagem(nome):
    frame_ctr.place(x=screen_w//2 - 300, y=80)
    frame_dir.place(x=screen_w - 470, y=80)

    for w in frame_ctr.winfo_children():
        w.destroy()

    card_frame = ctk.CTkFrame(frame_ctr, width=580, height=700, fg_color="#121212", corner_radius=20)
    card_frame.pack(pady=20)
    card_frame.pack_propagate(False)

    moldura = ctk.CTkFrame(card_frame, fg_color="#1e1e1e", border_color="#FFD700", border_width=3, corner_radius=16)
    moldura.pack(padx=20, pady=20, fill="both", expand=True)
    moldura.pack_propagate(False)

    ctk.CTkLabel(moldura, text=nome, font=CTkFont("SDK_SC_Web", size=26, weight="bold"), text_color="white").pack(pady=(20, 10))
    img_path = os.path.join(ICON_PATH, f"ui-avataricon-{nome.lower()}.png")
    img = carregar_imagem(img_path, tamanho=(320, 320)) if os.path.exists(img_path) else None
    if img:
        ctk.CTkLabel(moldura, image=img, text="").pack(pady=10)

    global entry_atual, entry_destino
    lv_frame = ctk.CTkFrame(moldura, fg_color="#1a1a1a", corner_radius=10)
    lv_frame.pack(pady=20)

    ctk.CTkLabel(lv_frame, text="Level Atual:", font=material_font, text_color="white").pack(side="left", padx=10)
    entry_atual = ctk.CTkEntry(lv_frame, width=80, fg_color="#2a2a2a", text_color="white", corner_radius=10)
    entry_atual.pack(side="left", padx=5)

    ctk.CTkLabel(lv_frame, text="➔", font=material_font, text_color="#FFD700").pack(side="left", padx=10)

    entry_destino = ctk.CTkEntry(lv_frame, width=80, fg_color="#2a2a2a", text_color="white", corner_radius=10)
    entry_destino.pack(side="left", padx=5)

    HoverButton(
        moldura,
        text="➕ Adicionar Personagem",
        font=material_font,
        corner_radius=12,
        fg_color="#FFD700",
        text_color="black",
        hover_color="#FFF3AA",
        height=40,
        command=lambda: on_adicionar(nome)
    ).pack(pady=(20, 15))

# === CARREGAMENTO E INICIALIZAÇÃO ===
carregar_dados()

for nome in sorted([p["name"] for p in personagens_data]):
    frame_p = ctk.CTkFrame(frame_esq, fg_color="#1e1e1e", corner_radius=10)
    frame_p.pack(fill="x", padx=10, pady=6)

    dados = next((p for p in personagens_data if p["name"] == nome), None)
    img_icon = carregar_imagem(dados["icon"], tamanho=(48, 48)) if dados else None

    HoverButton(
        frame_p,
        image=img_icon,
        text=nome,
        font=material_font,
        anchor="w",
        height=50,
        fg_color="#2c2c2c",
        text_color="white",
        hover_color="#FFD700",
        corner_radius=8,
        compound="left",
        command=lambda nome=nome: selecionar_personagem(nome)
    ).pack(fill="x", padx=8, pady=4)


# === MÚSICA DE FUNDO ===
import time

pygame.mixer.init()
MUSIC_PATH = r"C:\meu_projeto\assets\music"  # Altere conforme necessário
musicas = [f for f in os.listdir(MUSIC_PATH) if f.endswith(".mp3")]

musica_atual = {"nome": None}
musica_completa = ""

def proxima_musica():
    if not musicas:
        return
    nova = random.choice([m for m in musicas if m != musica_atual["nome"]])
    musica_atual["nome"] = nova
    global musica_completa, duracao_musica
    musica_completa = os.path.join(MUSIC_PATH, nova)
    try:
        pygame.mixer.music.load(musica_completa)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.3)
        label_musica.configure(text=f"🎵 {nova}")
        botao_play_pause.configure(text="⏸")
        duracao_musica = atualizar_duracao()
    except Exception as e:
        print("Erro ao trocar música:", e)

def tocar_ou_pausar():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        botao_play_pause.configure(text="▶")
    else:
        pygame.mixer.music.unpause()
        botao_play_pause.configure(text="⏸")

# Iniciar primeira música
if musicas:
    musica_atual["nome"] = random.choice(musicas)
    musica_completa = os.path.join(MUSIC_PATH, musica_atual["nome"])
    try:
        pygame.mixer.music.load(musica_completa)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
        print(f"🎵 Tocando: {musica_atual['nome']}")
        player = MiniPlayer(app, [os.path.join(MUSIC_PATH, m) for m in musicas])
    except Exception as e:
        print("Erro ao carregar música:", e)



import pygame
import tkinter as tk  # ou from tkinter import *
import customtkinter as ctk
from tkinter import font as tkFont
import os  # Importa o módulo os para manipulação de arquivos e diretórios


class MiniPlayer:
    def __init__(self, master, track_list, width=620, height=280):
        # Configurações iniciais
        self.master = master
        self.track_list = track_list
        self.current_index = 0
        self.is_playing = False
        self.duration = 1

        # Inicializa pygame.mixer
        pygame.mixer.init()

        # Fonte personalizada
        available_fonts = list(tkFont.families())  # Corrigido
        font_name = "SDK_SC_Web" if "SDK_SC_Web" in available_fonts else "Arial"
        self.player_font = CTkFont(font_name, size=28)

        # Variáveis Tkinter
        self.prog_var = ctk.DoubleVar(value=0.0)
        self.time_var = ctk.StringVar(value="0:00")
        self.total_var = ctk.StringVar(value="0:00")

        # Monta interface
        self._build_ui(width, height)

        # Carrega primeira faixa e inicia update loop
        self.load_track(self.current_index)
        self._update_progress()

    def _build_ui(self, w, h):
        # Frame Principal
        self.frame = ctk.CTkFrame(
            self.master, width=w, height=h,
            fg_color="#1e1e1e", border_color="#FFD700",
            border_width=2, corner_radius=20
        )
        self.frame.place(
            x=self.master.winfo_screenwidth() - w - 20,
            y=self.master.winfo_screenheight() - h - 40
        )
        self.frame.pack_propagate(False)

        # Label do nome da música
        self.label_track = ctk.CTkLabel(
            self.frame, text="",
            font=self.player_font, text_color="#FFD700"
        )
        self.label_track.pack(pady=(20, 10))

        # Barra e tempos
        bar_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        bar_frame.pack(fill="x", padx=40)

        ctk.CTkLabel(bar_frame, textvariable=self.time_var,
                     font=self.player_font, text_color="white") \
            .pack(side="left", padx=(0,10))

        self.progress = ctk.CTkProgressBar(
            bar_frame, variable=self.prog_var,
            width=500, height=14, progress_color="#FFD700"
        )
        self.progress.pack(side="left", expand=True)
        self.progress.bind("<Button-1>", self._on_click_progress)

        ctk.CTkLabel(bar_frame, textvariable=self.total_var,
                     font=self.player_font, text_color="white") \
            .pack(side="left", padx=(10,0))

        # Botões de controle
        btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        btn_frame.pack(pady=16)

        self.btn_prev = ctk.CTkButton(
            btn_frame, text="⏮", width=80, height=60,
            font=self.player_font,
            fg_color="#FFD700", text_color="black",
            hover_color="#ffeb80", command=self.prev_track
        )
        self.btn_prev.pack(side="left", padx=12)

        self.btn_play = ctk.CTkButton(
            btn_frame, text="▶️", width=80, height=60,
            font=self.player_font,
            fg_color="#FFD700", text_color="black",
            hover_color="#ffeb80", command=self.toggle_play
        )
        self.btn_play.pack(side="left", padx=12)

        self.btn_next = ctk.CTkButton(
            btn_frame, text="⏭", width=80, height=60,
            font=self.player_font,
            fg_color="#FFD700", text_color="black",
            hover_color="#ffeb80", command=self.next_track
        )
        self.btn_next.pack(side="left", padx=12)

    def load_track(self, index):
        # Carrega e exibe metadados
        path = self.track_list[index]
        self.label_track.configure(text=f"🎵 {os.path.basename(path)}")

        try:
            pygame.mixer.music.load(path)
            self._update_duration(path)
        except pygame.error as e:
            print(f"Falha ao carregar {path}: {e}")
            self.duration = 1
            self.total_var.set("0:00")

    def _update_duration(self, path):
        try:
            sound = pygame.mixer.Sound(path)
            self.duration = max(1, int(sound.get_length()))
            m, s = divmod(self.duration, 60)
            self.total_var.set(f"{m}:{s:02d}")
        except pygame.error:
            self.duration = 1
            self.total_var.set("0:00")

    def toggle_play(self):
        if not self.is_playing:
            pygame.mixer.music.play()
            self.btn_play.configure(text="⏸")
            self.is_playing = True
        else:
            pygame.mixer.music.pause()
            self.btn_play.configure(text="▶️")
            self.is_playing = False

    def prev_track(self):
        pygame.mixer.music.stop()
        self.current_index = (self.current_index - 1) % len(self.track_list)
        self.load_track(self.current_index)
        if self.is_playing:
            pygame.mixer.music.play()

    def next_track(self):
        pygame.mixer.music.stop()
        self.current_index = (self.current_index + 1) % len(self.track_list)
        self.load_track(self.current_index)
        if self.is_playing:
            pygame.mixer.music.play()

    def _on_click_progress(self, event):
        # Se a duração não estiver válida, aborta
        if not isinstance(self.duration, int) or self.duration <= 0:
            return

        largura = self.progress.winfo_width() or 1
        pct = min(max(event.x / largura, 0.0), 1.0)
        novo = int(pct * self.duration)

        pygame.mixer.music.play(start=novo)
        self.prog_var.set(pct)
        m, s = divmod(novo, 60)
        self.time_var.set(f"{m}:{s:02d}")

    def _update_progress(self):
        if self.is_playing:
            pos = pygame.mixer.music.get_pos() // 1000
            pct = min(pos / self.duration, 1.0)
            self.prog_var.set(pct)
            m, s = divmod(pos, 60)
            self.time_var.set(f"{m}:{s:02d}")
        self.master.after(1000, self._update_progress)



# === LOOP PRINCIPAL ===
app.mainloop()
