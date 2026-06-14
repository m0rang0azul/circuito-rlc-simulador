#!/usr/bin/env python
# coding: utf-8

# In[15]:


"""
Simulador de Circuito RLC Série
================================
Autora: Luana M. Souza
GitHub: https://github.com/m0rang0azul
Data: 2026
Descrição: Simulador interativo para ensino de fenômenos de ressonância em circuitos RLC
"""
import pygame
import numpy as np
import math

# ========== Inicializar Pygame ==========
pygame.init()

LARGURA_JANELA = 1600
ALTURA_JANELA = 950
LARGURA_CONTEUDO = 1600
ALTURA_CONTEUDO = 950

tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA), pygame.RESIZABLE)
pygame.display.set_caption("Circuito RLC - Teclas 1-6: Redução de Velocidade")
clock = pygame.time.Clock()

tela_conteudo = pygame.Surface((LARGURA_CONTEUDO, ALTURA_CONTEUDO))

zoom = 0.65
cam_x = 0
cam_y = 0

# ========== Parâmetros ==========
L = 10e-3
C = 100e-6
R = 2.0
V0 = 5.0
freq = 159.0
f0 = 1 / (2 * np.pi * np.sqrt(L * C))
I_max_ressonancia = V0 / R

# Velocidades
VELOCIDADES = [1, 2, 5, 10, 30, 60]
velocidade_atual = 10

print(f"f0 = {f0:.1f} Hz | I_max = {I_max_ressonancia:.2f} A")
print(f"Velocidade: {velocidade_atual}x mais lento")

# Fontes
fonte_pequena = pygame.font.Font(None, 20)
fonte_media = pygame.font.Font(None, 28)
fonte_grande = pygame.font.Font(None, 38)

# Cores
FUNDO = (25, 25, 35)
GRADE = (35, 35, 50)
COBRE = (180, 120, 40)
FERRO = (100, 100, 110)
CERAMICA = (230, 220, 200)
TEXTO_CLARO = (255, 255, 255)
BRANCO = (255, 255, 255)
AMARELO = (255, 255, 0)
CIANO = (0, 255, 255)
VERMELHO = (255, 50, 50)
VERDE = (50, 255, 100)
ROXO = (180, 100, 255)
LARANJA = (255, 180, 0)
AZUL = (50, 50, 255)

# Partículas
class Particula:
    def __init__(self, x, y):
        self.x = x; self.y = y; self.trail = []
    def update(self, vx, vy, dt):
        self.x += vx*dt; self.y += vy*dt
        self.trail.append((self.x, self.y))
        if len(self.trail) > 6: self.trail.pop(0)

n_particulas = 300
particulas = [Particula(200+(i/n_particulas)*1100, 420) for i in range(n_particulas)]

# Variáveis
tempo = 0.0
pausado = False
auto_sweep = False
sweep_dir = 1

# Cálculos
def get_valores():
    omega = 2*np.pi*freq
    Xl = omega*L
    Xc = 1/(omega*C) if omega>0 else float('inf')
    Z = np.sqrt(R**2 + (Xl-Xc)**2)
    I_amp = V0/Z
    phi = np.arctan2((Xl-Xc), R)
    i_inst = I_amp*np.sin(omega*tempo - phi)
    vc_inst = (I_amp/(omega*C))*np.sin(omega*tempo - phi - np.pi/2) if omega>0 else 0
    vf_inst = V0*np.sin(omega*tempo)
    return Xl, Xc, Z, I_amp, phi, i_inst, vc_inst, vf_inst

# Desenho
def desenhar_grade():
    for x in range(0, LARGURA_CONTEUDO, 50):
        pygame.draw.line(tela_conteudo, GRADE, (x,0), (x,ALTURA_CONTEUDO), 1)
    for y in range(0, ALTURA_CONTEUDO, 50):
        pygame.draw.line(tela_conteudo, GRADE, (0,y), (LARGURA_CONTEUDO,y), 1)

def desenhar_sombra(x, y, l, a):
    s = pygame.Surface((l+20, a+20), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0,0,0,80), (0, a-10, l+20, 30))
    tela_conteudo.blit(s, (x-10, y+a-25))

