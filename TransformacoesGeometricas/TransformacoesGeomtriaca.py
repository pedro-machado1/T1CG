# ***********************************************************************************
#   ExibePoligonos.py
#       Autor: Márcio Sarroglia Pinho
#       pinho@pucrs.br
#   Este programa cria um conjunto de INSTANCIAS
#   Para construir este programa, foi utilizada a biblioteca PyOpenGL, disponível em
#   http://pyopengl.sourceforge.net/documentation/index.html
#
#   Sugere-se consultar também as páginas listadas
#   a seguir:
#   http://bazaar.launchpad.net/~mcfletch/pyopengl-demo/trunk/view/head:/PyOpenGL-Demo/NeHe/lesson1.py
#   http://pyopengl.sourceforge.net/documentation/manual-3.0/index.html#GLUT
#
#   No caso de usar no MacOS, pode ser necessário alterar o arquivo ctypesloader.py,
#   conforme a descrição que está nestes links:
#   https://stackoverflow.com/questions/63475461/unable-to-import-opengl-gl-in-python-on-macos
#   https://stackoverflow.com/questions/6819661/python-location-on-mac-osx
#   Veja o arquivo Patch.rtf, armazenado na mesma pasta deste fonte.
# ***********************************************************************************

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Poligonos import *
from Instancia import *
from ModeloMatricial import *
from ListaDeCoresRGB import *
from datetime import datetime
import time
import random
import copy

# ***********************************************************************************

# Modelos de Objetos
MeiaSeta = Polygon()
Mastro = Polygon()

# Limites da Janela de Seleção
Min = Ponto()
Max = Ponto()

# lista de instancias do Personagens
Personagens = [Instancia() for x in range(100)]

AREA_DE_BACKUP = 50 # posicao a partir da qual sao armazenados backups dos personagens

# lista de modelos
Modelos = []

vida = 3
nInimigos = 20
#  implementar
invencibilidade = False
angulo = 0.0
PersonagemAtual = -1
nInstancias = 0

imprimeEnvelope = False

LarguraDoUniverso = 10.0

TempoInicial = time.time()
TempoTotal = time.time()
TempoAnterior = time.time()
TempoAux = time.time()
TempoVelocidade = time.time()

invencibilidade = TempoInicial - 3

# invencibilidade: tempo mínimo entre danos consecutivos (segundos)
INVENCIBILITY_DURATION = 3.0
invencibilidade_last = 0.0

# flags para estado das teclas especiais (manter entradas enquanto pressionadas)
keyUpPressed = False
keyDownPressed = False
keyLeftPressed = False
keyRightPressed = False

# define uma funcao de limpeza de tela
from os import system, name
def clear():
 
    # for windows
    if name == 'nt':
        _ = system('cls')
 
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')
        print("*******************")
        print ("PWD: ", os.getcwd()) 
        
def DesenhaLinha (P1, P2):
    glBegin(GL_LINES)
    glVertex3f(P1.x,P1.y,P1.z)
    glVertex3f(P2.x,P2.y,P2.z)
    glEnd()

# ****************************************************************
def RotacionaAoRedorDeUmPonto(alfa: float, P: Ponto):
    glTranslatef(P.x, P.y, P.z)
    glRotatef(alfa, 0,0,1)
    glTranslatef(-P.x, -P.y, -P.z)