def desenhar_fonte_ac(x, y):
    desenhar_sombra(x+40, y+35, 60, 80)
    
    # Caixa principal (posição que você definiu)
    pygame.draw.rect(tela_conteudo, FERRO, (x+35, y+75, 70, 70), 0, 10)
    pygame.draw.rect(tela_conteudo, (150,150,160), (x+35, y+75, 70, 70), 3, 10)
    
    # Display digital (centralizado na caixa)
    pygame.draw.rect(tela_conteudo, (20,30,20), (x+50, y+90, 40, 25))
    pygame.draw.rect(tela_conteudo, (0,0,0), (x+50, y+90, 40, 25), 2)
    tela_conteudo.blit(fonte_media.render(f"{freq:.0f}", True, (0,255,100)), (x+55, y+92))
    tela_conteudo.blit(fonte_pequena.render("Hz", True, (0,200,50)), (x+85, y+98))
    
    # LED indicador (canto superior esquerdo da caixa)
    brilho = abs(math.sin(2*np.pi*freq*tempo))
    pygame.draw.circle(tela_conteudo, (min(255,int(50+brilho*200)),min(255,int(100+brilho*150)),255), (x+45, y+85), 5)
    
    # Símbolo AC (centro da caixa)
    tela_conteudo.blit(fonte_media.render("~", True, TEXTO_CLARO), (x+62, y+115))
    
    # Etiqueta (abaixo da caixa)
    tela_conteudo.blit(fonte_media.render("FONTE AC", True, TEXTO_CLARO), (x+20, y+150))

def desenhar_resistor(x, y):
    desenhar_sombra(x-10, y-30, 140, 60)
    
    _,_,_,_,_,i_inst,_,_ = get_valores()
    calor = min(R*i_inst**2/5.0, 1.0)
    cor = (min(255,int(255*calor)),min(255,int(100*(1-calor))),min(255,int(50*(1-calor))))
    
    # Corpo cerâmico (posição que você definiu)
    pygame.draw.rect(tela_conteudo, CERAMICA, (x, y, 120, 40), 0, 8)
    pygame.draw.rect(tela_conteudo, (180,170,160), (x, y, 120, 40), 2, 8)
    
    # Efeito de aquecimento (alinhado com a cerâmica)
    s = pygame.Surface((120,40), pygame.SRCALPHA)
    for i in range(120): 
        pygame.draw.line(s, (255,100,50,int(cor[0]*0.5)), (i,0), (i,40))
    tela_conteudo.blit(s, (x, y))
    
    # Faixas coloridas (dentro da cerâmica)
    for i,c in enumerate([(139,69,19),(0,0,0),(255,0,0),(255,215,0)]):
        pygame.draw.rect(tela_conteudo, c, (x+20+i*20, y+2, 8, 36))
    
    # Terminais (saindo das laterais da cerâmica)
    pygame.draw.rect(tela_conteudo, COBRE, (x-15, y+15, 20, 10))
    pygame.draw.rect(tela_conteudo, COBRE, (x+115, y+15, 20, 10))
    
    # Etiqueta (abaixo da cerâmica)
    tela_conteudo.blit(fonte_media.render(f"R = {R:.1f} Ohm", True, TEXTO_CLARO), (x+10, y+45))
    

def desenhar_indutor(x, y):
    desenhar_sombra(x-10, y-75, 140, 80)
    
    # Núcleo do indutor (posição que você definiu)
    pygame.draw.rect(tela_conteudo, (60,60,65), (x, y, 120, 30), 0, 5)
    pygame.draw.rect(tela_conteudo, (80,80,85), (x, y, 120, 30), 2, 5)
    
    _,_,_,_,_,i_inst,_,_ = get_valores()
    intensidade = abs(i_inst)/I_max_ressonancia if I_max_ressonancia>0 else 0
    
    # Bobina (espiras) - centralizadas no núcleo
    for i in range(15):
        brilho = min(1.0, 0.5+intensidade*0.5)
        cor = (min(255,int(200*brilho)),min(255,int(140*brilho)),min(255,int(50*brilho)))
        pygame.draw.rect(tela_conteudo, cor, (x+10+i*7, y-15, 4, 60), 0, 2)
    
    # Campo magnético (glow) - centralizado no núcleo
    s = pygame.Surface((160,100), pygame.SRCALPHA)
    for r in range(60,20,-5):
        a = min(255,int(intensidade*80*(1-r/60)))
        pygame.draw.ellipse(s, (0,255,100,a), (80-r,50-r,2*r,2*r))
    tela_conteudo.blit(s, (x-20, y-35))
    
    # Terminais (nas laterais do núcleo)
    pygame.draw.circle(tela_conteudo, COBRE, (x-5, y+15), 6)
    pygame.draw.circle(tela_conteudo, COBRE, (x+125, y+15), 6)
    
    # Etiqueta (abaixo do núcleo)
    tela_conteudo.blit(fonte_media.render(f"L = {L*1000:.0f} mH", True, TEXTO_CLARO), (x+15, y+50))

def desenhar_capacitor(x, y):
    desenhar_sombra(x-10, y-20, 100, 50)
    _, Xc, _, _, _, _, vc_inst, _ = get_valores()
    vc_norm = min(abs(vc_inst)/V0, 1.0)
    largura = 80  # Agora é largura (horizontal)
    
    # EFEITO DE BRILHO quando circuito é CAPACITIVO
    if freq < f0 and abs(freq - f0) > 2:
        intensidade_glow = min(1.0, Xc / (Xc + 2*np.pi*freq*L + 0.001))
        glow_surf = pygame.Surface((120, 80), pygame.SRCALPHA)
        for r in range(50, 15, -3):
            alpha = int(intensidade_glow * 120 * (1 - r/50))
            pygame.draw.rect(glow_surf, (200, 50, 255, alpha), (60-r, 40-r, 2*r, 2*r), border_radius=10)
        tela_conteudo.blit(glow_surf, (x-25, y-20))
    
    # Placas do capacitor (horizontais)
    for dx in range(largura):
        carga = vc_norm*(dx/largura)
        r, g, b = min(255, int(100+carga*155)), min(255, int(50+carga*100)), min(255, int(150+carga*105))
        pygame.draw.line(tela_conteudo, (r,g,b), (x+dx, y), (x+dx, y+25))
    
    # Invólucro horizontal
    pygame.draw.rect(tela_conteudo, (80,80,90), (x-5, y-5, largura+10, 35), 0, 8)
    pygame.draw.rect(tela_conteudo, (120,120,130), (x-5, y-5, largura+10, 35), 2, 8)
    
    # Faixa negativa (lado esquerdo)
    pygame.draw.rect(tela_conteudo, (50,50,50), (x-5, y-5, 20, 35), 0, 5)
    tela_conteudo.blit(fonte_pequena.render("-", True, BRANCO), (x+2, y+8))
    
    # Pontos de solda no fio
    pygame.draw.circle(tela_conteudo, COBRE, (x-7, 420), 5)
    pygame.draw.circle(tela_conteudo, COBRE, (x+87, 420), 5)
    
    # Etiqueta (abaixo)
    tela_conteudo.blit(fonte_media.render(f"C = {C*1e6:.0f} uF", True, TEXTO_CLARO), (x-5, y+35))

def desenhar_painel_equacoes():
    """Painel com as principais equações do circuito RLC"""
    px, py = 20, 20  # Canto superior esquerdo
    largura, altura = 520, 315
    
    # Fundo do painel
    pygame.draw.rect(tela_conteudo, (25, 30, 40), (px, py, largura, altura))
    pygame.draw.rect(tela_conteudo, (80, 85, 90), (px, py, largura, altura), 3)
    
    # Título
    tela_conteudo.blit(fonte_grande.render("EQUAÇÕES CIRCUITO RLC EM SÉRIE", True, (255, 255, 200)), (px+20, py+10))
    
    # Equações (cor amarela para destaque)
    equacoes = [
        ("Lei de Ohm:", f"V = R * I"),
        ("Reatância Capacitiva:", f"Xc = 1/(2πfC) = 1/(ωC)"),
        ("Reatância Indutiva:", f"XL = 2πfL = ωL"),
        ("Impedância Total:", f"Z = √(R² + (XL - Xc)²)"),
        ("Corrente:", f"I = V/Z"),
        ("Frequência de Ressonância:", f"fn = 1/(2π√(LC))"),
        ("Defasagem:", f"φ = arctan((XL - Xc)/R)"),
    ]
    
    y_eq = py + 50
    for nome, eq in equacoes:
        # Nome da equação (ciano)
        tela_conteudo.blit(fonte_media.render(nome, True, CIANO), (px+18, y_eq))
        # Equação (amarelo)
        tela_conteudo.blit(fonte_media.render(eq, True, AMARELO), (px+18, y_eq+20))
        y_eq += 36
    
    # Valores atuais dos parâmetros
    Xl, Xc, Z, I_amp, phi, _, _, _ = get_valores()
    y_val = py + 50
    valores = [
        f"Xc = {Xc:.1f} Ω",
        f"XL = {Xl:.1f} Ω",
        f"Z = {Z:.1f} Ω",
        f"I = {I_amp:.2f} A",
        f"fn = {f0:.1f} Hz",
        f"φ = {np.degrees(phi):.1f}°",
    ]
    
    for val in valores:
        tela_conteudo.blit(fonte_media.render(val, True, VERDE), (px+350, y_val))
        y_val += 32