# ***********************************************************************************
def reshape(w,h):

    global Min, Max
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Cria uma folga na Janela de Selecao, com 10% das dimensoes do poligono
    BordaX = abs(Max.x-Min.x)*0.1
    BordaY = abs(Max.y-Min.y)*0.1
    #glOrtho(Min.x-BordaX, Max.x+BordaX, Min.y-BordaY, Max.y+BordaY, 0.0, 1.0)
    glOrtho(Min.x, Max.x, Min.y, Max.y, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

# ***********************************************************************************
def DesenhaMastro():
    Mastro.desenhaPoligono()

# ***********************************************************************************
def DesenhaSeta():
    glPushMatrix()
    MeiaSeta.desenhaPoligono()
    glScaled(1,-1, 1)
    MeiaSeta.desenhaPoligono()
    glPopMatrix()

# ***********************************************************************************
def DesenhaApontador():
    glPushMatrix()
    glTranslated(-4, 0, 0)
    DesenhaSeta()
    glPopMatrix()
# **********************************************************************
def DesenhaHelice():
    glPushMatrix()
    for i in range (4):   
        glRotatef(90, 0, 0, 1)
        DesenhaApontador()
    glPopMatrix()

# ***********************************************************************************
def DesenhaHelicesGirando():
    global angulo
    #print ("angulo:", angulo)
    glPushMatrix()
    glRotatef(angulo, 0, 0, 1)
    DesenhaHelice()
    glPopMatrix()

# ***********************************************************************************
def DesenhaCatavento():
    #glLineWidth(3)
    glPushMatrix()
    DesenhaMastro()
    glPushMatrix()
    glColor3f(1,0,0)
    glTranslated(0,3,0)
    glScaled(0.2, 0.2, 1)
    DesenhaHelicesGirando()
    glPopMatrix()
    glPopMatrix()

# **************************************************************
def DesenhaEixos():
    global Min, Max

    Meio = Ponto(); 
    Meio.x = (Max.x+Min.x)/2
    Meio.y = (Max.y+Min.y)/2
    Meio.z = (Max.z+Min.z)/2

    glBegin(GL_LINES)
    #  eixo horizontal
    glVertex2f(Min.x,Meio.y)
    glVertex2f(Max.x,Meio.y)
    #  eixo vertical
    glVertex2f(Meio.x,Min.y)
    glVertex2f(Meio.x,Max.y)
    glEnd()

# ***********************************************************************************
def TestaColisao(P1, P2) -> bool :

    # cout << "\n-----\n" << endl;
    # Personagens[Objeto1].ImprimeEnvelope("Envelope 1: ", "\n");
    # Personagens[Objeto2].ImprimeEnvelope("\nEnvelope 2: ", "\n");
    # cout << endl;

    # Testa todas as arestas do envelope de
    # um objeto contra as arestas do outro
       
    for i in range(4):
        A = Personagens[P1].Envelope[i]
        B = Personagens[P1].Envelope[(i+1)%4]
        for j in range(4):
            # print ("Testando ", i," contra ",j)
            # Personagens[Objeto1].ImprimeEnvelope("\nEnvelope 1: ", "\n");
            # Personagens[Objeto2].ImprimeEnvelope("Envelope 2: ", "\n");
            C = Personagens[P2].Envelope[j]
            D = Personagens[P2].Envelope[(j+1)%4]
            # A.imprime("A:","\n");
            # B.imprime("B:","\n");
            # C.imprime("C:","\n");
            # D.imprime("D:","\n\n");    
            if HaInterseccao(A, B, C, D):
                return True
    return False


# nova função para remover uma instância rapidamente (swap-delete)
def RemoveInstancia(idx):
    global nInstancias, nInimigos, Personagens, AREA_DE_BACKUP
    if idx < 0 or idx >= nInstancias:
        return
    # detecta se a instância removida é um inimigo (modelos 2..5)
    isEnemy = Personagens[idx].IdDoModelo in (2,3,4,5)
    last = nInstancias - 1
    if idx != last:
        # copia última instância para o local removido (deep copy para preservar objetos separados)
        Personagens[idx] = copy.deepcopy(Personagens[last])
        # copia também a área de backup correspondente, se existir
        if last + AREA_DE_BACKUP < len(Personagens) and idx + AREA_DE_BACKUP < len(Personagens):
            Personagens[idx+AREA_DE_BACKUP] = copy.deepcopy(Personagens[last+AREA_DE_BACKUP])
    # limpa o último slot (substitui por nova Instancia)
    Personagens[last] = Instancia()
    if last + AREA_DE_BACKUP < len(Personagens):
        Personagens[last+AREA_DE_BACKUP] = Instancia()
    nInstancias -= 1
    if isEnemy:
        # decrementa contador de inimigos se controlado pelo jogo
        try:
            nInimigos = max(0, nInimigos - 1)
        except Exception:
            pass

# ***********************************************************************************
def AtualizaEnvelope(i):
    global Personagens
    P = Personagens[i]
    id = Personagens[i].IdDoModelo
    MM = Modelos[id]

    pivo = Ponto(-P.Pivot.x, -P.Pivot.y)
    pivo.rotacionaZ(P.Rotacao)

    V = P.Direcao * (MM.nColunas/2.0)
    V.rotacionaZ(90)
    A = P.PosicaoDoPersonagem + pivo
    B = A + P.Direcao*MM.nLinhas
    
    V = P.Direcao * MM.nColunas
    V.rotacionaZ(-90)
    C = B + V

    V = P.Direcao * -1 * MM.nLinhas
    D = C + V

    # Desenha o envelope
    SetColor(Red)
    glBegin(GL_LINE_LOOP)
    glVertex2f(A.x, A.y)
    glVertex2f(B.x, B.y)
    glVertex2f(C.x, C.y)
    glVertex2f(D.x, D.y)
    glEnd()
    # if (imprimeEnvelope):
    #     A.imprime("A:");
    #     B.imprime("B:");
    #     C.imprime("C:");
    #     D.imprime("D:");
    #     print("");

    Personagens[i].Envelope[0] = A
    Personagens[i].Envelope[1] = B
    Personagens[i].Envelope[2] = C
    Personagens[i].Envelope[3] = D

# ***********************************************************************************
# Gera sempre uma posicao na metade de baixo da tela
def GeraPosicaoAleatoria():
        x = random.randint(-LarguraDoUniverso, LarguraDoUniverso)
        y = random.randint(-LarguraDoUniverso, 0)
        return Ponto (x,y)


# ***********************************************************************************
def AtualizaJogo():
    global imprimeEnvelope, nInstancias, Personagens, vida, nInimigos, invencibilidade

    timer, numInimigo = 0, 1 

    #  Esta funcao deverá atualizar todos os elementos do jogo
    #  em funcao das novas posicoes dos personagens
    #  Entre outras coisas, deve-se:
    
    #   - calcular colisões
    #  Para calcular as colisoes eh preciso fazer o calculo do envelopes de
    #  todos os personagens

    for i in range (0, nInstancias):
        AtualizaEnvelope(i) 
        if (imprimeEnvelope): # pressione E para alterar esta flag
            print("Envelope ", i)
            Personagens[i].ImprimeEnvelope("","")
    imprimeEnvelope = False

    # Colisões projétil (IdDoModelo == 1) x inimigo (IdDoModelo in 2..5)
    # removemos ambos imediatamente; removendo índice maior primeiro
    b = 1
    while b < nInstancias:
        if Personagens[b].IdDoModelo != 1:
            b += 1
            continue
        j = 1
        collided = False
        while j < nInstancias:
            if Personagens[j].IdDoModelo in (2,3,4,5):
                if TestaColisao(b, j):
                    hi = max(b, j)
                    lo = min(b, j)
                    RemoveInstancia(hi)
                    RemoveInstancia(lo)
                    collided = True
                    break
            j += 1
        if not collided:
            b += 1
    global invencibilidade_last
    for i in range (1, nInstancias):
        if TestaColisao(0, i):
            agora = time.time()
            # só aplica dano se já passou o tempo de invencibilidade
            if (agora - invencibilidade_last) >= INVENCIBILITY_DURATION:
                invencibilidade_last = agora
                vida -= 1
                print("Player atingido. Vidas:", vida)
                if (vida == 0):
                    print("Perdeu")
                    os._exit(0)
            else:
                # em invencibilidade, ignora colisão
                pass
    #  definir qnts inimigos vai ter 
    # nInimigos = 30  # falso 
    # for inimigo in range (1, nInimigos) :
    #     for i in range (inimigo, nInstancias) : 
    #         if (TestaColisao(inimigo, i)) : 
    #             Personagens[inimigo] = None
    #             Personagens[i] = None
    # 
    # if (timer == 20) : 
    #     if (numInimigo >= 20) : 
    #         numInimigo = 0
    #     timer = 0
    #     atirar(numInimigo)
    #     numInimigo += 1
    
    dx, dy = Personagens[0].Direcao.x, Personagens[0].Direcao.y
    mod = Personagens[0].Rotacao % 360
    P = Personagens[0]
    if P.Posicao.x > 15:
        P.Posicao.x = 15
        P.Direcao.x *= -1
        P.Rotacao = ((math.degrees(math.atan2(P.Direcao.y, P.Direcao.x))) % 360) - 90
        print(P.Rotacao)

    elif P.Posicao.x < -20:
        P.Posicao.x = -20
        P.Direcao.x *= -1
        P.Rotacao = ((math.degrees(math.atan2(P.Direcao.y, P.Direcao.x))) % 360) - 90
        print(P.Rotacao)


    elif P.Posicao.y > 17:
        P.Posicao.y = 17
        P.Direcao.y *= -1
        P.Rotacao = ((math.degrees(math.atan2(P.Direcao.y, P.Direcao.x))) % 360) - 90
        print(P.Rotacao)


    elif P.Posicao.y < -17:
        P.Posicao.y = -17
        P.Direcao.y *= -1
        P.Rotacao = ((math.degrees(math.atan2(P.Direcao.y, P.Direcao.x))) % 360) - 90
        print(P.Rotacao)

        # timer += 1
    #     else:
            # pass
            # print ("SEM Colisao")
        
    # Faz inimigos (modelos 2..5) quicarem nas bordas igual a nave principal
    for i in range(1, nInstancias):
        P = Personagens[i]
        if P.IdDoModelo not in (2,3,4,5):
            continue
        dx, dy = P.Direcao.x, P.Direcao.y
        mod = P.Rotacao % 360
        if P.Posicao.x > 15:
            P.Posicao.x = 15
            
            
            P.Direcao.x *= -1
            P.Rotacao = ((math.degrees(math.atan2(P.Direcao.y, P.Direcao.x))) % 360) - 90
            print(P.Rotacao)

        elif P.Posicao.x < -20:
            P.Posicao.x = -20
            P.Direcao.x *= -1
            P.Rotacao = ((math.degrees(math.atan2(P.Direcao.y, P.Direcao.x))) % 360) - 90
            print(P.Rotacao)


        elif P.Posicao.y > 17:
            P.Posicao.y = 17
            P.Direcao.y *= -1
            P.Rotacao = ((math.degrees(math.atan2(P.Direcao.y, P.Direcao.x))) % 360) - 90
            print(P.Rotacao)


        elif P.Posicao.y < -17:
            P.Posicao.y = -17
            P.Direcao.y *= -1
            P.Rotacao = ((math.degrees(math.atan2(P.Direcao.y, P.Direcao.x))) % 360) - 90
            print(P.Rotacao)


# ***********************************************************************************
def AtualizaPersonagens(tempoDecorrido):
    global nInstancias
    global keyUpPressed, keyDownPressed, keyLeftPressed, keyRightPressed, TempoVelocidade
    # aplica entradas contínuas do jogador (instância 0)
    if nInstancias > 0:
        P0 = Personagens[0]
        # acelera enquanto a tecla CIMA estiver segurada
        if keyUpPressed:
            accel = 3.0  # ajuste conforme desejado (unidades por segundo^2)
            P0.Velocidade += accel * tempoDecorrido
            if P0.Velocidade > 5:
                P0.Velocidade = 5
            TempoVelocidade = time.time()
        else:
            # desaceleração (fricção) quando não está apertando CIMA
            decel = 4.0
            P0.Velocidade -= decel * tempoDecorrido
            if P0.Velocidade < 0:
                P0.Velocidade = 0
        # rotação contínua enquanto ESQ/DIR estiverem seguradas
        if keyLeftPressed or keyRightPressed:
            angSpeed = 180.0  # graus por segundo (ajuste)
            dir_sign = 0
            if keyLeftPressed:
                dir_sign += 1
            if keyRightPressed:
                dir_sign -= 1
            deltaAng = angSpeed * tempoDecorrido * dir_sign
            P0.Rotacao = (P0.Rotacao + deltaAng) % 360
            # gira o vetor direção incrementalmente (metodo existente em Ponto)
            P0.Direcao.rotacionaZ(deltaAng)
            TempoVelocidade = time.time()
    # atualiza todas as instâncias normalmente
    for i in range (0, nInstancias):
       Personagens[i].AtualizaPosicao(tempoDecorrido)
    AtualizaJogo()
    InimigoController()

# ***********************************************************************************
def DesenhaPersonagens():
    global PersonagemAtual, nInstancias
    
    for i in range (0, nInstancias):
        PersonagemAtual = i
        Personagens[i].Desenha()
        
# ***********************************************************************************
def display():

    global TempoInicial, TempoTotal, TempoAnterior

    TempoAtual = time.time()

    TempoTotal =  TempoAtual - TempoInicial

    DiferencaDeTempo = TempoAtual - TempoAnterior

	# Limpa a tela coma cor de fundo
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    #glLineWidth(3)
    glColor3f(1,1,1) # R, G, B  [0..1]
    DesenhaEixos()

    DesenhaPersonagens()
    AtualizaPersonagens(DiferencaDeTempo)
    
    glutSwapBuffers()
    TempoAnterior = TempoAtual

# ***********************************************************************************
# The function called whenever a key is pressed. 
# Note the use of Python tuples to pass in: (key, x, y)
#ESCAPE = '\033'
ESCAPE = b'\x1b'
def keyboard(*args):
    global imprimeEnvelope
    print (args)
    # If escape is pressed, kill everything.
    if args[0] == b'q':
        os._exit(0)
    if args[0] == ESCAPE:
        os._exit(0)
    if args[0] == b'e':
        imprimeEnvelope = True
    if args[0] == b' ':
        atirar(0)
# Forca o redesenho da tela
    glutPostRedisplay()

# **********************************************************************
#  arrow_keys ( a_keys: int, x: int, y: int )   
# **********************************************************************
def arrow_keys(a_keys: int, x: int, y: int):
    # marca tecla especial como pressionada; AtualizaPersonagens aplica o efeito contínuo
    global keyUpPressed, keyDownPressed, keyLeftPressed, keyRightPressed
    if a_keys == GLUT_KEY_UP:
        keyUpPressed = True
    elif a_keys == GLUT_KEY_DOWN:
        keyDownPressed = True
    elif a_keys == GLUT_KEY_LEFT:
        keyLeftPressed = True
    elif a_keys == GLUT_KEY_RIGHT:
        keyRightPressed = True
    glutPostRedisplay()

def special_key_up(a_keys: int, x: int, y: int):
    # limpa flags quando tecla especial for solta
    global keyUpPressed, keyDownPressed, keyLeftPressed, keyRightPressed
    if a_keys == GLUT_KEY_UP:
        keyUpPressed = False
    elif a_keys == GLUT_KEY_DOWN:
        keyDownPressed = False
    elif a_keys == GLUT_KEY_LEFT:
        keyLeftPressed = False
    elif a_keys == GLUT_KEY_RIGHT:
        keyRightPressed = False
    glutPostRedisplay()

# ***********************************************************************************
#
# ***********************************************************************************
def mouse(button: int, state: int, x: int, y: int):
    global PontoClicado
    if (state != GLUT_DOWN): 
        return
    if (button != GLUT_RIGHT_BUTTON):
        return
    #print ("Mouse:", x, ",", y)
    # Converte a coordenada de tela para o sistema de coordenadas do 
    # Personagens definido pela glOrtho
    vport = glGetIntegerv(GL_VIEWPORT)
    mvmatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
    projmatrix = glGetDoublev(GL_PROJECTION_MATRIX)
    realY = vport[3] - y
    worldCoordinate1 = gluUnProject(x, realY, 0, mvmatrix, projmatrix, vport)

    PontoClicado = Ponto (worldCoordinate1[0],worldCoordinate1[1], worldCoordinate1[2])
    PontoClicado.imprime("Ponto Clicado:")

    glutPostRedisplay()

# ***********************************************************************************
def mouseMove(x: int, y: int):
    #glutPostRedisplay()
    return

# ***********************************************************************************
def CarregaModelos():
    global MeiaSeta, Mastro
    MeiaSeta.LePontosDeArquivo("MeiaSeta.txt")
    Mastro.LePontosDeArquivo("Mastro.txt")

    Modelos.append(ModeloMatricial())
    Modelos[0].leModelo("Nave.txt");
    Modelos.append(ModeloMatricial())
    Modelos[1].leModelo("MatrizProjetil.txt");
    Modelos.append(ModeloMatricial())
    Modelos[2].leModelo("Inimigo1.txt");
    Modelos.append(ModeloMatricial())
    Modelos[3].leModelo("Inimigo2.txt");
    Modelos.append(ModeloMatricial())
    Modelos[4].leModelo("Inimigo3.txt");
    Modelos.append(ModeloMatricial())
    Modelos[5].leModelo("Inimigo4.txt");

    print ("Modelo 0");
    Modelos[0].Imprime()
    print ("Modelo 1");
    Modelos[1].Imprime()
    print ("Modelo 2");
    Modelos[2].Imprime()
    print ("Modelo 3");
    Modelos[3].Imprime()
    print ("Modelo 4");
    Modelos[4].Imprime()
    print ("Modelo 5");
    Modelos[5].Imprime()

def DesenhaCelula():
    glBegin(GL_QUADS)
    glVertex2f(0,0)
    glVertex2f(0,1)
    glVertex2f(1,1)
    glVertex2f(1,0)
    glEnd()
    pass

def DesenhaBorda():
    glBegin(GL_LINE_LOOP)
    glVertex2f(0,0)
    glVertex2f(0,1)
    glVertex2f(1,1)
    glVertex2f(1,0)
    glEnd()

# ***********************************************************************************
def DesenhaPersonagemMatricial():
    global PersonagemAtual

    MM = ModeloMatricial()
    
    ModeloDoPersonagem = Personagens[PersonagemAtual].IdDoModelo
        
    MM = Modelos[ModeloDoPersonagem]
    # MM.Imprime("Matriz:")
      
    glPushMatrix()
    larg = MM.nColunas
    alt = MM.nLinhas
    # print (alt, " LINHAS e ", larg, " COLUNAS")
    for i in range(alt):
        glPushMatrix()
        for j in range(larg):
            cor = MM.getColor(alt-1-i,j)
            if cor != -1: # nao desenha celulas com -1 (transparentes)
                SetColor(cor)
                DesenhaCelula()
                SetColor(Wheat)
                DesenhaBorda()
            glTranslatef(1, 0, 0)
        glPopMatrix()
        glTranslatef(0, 1, 0)
    glPopMatrix()



# ***********************************************************************************
# Esta função deve instanciar todos os personagens do cenário
# ***********************************************************************************
def CriaInstancias():
    global Personagens, nInstancias

    i = 0
    ang = 270.0
    #Personagens.append(Instancia())
    Personagens[i].Posicao = Ponto (-2.5,0)
    Personagens[i].Escala = Ponto (1,1)
    Personagens[i].Rotacao = ang
    Personagens[i].IdDoModelo = 0
    Personagens[i].Modelo = DesenhaPersonagemMatricial
    Personagens[i].Pivot = Ponto(2.5,0)
    Personagens[i].Direcao = Ponto(0,1) # direcao do movimento para a cima
    Personagens[i].Direcao.rotacionaZ(ang) # direcao alterada para a direita
    Personagens[i].Velocidade = 0 # jogador começa parado

    # Salva os dados iniciais do personagem i na area de backup
    Personagens[i+AREA_DE_BACKUP] = copy.deepcopy(Personagens[i]) 
    nInstancias = i + 1
    
    i += 1 
    #Personagens[0].ImprimeEnvelope("Envelope:")

    ang = 0
    Personagens[i].Posicao = Ponto (13.5,0)
    Personagens[i].Escala = Ponto (1,1)
    Personagens[i].Rotacao = ang
    Personagens[i].IdDoModelo = 2
    Personagens[i].Modelo = DesenhaPersonagemMatricial
    Personagens[i].Pivot = Ponto(1.5,0)
    Personagens[i].Direcao = Ponto(0,1) # direcao do movimento para a cima
    Personagens[i].Direcao.rotacionaZ(ang) # direcao alterada para a direita
    Personagens[i].Velocidade = 5   # move-se a 3 m/s

    # Salva os dados iniciais do personagem i na area de backup
    Personagens[i+AREA_DE_BACKUP] = copy.deepcopy(Personagens[i]) 
    nInstancias = i+1

    # i += 1 
    # #Personagens[0].ImprimeEnvelope("Envelope:")

    # ang = 90
    # Personagens[i].Posicao = Ponto (5,5)
    # Personagens[i].Escala = Ponto (1,1)
    # Personagens[i].Rotacao = ang
    # Personagens[i].IdDoModelo = 3
    # Personagens[i].Modelo = DesenhaPersonagemMatricial
    # Personagens[i].Pivot = Ponto(2.5,0)
    # Personagens[i].Direcao = Ponto(0,1) # direcao do movimento para a cima
    # Personagens[i].Direcao.rotacionaZ(ang) # direcao alterada para a direita
    # Personagens[i].Velocidade = 5   # move-se a 3 m/s

    # # Salva os dados iniciais do personagem i na area de backup
    # Personagens[i+AREA_DE_BACKUP] = copy.deepcopy(Personagens[i]) 
    # nInstancias = i+1

    # i += 1 
    # #Personagens[0].ImprimeEnvelope("Envelope:")

    # ang = 90
    # Personagens[i].Posicao = Ponto (-10,-3)
    # Personagens[i].Escala = Ponto (1,1)
    # Personagens[i].Rotacao = ang
    # Personagens[i].IdDoModelo = 4
    # Personagens[i].Modelo = DesenhaPersonagemMatricial
    # Personagens[i].Pivot = Ponto(2.5,0)
    # Personagens[i].Direcao = Ponto(0,1) # direcao do movimento para a cima
    # Personagens[i].Direcao.rotacionaZ(ang) # direcao alterada para a direita
    # Personagens[i].Velocidade = 5   # move-se a 3 m/s

    # # Salva os dados iniciais do personagem i na area de backup
    # Personagens[i+AREA_DE_BACKUP] = copy.deepcopy(Personagens[i]) 
    # nInstancias = i+1



def atirar(num):
    global nInstancias, Personagens
    i = nInstancias


#  fzr pela rotação
    print(Personagens[num].Direcao.x)
    print(Personagens[num].Direcao.y)

    mod = Personagens[num].Rotacao % 360
    ang = mod % 90 
    

    x, y = 0, 0 

#  é algo assim 

    if (mod < 90) :
        x = Personagens[num].Posicao.x + (5 * Personagens[num].Direcao.x)
        print(Personagens[num].Direcao.x)
        y = Personagens[num].Posicao.y  + ( 3 * Personagens[num].Direcao.y)
        print(Personagens[num].Direcao.y)
    elif (mod < 180) :
        x = Personagens[num].Posicao.x + (4 * Personagens[num].Direcao.x)
        print(4 * Personagens[num].Direcao.x)
        y = Personagens[num].Posicao.y  + (6 * Personagens[num].Direcao.y)
        print(6 * Personagens[num].Direcao.y)
    elif (mod < 270) :
        x = Personagens[num].Posicao.x + (4 * Personagens[num].Direcao.x)
        print(4 * Personagens[num].Direcao.x)
        y = Personagens[num].Posicao.y  + (6 * Personagens[num].Direcao.y)
        print(6 * Personagens[num].Direcao.y)
    else :
        x = Personagens[num].Posicao.x + (4 * Personagens[num].Direcao.x)
        print(4 * Personagens[num].Direcao.x)
        y = Personagens[num].Posicao.y  + (6 * Personagens[num].Direcao.y)
        print(6 * Personagens[num].Direcao.y)


    # posição inicial do tiro
    Personagens[i].Posicao = Ponto(Personagens[num].Direcao.x + Personagens[num].Posicao.x, Personagens[num].Direcao.y + Personagens[num].Posicao.y ) 
    Personagens[i].Escala = Ponto (1,1)
    Personagens[i].Rotacao = Personagens[num].Rotacao
    Personagens[i].IdDoModelo = 1
    Personagens[i].Modelo = DesenhaPersonagemMatricial
    Personagens[i].Pivot = Ponto(0.5,0)
    Personagens[i].Direcao = Ponto(Personagens[num].Direcao.x, Personagens[num].Direcao.y) 
    # Personagens[i].Direcao.rotacionaZ(ang) 
    Personagens[i].Velocidade = 4

    Personagens[i+AREA_DE_BACKUP] = copy.deepcopy(Personagens[i]) 
    nInstancias = i+1

# aqui criar funcão para inimigos


# instanciar  n fzr logica 
def InimigoController() :
    global nInstancias, TempoInicial, TempoAnterior, TempoAux

    TempoAtual = time.time()

    DiferencaDeTempo =  TempoAtual - TempoAux

    


    if (DiferencaDeTempo >= 5) :
        TempoAux = time.time()
        nInstancias += 1
        n1 = random.randint(1, 4)
        n2 = random.randint(-20, 20)

        Personagens[nInstancias].Escala = Ponto (1,1)
        if (n1 == 1) : 
            Personagens[nInstancias].Posicao = Ponto (n2,15)
            ang = 180
        elif (n1 == 2 ) : 
            Personagens[nInstancias].Posicao = Ponto (n2, -15)
            ang = 0
        elif (n1 == 3 ) : 
            Personagens[nInstancias].Posicao = Ponto (15, n2)
            ang = 90 
        else : 
            Personagens[nInstancias].Posicao = Ponto (-15, n2)
            ang = 270
        
        n1 = random.randint(1,4) 
        if (n1 == 1) : 
            Personagens[nInstancias].IdDoModelo = 2
            Personagens[nInstancias].Rotacao = ang
            Personagens[nInstancias].Modelo = DesenhaPersonagemMatricial
            Personagens[nInstancias].Pivot = Ponto(-1.5,0)
            Personagens[nInstancias].Direcao = Ponto(0,1) # direcao do movimento para a cima
            Personagens[nInstancias].Direcao.rotacionaZ(ang) # direcao alterada para a direita
            Personagens[nInstancias].Velocidade = 1   # move-se a 3 m/s

            # Salva os dados iniciais do personagem i na area de backup
            Personagens[nInstancias+AREA_DE_BACKUP] = copy.deepcopy(Personagens[nInstancias]) 
        
        if (n1 == 2) : 
            Personagens[nInstancias].IdDoModelo = 3
            Personagens[nInstancias].Rotacao = ang
            Personagens[nInstancias].Modelo = DesenhaPersonagemMatricial
            Personagens[nInstancias].Pivot = Ponto(1,0)
            Personagens[nInstancias].Direcao = Ponto(0,1) # direcao do movimento para a cima
            Personagens[nInstancias].Direcao.rotacionaZ(ang) # direcao alterada para a direita
            Personagens[nInstancias].Velocidade = 5   # move-se a 3 m/s

            # Salva os dados iniciais do personagem i na area de backup
            Personagens[nInstancias+AREA_DE_BACKUP] = copy.deepcopy(Personagens[nInstancias]) 
        
        if (n1 == 3) : 
            Personagens[nInstancias].IdDoModelo = 5
            Personagens[nInstancias].Rotacao = ang
            Personagens[nInstancias].Modelo = DesenhaPersonagemMatricial
            Personagens[nInstancias].Pivot = Ponto(1,0)
            Personagens[nInstancias].Direcao = Ponto(0,1) # direcao do movimento para a cima
            Personagens[nInstancias].Direcao.rotacionaZ(ang) # direcao alterada para a direita
            Personagens[nInstancias].Velocidade = 2   # move-se a 3 m/s

            # Salva os dados iniciais do personagem i na area de backup
            Personagens[nInstancias+AREA_DE_BACKUP] = copy.deepcopy(Personagens[nInstancias]) 
        
        
        if (n1 == 4) : 
            Personagens[nInstancias].IdDoModelo = 4
            Personagens[nInstancias].Rotacao = ang
            Personagens[nInstancias].Modelo = DesenhaPersonagemMatricial
            Personagens[nInstancias].Pivot = Ponto(2.5,0)
            Personagens[nInstancias].Direcao = Ponto(0,1) # direcao do movimento para a cima
            Personagens[nInstancias].Direcao.rotacionaZ(ang) # direcao alterada para a direita
            Personagens[nInstancias].Velocidade = 3   # move-se a 3 m/s

            # Salva os dados iniciais do personagem i na area de backup
            Personagens[nInstancias+AREA_DE_BACKUP] = copy.deepcopy(Personagens[nInstancias]) 

        print("chegou")

# ***********************************************************************************
def init():
    global Min, Max
    global TempoInicial, LarguraDoUniverso
    # Define a cor do fundo da tela (AZUL)
    glClearColor(0, 0, 1, 1)
    
    clear() # limpa o console
    CarregaModelos()
    CriaInstancias()

    LarguraDoUniverso = 20
    Min = Ponto(-LarguraDoUniverso,-LarguraDoUniverso)
    Max = Ponto(LarguraDoUniverso,LarguraDoUniverso)

    TempoInicial = time.time()
    print("Inicio: ", datetime.now())
    print("TempoInicial", TempoInicial)

def animate():
    global angulo
    angulo = angulo + 1
    glutPostRedisplay()

# ***********************************************************************************
# Programa Principal
# ***********************************************************************************

glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA)
# Define o tamanho inicial da janela grafica do programa
glutInitWindowSize(500, 500)
glutInitWindowPosition(100, 100)
wind = glutCreateWindow(b"Exemplo de Criacao de Instancias")
glutDisplayFunc(display)
glutIdleFunc(animate)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutSpecialFunc(arrow_keys)
glutSpecialUpFunc(special_key_up)
glutMouseFunc(mouse)
init()

try:
    glutMainLoop()
except SystemExit:
    pass