def desenhar_fasor(cx, cy, dx, dy, cor, label, espessura):
    """Desenha um fasor com seta"""
    if abs(dx) > 0.5 or abs(dy) > 0.5:
        # Linha principal
        pygame.draw.line(tela_conteudo, cor, (cx, cy), (cx+int(dx), cy-int(dy)), espessura)
        
        # Ponta da seta
        ang = math.atan2(-dy, dx)
        ponta_x = cx + int(dx)
        ponta_y = cy - int(dy)
        
        p1 = (ponta_x, ponta_y)
        p2 = (ponta_x - int(12*np.cos(ang - 0.5)), ponta_y + int(12*np.sin(ang - 0.5)))
        p3 = (ponta_x - int(12*np.cos(ang + 0.5)), ponta_y + int(12*np.sin(ang + 0.5)))
        
        pygame.draw.polygon(tela_conteudo, cor, [p1, p2, p3])
        
        # Label do fasor
        label_x = cx + int(dx*1.15) if abs(dx) > 5 else cx + 15
        label_y = cy - int(dy*1.15) if abs(dy) > 5 else cy - 15
        tela_conteudo.blit(fonte_pequena.render(label, True, cor), (label_x-10, label_y-10))

def desenhar_fasores():
    """Diagrama fasorial do circuito RLC - REFERÊNCIA NA CORRENTE"""
    fx, fy = 650, 20
    raio_max = 120
    
    # Fundo do painel
    pygame.draw.rect(tela_conteudo, (25, 30, 40), (fx, fy, 290, 315))
    pygame.draw.rect(tela_conteudo, (60, 70, 60), (fx, fy, 290, 315), 2)
    
    # Título
    tela_conteudo.blit(fonte_media.render("DIAGRAMA FASORIAL", True, (200, 200, 255)), (fx+40, fy+5))
    
    # Centro do diagrama
    centro_x = fx + 140
    centro_y = fy + 170
    
    # Eixos
    pygame.draw.line(tela_conteudo, (60, 60, 70), (fx+20, centro_y), (fx+260, centro_y), 1)
    pygame.draw.line(tela_conteudo, (60, 60, 70), (centro_x, fy+40), (centro_x, fy+270), 1)
    pygame.draw.circle(tela_conteudo, (50, 50, 60), (centro_x, centro_y), raio_max, 1)
    
    Xl, Xc, Z, I_amp, phi, _, _, _ = get_valores()
    
    V0_fasor = 5.0
    I_fasor = I_amp
    Vc_fasor = I_amp/(2*np.pi*freq*C) if freq > 0 else 0
    Vl_fasor = I_amp*2*np.pi*freq*L
    
    escala = raio_max / max(V0_fasor, I_fasor*2, Vc_fasor, Vl_fasor, 1)
    
   
    # ===== CORRENTE LIMITADA AO RAIO DO CÍRCULO =====
    
    # Fator para limitar ao raio máximo
    fator_I = raio_max / I_max_ressonancia  # raio_max / 2.5
    
    # Fasor I (CORRENTE) - Referência na horizontal (0°) - CIANO
    ix = min(I_fasor * fator_I, raio_max)  # ← LIMITADO ao raio
    iy = 0
    desenhar_fasor(centro_x, centro_y, ix, iy, CIANO, "I", 3)
    
    # Fasor V (TENSÃO) - Também limitado - AMARELO
    fator_V = raio_max / V0_fasor  # raio_max / 5.0
    vx = min(V0_fasor * fator_V * abs(np.cos(phi)), raio_max) * np.sign(np.cos(phi)) if abs(np.cos(phi)) > 0.001 else 0
    vy = min(V0_fasor * fator_V * abs(np.sin(phi)), raio_max) * np.sign(np.sin(phi)) if abs(np.sin(phi)) > 0.001 else 0
    desenhar_fasor(centro_x, centro_y, vx, -vy, AMARELO, "V", 3)
    
    # Fasor Vc - Adiantado 90° da corrente = para CIMA ↑ - ROXO
    vcx = 0
    vcy = min(Vc_fasor * fator_V, raio_max)  # POSITIVO = para CIMA
    desenhar_fasor(centro_x, centro_y, vcx, vcy, ROXO, "Vc", 2)
    
    # Fasor VL - Atrasado 90° da corrente = para BAIXO ↓ - VERDE
    vlx = 0
    vly = -min(Vl_fasor * fator_V, raio_max)  # NEGATIVO = para BAIXO
    desenhar_fasor(centro_x, centro_y, vlx, vly, VERDE, "VL", 2)
    
    # ===== ARCO DO ÂNGULO PHI =====
    if abs(phi) > 0.05:
        raio_arco = 35
        if phi > 0:
            # Indutivo: V adiantado = arco para CIMA (sentido anti-horário)
            pygame.draw.arc(tela_conteudo, (255, 200, 100), 
                          (centro_x-raio_arco, centro_y-raio_arco, raio_arco*2, raio_arco*2),
                          -phi, 0, 2)
        else:
            # Capacitivo: V atrasado = arco para BAIXO (sentido horário)
            pygame.draw.arc(tela_conteudo, (255, 200, 100), 
                          (centro_x-raio_arco, centro_y-raio_arco, raio_arco*2, raio_arco*2),
                          0, -phi, 2)
    
    # Legenda
    legendas = [
        (f"φ = {np.degrees(phi):.1f}°", (255, 200, 100)),
        (f"I = {I_amp:.2f}A (ref)", CIANO),
        (f"V = {V0_fasor}V", AMARELO),
        (f"Vc = {Vc_fasor:.1f}V", ROXO),
        (f"VL = {Vl_fasor:.1f}V", VERDE),
    ]
    
    y_leg = fy + 220
    for texto, cor in legendas:
        tela_conteudo.blit(fonte_media.render(texto, True, cor), (fx+8, y_leg))
        y_leg += 18
    
def desenhar_fios():
    # Fio superior (horizontal): de 200 a 1000
    for x in range(200, 1000, 8): 
        pygame.draw.line(tela_conteudo, COBRE, (x, 420), (x+8, 420), 3)
    
    # Descida direita: em x=1000
    for y in range(420, 650, 8): 
        pygame.draw.line(tela_conteudo, COBRE, (1000, y), (1000, y+8), 3)
    
    # Fio inferior (retorno): de 200 a 1000
    for x in range(200, 1000, 8): 
        pygame.draw.line(tela_conteudo, COBRE, (x, 650), (x+8, 650), 3)
    
    # Subida esquerda: em x=200
    for y in range(420, 650, 8): 
        pygame.draw.line(tela_conteudo, COBRE, (200, y), (200, y+8), 3)

def desenhar_seta_corrente():
    """Seta de corrente MOVIDA para perto da fonte AC"""
    _, _, _, I_amp, _, i_inst, _, _ = get_valores()
    I_norm = np.clip(i_inst/I_max_ressonancia, -1, 1) if I_max_ressonancia > 0 else 0
    
    # Posição da seta: entre a fonte e o resistor (x=200, y=430)
    x_base = 200
    y_base = 370  # Acima do fio
    
    if abs(I_norm) > 0.02:
        cor = VERMELHO if I_norm > 0 else AZUL
        d = 1 if I_norm > 0 else -1
        comp = int(abs(I_norm) * 100)
        
        # Seta horizontal
        pygame.draw.line(tela_conteudo, cor, (x_base, y_base), (x_base + comp*d, y_base), 6)
        # Ponta da seta
        ponta = x_base + comp*d
        pygame.draw.polygon(tela_conteudo, cor, [
            (ponta, y_base),
            (ponta - 15*d, y_base - 10),
            (ponta - 15*d, y_base + 10)
        ])
        
        # Texto do valor da corrente
        texto = fonte_media.render(f"i = {i_inst:+.3f} A", True, cor)
        tela_conteudo.blit(texto, (x_base + 50, y_base - 30))
    else:
        texto = fonte_media.render("i = 0 A", True, (150, 150, 150))
        tela_conteudo.blit(texto, (x_base + 50, y_base - 30))

def desenhar_particulas():
    _,_,_,_,_,i_inst,_,_ = get_valores()
    v = i_inst/I_max_ressonancia*300 if I_max_ressonancia>0 else 0
    for p in particulas:
        p.x += v*0.016
        
        # Antes:
        # if p.x>1300: p.x=200
        # if p.x<200: p.x=1300
        
        # Depois (limites ajustados para 200 a 1000):
        if p.x > 1000: p.x = 200
        if p.x < 200: p.x = 1000
        
        p.trail.append((p.x, p.y))
        if len(p.trail)>6: p.trail.pop(0)
        for j,(tx,ty) in enumerate(p.trail):
            pygame.draw.circle(tela_conteudo, (0,200,255,int(150*j/len(p.trail))), (int(tx),int(ty)), 2)
        pygame.draw.circle(tela_conteudo, (0,255,255), (int(p.x),int(p.y)), 3)

def desenhar_osciloscopio():
    ox, oy = 1050, 420
    lx, ly = 500, 250
    
    pygame.draw.rect(tela_conteudo, (20,30,20), (ox,oy,lx,ly))
    pygame.draw.rect(tela_conteudo, (60,70,60), (ox,oy,lx,ly), 3)
    
    # Grade
    for gx in range(ox, ox+lx+1, 50):
        pygame.draw.line(tela_conteudo, (30,40,30), (gx,oy), (gx,oy+ly), 1)
    for gy in range(oy, oy+ly+1, 50):
        pygame.draw.line(tela_conteudo, (30,40,30), (ox,gy), (ox+lx,gy), 1)
    
    omega = 2*np.pi*freq
    Z = np.sqrt(R**2+(omega*L-1/(omega*C))**2)
    I_amp = V0/Z
    phi = np.arctan2((omega*L-1/(omega*C)), R)
    
    npts = lx - 40
    t_wave = np.linspace(tempo, tempo+0.04, npts)
    v_wave = V0 * np.sin(omega * t_wave)
    i_wave = I_amp * np.sin(omega * t_wave - phi)
    
    # Tensão (amarelo) - escala: 1V = 20 pixels
    pts_v = [(ox+20+i, max(oy+5, min(oy+ly-5, oy+ly//2 - int(v_wave[i]*20)))) for i in range(npts)]
    if len(pts_v)>1: pygame.draw.lines(tela_conteudo, AMARELO, False, pts_v, 2)
    
    # Corrente (ciano) - escala: 1A = 40 pixels
    pts_i = [(ox+20+i, max(oy+5, min(oy+ly-5, oy+ly//2 - int(i_wave[i]*40)))) for i in range(npts)]
    if len(pts_i)>1: pygame.draw.lines(tela_conteudo, CIANO, False, pts_i, 2)
    
    # Título
    tela_conteudo.blit(fonte_media.render("OSCILOSCOPIO", True, (0,255,0)), (ox+180, oy+5))
    
    # Legenda AMARELA (Tensão)
    pygame.draw.line(tela_conteudo, AMARELO, (ox+10, oy+ly-50), (ox+50, oy+ly-50), 3)
    tela_conteudo.blit(fonte_pequena.render("Tensao da Fonte (V)", True, AMARELO), (ox+55, oy+ly-58))
    tela_conteudo.blit(fonte_pequena.render(f"Amplitude: {V0}V (eixo vertical)", True, (200,200,150)), (ox+55, oy+ly-42))
    
    # Legenda CIANO (Corrente)
    pygame.draw.line(tela_conteudo, CIANO, (ox+10, oy+ly-22), (ox+50, oy+ly-22), 3)
    tela_conteudo.blit(fonte_pequena.render("Corrente (A)", True, CIANO), (ox+55, oy+ly-30))
    tela_conteudo.blit(fonte_pequena.render(f"Amplitude: {I_amp:.2f}A (eixo vertical)", True, (150,200,200)), (ox+55, oy+ly-14))

    # Eixo X: Tempo (posicionado à direita)
    texto_tempo = fonte_media.render("Tempo (ms)", True, (180, 180, 180))
    tela_conteudo.blit(texto_tempo, (ox + lx - texto_tempo.get_width() - 10, oy + ly - 30))
 
def desenhar_curva_ressonancia():
    rx, ry = 1050, 20
    pygame.draw.rect(tela_conteudo, (25,25,35), (rx,ry,500,380))
    pygame.draw.rect(tela_conteudo, (60,60,70), (rx,ry,500,380), 2)
    
    # Eixo X (frequência)
    pygame.draw.line(tela_conteudo, (100,100,100), (rx+50, ry+330), (rx+470, ry+330), 2)
    # Eixo Y (corrente)
    pygame.draw.line(tela_conteudo, (100,100,100), (rx+50, ry+30), (rx+50, ry+330), 2)
    
    # Curva
    freqs_c = np.logspace(1, 2.7, 200)
    I_c = V0/np.sqrt(R**2 + (2*np.pi*freqs_c*L - 1/(2*np.pi*freqs_c*C))**2)
    maxI = max(I_c)
    pts = [(rx+50+i*2, ry+330-int(I_c[i]/maxI*280)) for i in range(len(freqs_c))]
    if len(pts)>1: pygame.draw.lines(tela_conteudo, (100,150,255), False, pts, 3)
    
    # Linha de ressonância
    idx_f0 = np.argmin(np.abs(freqs_c-f0))
    pygame.draw.line(tela_conteudo, (255,80,80), (rx+50+idx_f0*2, ry+30), (rx+50+idx_f0*2, ry+330), 2)
    
    # Ponto atual
    idx = np.argmin(np.abs(freqs_c-freq))
    I_at = V0/np.sqrt(R**2+(2*np.pi*freq*L-1/(2*np.pi*freq*C))**2)
    px, py = rx+50+idx*2, ry+330-int(I_at/maxI*280)
    pygame.draw.circle(tela_conteudo, (255,255,0), (px, py), 10)
    pygame.draw.circle(tela_conteudo, LARANJA, (px, py), 5)
    
    # Barra indicadora de corrente
    barra = int(I_at/maxI*280)
    pygame.draw.rect(tela_conteudo, (255,255,0,100), (rx+460, ry+330-barra, 15, barra))
    
    # Título e legendas dos eixos
    tela_conteudo.blit(fonte_media.render("CURVA DE RESSONANCIA", True, (200,200,255)), (rx+120, ry+10))
    
    # Eixo Y: Corrente (A)
    texto = fonte_media.render("I(A)", True, (200,200,200))
    tela_conteudo.blit(texto, (rx+5, ry+130))
    
    # Eixo X: Frequência (Hz)
    texto = fonte_media.render("F(Hz)", True, (200,200,200))
    tela_conteudo.blit(texto, (rx+220, ry+345))
    
    # Valor da corrente atual
    tela_conteudo.blit(fonte_media.render(f"I = {I_at:.2f} A", True, (255,255,0)), (px-30, py-25))

def desenhar_painel_controle():
    px, py = 20, 700
    pygame.draw.rect(tela_conteudo, (30,35,40), (px,py,1000,220))
    pygame.draw.rect(tela_conteudo, (80,85,90), (px,py,1000,220), 3)
    Xl, Xc, Z, I_amp, phi, i_inst, vc_inst, _ = get_valores()
    
    if abs(freq-f0)<2: status, cor = "*** RESSONANCIA! Xc = Xl ***", VERMELHO
    elif freq<f0: status, cor = "CAPACITIVO: Xc > Xl", ROXO
    else: status, cor = "INDUTIVO: Xl > Xc", VERDE
    
    tela_conteudo.blit(fonte_grande.render(status, True, cor), (px+50, py+15))
    dados = [
        f"f = {freq:.1f} Hz | fn = {f0:.1f} Hz | R = {R:.1f} Ohm",
        f"Xc = {Xc:.1f} Ohm | Xl = {Xl:.1f} Ohm | Z = {Z:.1f} Ohm",
        f"I pico = {I_amp:.3f} A | phi = {np.degrees(phi):.1f} graus",
        f"Velocidade: {velocidade_atual}x mais lento | Zoom: {zoom:.0%}",
    ]
    for i, linha in enumerate(dados):
        tela_conteudo.blit(fonte_media.render(linha, True, (200,200,200)), (px+30, py+70+i*35))

def desenhar_controles():
    x, y = 1050, 730
    controles = [
        "TECLAS 1-6: REDUÇÃO DE VELOCIDADE",
        f"  [1] 1x  [2] 2x  [3] 5x  [4] 10x  [5] 30x  [6] 60x",
        f"  >>> ATUAL: {velocidade_atual}x <<<",
        "",
        "Z/X: Zoom | C: Reset | WASD: Navegar",
        "Setas: Freq/Resist | S: Sweep | Espaco: Pausa",
        "R: Reset | ESC: Sair",
    ]
    for i, txt in enumerate(controles):
        if "ATUAL" in txt: cor = (0,255,0)
        elif "TECLAS" in txt: cor = (255,255,255)
        elif "[" in txt: cor = (200,200,255)
        else: cor = (180,180,180)
        tela_conteudo.blit(fonte_media.render(txt, True, cor), (x, y+i*25))

# ========== Loop principal ==========
rodando = True

while rodando:
    dt_real = clock.tick(60)/1000.0
    
    teclas = pygame.key.get_pressed()
    if zoom > 1.0:
        v = 8/zoom
        if teclas[pygame.K_a]: cam_x -= v
        if teclas[pygame.K_d]: cam_x += v
        if teclas[pygame.K_w]: cam_y -= v
        if teclas[pygame.K_s]: cam_y += v
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: rodando = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: rodando = False
            elif event.key == pygame.K_z: zoom = min(3.0, zoom+0.1)
            elif event.key == pygame.K_x: zoom = max(0.3, zoom-0.1)
            elif event.key == pygame.K_c: zoom = 0.65
            elif event.key in (pygame.K_1, pygame.K_KP1): velocidade_atual = VELOCIDADES[0]; print(f"Velocidade: {velocidade_atual}x")
            elif event.key in (pygame.K_2, pygame.K_KP2): velocidade_atual = VELOCIDADES[1]; print(f"Velocidade: {velocidade_atual}x")
            elif event.key in (pygame.K_3, pygame.K_KP3): velocidade_atual = VELOCIDADES[2]; print(f"Velocidade: {velocidade_atual}x")
            elif event.key in (pygame.K_4, pygame.K_KP4): velocidade_atual = VELOCIDADES[3]; print(f"Velocidade: {velocidade_atual}x")
            elif event.key in (pygame.K_5, pygame.K_KP5): velocidade_atual = VELOCIDADES[4]; print(f"Velocidade: {velocidade_atual}x")
            elif event.key in (pygame.K_6, pygame.K_KP6): velocidade_atual = VELOCIDADES[5]; print(f"Velocidade: {velocidade_atual}x")
            elif event.key == pygame.K_SPACE: pausado = not pausado
            elif event.key == pygame.K_r: freq = f0; auto_sweep = False
            elif event.key == pygame.K_s: auto_sweep = not auto_sweep
            elif event.key == pygame.K_UP: freq = min(500, freq+5); auto_sweep = False
            elif event.key == pygame.K_DOWN: freq = max(10, freq-5); auto_sweep = False
            elif event.key == pygame.K_RIGHT: R = min(20, R+0.5)
            elif event.key == pygame.K_LEFT: R = max(0.5, R-0.5)
    
    if auto_sweep and not pausado:
        freq += sweep_dir*1.5
        if freq >= 500: sweep_dir = -1
        elif freq <= 10: sweep_dir = 1
    
    if not pausado:
        tempo += dt_real / velocidade_atual
    
    tela_conteudo.fill(FUNDO)
    desenhar_grade()
    desenhar_painel_equacoes()
    desenhar_fasores()
    desenhar_fios()
    desenhar_particulas()
    desenhar_resistor(330, 400)
    desenhar_fonte_ac(130, 420)
    desenhar_indutor(550, 405)
    desenhar_capacitor(800, 408)
    desenhar_seta_corrente()  # Agora desenha perto da fonte
    desenhar_osciloscopio()
    desenhar_curva_ressonancia()
    desenhar_painel_controle()
    desenhar_controles()
    
    if pausado:
        texto_pausa = fonte_grande.render("PAUSADO", True, (255, 255, 0))
        tela_conteudo.blit(texto_pausa, (LARGURA_CONTEUDO//2 - texto_pausa.get_width()//2, ALTURA_CONTEUDO//2 - 120))

    if auto_sweep:
        texto_sweep = fonte_grande.render("AUTO-SWEEP", True, (0, 255, 0))
        tela_conteudo.blit(texto_sweep, (LARGURA_CONTEUDO//2 - texto_sweep.get_width()//2, ALTURA_CONTEUDO//2 + 20))
    
    if zoom <= 1.0:
        nt = (int(LARGURA_CONTEUDO*zoom), int(ALTURA_CONTEUDO*zoom))
        tr = pygame.transform.smoothscale(tela_conteudo, nt)
        tela.fill((0,0,0))
        tela.blit(tr, ((LARGURA_JANELA-nt[0])//2, (ALTURA_JANELA-nt[1])//2))
    else:
        lv, av = int(LARGURA_JANELA/zoom), int(ALTURA_JANELA/zoom)
        cam_x = max(0, min(cam_x, LARGURA_CONTEUDO-lv))
        cam_y = max(0, min(cam_y, ALTURA_CONTEUDO-av))
        lv, av = min(lv, LARGURA_CONTEUDO-int(cam_x)), min(av, ALTURA_CONTEUDO-int(cam_y))
        if lv>0 and av>0:
            try:
                avis = tela_conteudo.subsurface((int(cam_x),int(cam_y),lv,av))
                tela.blit(pygame.transform.smoothscale(avis, (LARGURA_JANELA,ALTURA_JANELA)), (0,0))
            except: tela.blit(tela_conteudo, (0,0))
    
    pygame.display.flip()

pygame.quit()


# In[ ]:





# In[ ]:




