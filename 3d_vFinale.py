# pip install PyOpenGL

import pygame
import random
import math
from math import cos,sin
import time
import os
import inspect
import numpy as np

from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import *

screenwidth = 1000
screenheight = 800

#recherche du répertoire de travail
scriptPATH = os.path.abspath(inspect.getsourcefile(lambda:0)) # compatible interactive Python Shell
scriptDIR  = os.path.dirname(scriptPATH)
assets = os.path.join(scriptDIR,"data")

# couleurs
BLACK = [0,0,0]
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

######################################################################################
#
#  gestion des sprite-sheets
#
######################################################################################

def LoadPygameImageInFolder(filename):
    fullname = os.path.join(assets, filename)
    Surface = pygame.image.load(fullname)
    return Surface

def ChargeSerieSprites(filename, larg,haut,DicSprites):

    planche_sprites = LoadPygameImageInFolder(filename)

    nX = planche_sprites.get_width()   //  larg
    nY = planche_sprites.get_height()  //  haut
    for ix in range(nX):
        for iy in range(nY):
            spr = planche_sprites.subsurface((larg * ix, haut * iy, larg,haut))
            id = GenTexture(spr)
            DicSprites[(ix,iy)] = id

#crée une ligne dans la scène
def Line(Couleur,P1,P2):
    glBegin(GL_LINES)
    glColor3f(Couleur[0],Couleur[1],Couleur[2])
    glVertex3fv(P1)
    glVertex3fv(P2)
    glColor4f(1,1,1,1)
    glEnd()


######################################################################################
#
#  fonction math sur les vecteurs
#
######################################################################################

def Add(u,v): return (u[0]+v[0], u[1]+v[1], u[2]+v[2])
def Sub(u,v): return (u[0]-v[0], u[1]-v[1], u[2]-v[2])
def Mul(u,s): return (u[0]*s, u[1]*s, u[2]*s)
def Norm(v):  return  math.sqrt( v[0]**2 + v[1]**2 + v[2]**2 )

def abs(n):
    if n<0:
        return -n
    return n

# rotation dans le plan horizontal

def Rz(v, theta):  return  ( cos(theta) * v[0] -  sin(theta) * v[1],  sin(theta) * v[0] + cos(theta) * v[1], v[2])

def M_rotation(T,vecteur):
    nx = vecteur[0]
    ny = vecteur[1]
    nz = vecteur[2]
    #formule de rotation de Rodrigues
    M = cos(T)*np.array([[1,0,0],[0,1,0],[0,0,1]])+(1-cos(T))*np.array([[nx*nx,nx*ny,nx*nz],[nx*ny,ny*ny,ny*nz],[nx*nz,ny*nz,nz*nz]]) + sin(T)*np.array([[0,-nz,ny],[nz,0,-nx],[-ny,nx,0]])
    return M

######################################################################################
#
#  fonctions pour les appels openGL
#
######################################################################################
LData = []

def GenTexture(pygameSurface):
    textureData = pygame.image.tostring(pygameSurface,"RGBA",1)
    LData.append(textureData)

    width, height = pygameSurface.get_size()

    ID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, ID)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    #glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_BLEND);
    #glGenerateMipmap(GL_TEXTURE_2D)

    return ID

def LoadTexture(filename):
    global CurrentID
    fullname = os.path.join(assets, filename)
    textureSurface = pygame.image.load(fullname)

    return GenTexture(textureSurface)


def Face(TexID,A1,A2,A3,A4,Debug = False):

    glBindTexture(GL_TEXTURE_2D, TexID)

    glBegin(GL_QUADS)
    glTexCoord2f( 1, 0);  glVertex3fv( A1 )
    glTexCoord2f( 1, 1);  glVertex3fv( A2 )
    glTexCoord2f( 0, 1);  glVertex3fv( A3 )
    glTexCoord2f( 0, 0);  glVertex3fv( A4  )
    glEnd()

    glBindTexture(GL_TEXTURE_2D, 0)
    if Debug :
        C = (0,0,0)
        Line(C,A1,A2)
        Line(C,A2,A3)
        Line(C,A3,A4)
        Line(C,A4,A1)

def Init3D(): #ne pas toucher
    width, height = display
    glViewport(0, 0, width, height)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(40.0, width / height, 0.1, 1000);

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glClear(GL_COLOR_BUFFER_BIT or GL_DEPTH_BIT);



    glEnable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)
    #glEnable(GL_BLEND)
    #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


    glClearColor(0.3,0,0,0)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    glAlphaFunc(GL_GREATER, 0.1)
    glEnable(GL_ALPHA_TEST)


    # camera
    glPushMatrix();
    glRotatef(-rotdegres_Oy, 0, 1, 0)
    glRotatef(-rotdegres_Ox_player, dir_Rcam_x, 0 ,dir_Rcam_z )
    glTranslatef(-player_x, -player_y, -player_z)

def End3D():
    glPopMatrix()

# HUD

def HUDInit():
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluOrtho2D(0, display[0], 0, display[1]);
    glMatrixMode(GL_MODELVIEW);

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glPushMatrix()
    glLoadIdentity()


def HUDBlit(TexID,x,y,L,H,Debug = False):

    glBindTexture(GL_TEXTURE_2D, TexID)

    glBegin(GL_QUADS)
    glTexCoord2f( 1, 0);  glVertex2f( x,   y   )
    glTexCoord2f( 1, 1);  glVertex2f( x,   y+H )
    glTexCoord2f( 0, 1);  glVertex2f( x+L, y+H )
    glTexCoord2f( 0, 0);  glVertex2f( x+L, y   )
    glEnd()

    glBindTexture(GL_TEXTURE_2D, 0)

    if Debug :
        C = (0,1,1)
        HUDLine(C,x,y,     x+L,y )
        HUDLine(C,x+L,y,   x+L,y+H)
        HUDLine(C,x+L,y+H, x,y+H)
        HUDLine(C,x,y+H,   x,y)


def HUDEnd():
    glPopMatrix()

def HUDLine(Couleur,x1,y1,x2,y2,Debug = False):
    glBegin(GL_LINES)
    glColor3f(Couleur[0],Couleur[1],Couleur[2])
    glVertex2f(x1,y1)
    glVertex2f(x2,y2)
    glColor4f(1,1,1,1)
    glEnd()

#################################################################################
#
#    Fonctions d'aide au dessin 3D
#
#################################################################################

# dessine un rectangle vertical
# (x1,z1) et (x2,z2) les points au sol qui définissent sa position
# h1 et h2 définit sa hauteur de départ et de fin
def RectVertical(TextID,x1,z1,x2,z2,h1,h2):
    A = (x1,h1,z1)
    B = (x1,h2,z1)
    C = (x2,h2,z2)
    D = (x2,h1,z2)
    Face(TextID,A,B,C,D)

# dessine un rectangle horizontal // axes
def RectHorizontal(TextID,x,z,Lx,Lz,h):
    A = (x,   h,z)
    B = (x,   h,z+Lz)
    C = (x+Lx,h,z+Lz)
    D = (x+Lx,h,z)
    Face(TextID,A,B,C,D)

#dessine un recangle vertical toujours orienté face caméra (billboarding)
def RectFaceCam(TextID,xmil,ymil,zmil,Largeur,hauteur):
    Largeur /= 2
    rotrad = math.radians(rotdegres_Oy)
    dirx =  Largeur * math.cos(rotrad)
    dirz =  Largeur * math.sin(-rotrad)
    #print(dirx,dirz)

    x1 = xmil - dirx
    z1 = zmil - dirz
    A = (x1,ymil,z1)
    B = (x1,ymil+hauteur,z1)

    x2 = xmil + dirx
    z2 = zmil + dirz
    C = (x2,ymil+hauteur,z2)
    D = (x2,ymil,z2)
    Face(TextID,A,B,C,D)

# construit un cube
def Cube(TextID,Cx,Cy,Cz,R):
    x1 = Cx    ;  z1 = Cz
    x2 = Cx    ;  z2 = Cz + R
    x3 = Cx + R;  z3 = Cz + R
    x4 = Cx + R;  z4 = Cz

    h1 = Cy -0.01
    h2 = Cy + R

    # faces latérales
    RectVertical(TextID,x1,z1,x2,z2,h1,h2)
    RectVertical(TextID,x2,z2,x3,z3,h1,h2)
    RectVertical(TextID,x3,z3,x4,z4,h1,h2)
    RectVertical(TextID,x4,z4,x1,z1,h1,h2)

    RectHorizontal(TextID,x1,z1,R,R,h1)  #dessous
    RectHorizontal(TextID,x1,z1,R,R,h2)  #dessus

# construit un pavé
def Pave(TextID,Cx,Cy,Cz,dx,dy,dz): #-44 ,0 ,-40, 4, 4, 80
    x1 = Cx      ;  z1 = Cz
    x2 = Cx +dx  ;  z2 = Cz
    x3 = Cx + dx ;  z3 = Cz + dz
    x4 = Cx      ;  z4 = Cz  + dz
    h1 = Cy -0.01
    h2 = Cy + dy

    # faces latérales
    RectVertical(TextID,x1,z1,x2,z2,h1,h2)
    RectVertical(TextID,x2,z2,x3,z3,h1,h2)
    RectVertical(TextID,x3,z3,x4,z4,h1,h2)
    RectVertical(TextID,x4,z4,x1,z1,h1,h2)

    RectHorizontal(TextID,x1,z1,dx,dz,h1)  #dessous
    RectHorizontal(TextID,x1,z1,dx,dz,h2)  #dessus

def Bidon(TextID):
    z = -.5
    x = 3
    Largeur = 2
    hauteut = 2
    RectFaceCam(TextID, x,z,Largeur,hauteut)

def Pilier():
    z = 2
    x = -3
    Largeur = 2
    hauteut = 3
    RectFaceCam(TexPilier, x,z,Largeur,hauteut)

def Mechant(TextID,x,y,z):
    Largeur = 3
    hauteut = 3
    RectFaceCam(TextID,x,y,z,Largeur,hauteut)

# crée un pavage en damier au sol
def Sol():
    for x in range(0,40,4) :
        for z in range(0,36,4):
            TextID = TexGrey25
            if (x+z) % 8 == 0 : TextID = TexGrey50
            RectHorizontal( TextID, x, z, 4, 4,0  )

def Surface(TextId,Cx,Cy,Cz,dx,dy,dz,px,py,pz):
    if dx==0:
        for y in range(0,dy,py):
            for z in range(0,dz,pz):
                TextID = TextId[0]
                if (y+z) % (py+px) == 0 : TextID = TextId[1]
                xx = Cx
                yy = Cy + y
                zz = Cz + z
                A=(xx,yy,zz)
                B=(xx,yy+py,zz)
                C=(xx,yy+py,zz+pz)
                D=(xx,yy,zz+pz)
                Face(TextID,A,B,C,D)
    if dy==0:
        for x in range(0,dx,px):
            for z in range(0,dz,pz):
                TextID = TextId[0]
                if (x+z) % (px+pz) == 0 : TextID = TextId[1]
                xx = Cx + x
                yy = Cy
                zz = Cz + z
                A=(xx,yy,zz)
                B=(xx+px,yy,zz)
                C=(xx+px,yy,zz+pz)
                D=(xx,yy,zz+pz)
                Face(TextID,A,B,C,D)
    if dz==0:
        for x in range(0,dx,px):
            for y in range(0,dy,py):
                TextID = TextId[0]
                if (x+y) % (px+py) == 0 : TextID = TextId[1]
                xx = Cx + x
                yy = Cy + y
                zz = Cz
                A=(xx,yy,zz)
                B=(xx+px,yy,zz)
                C=(xx+px,yy+py,zz)
                D=(xx,yy+py,zz)
                Face(TextID,A,B,C,D)

def escalier(Cx,Cy,Cz,dx,dz):
    list=[]
    if dx==0:
        for p in range (dz):
            marche_part1 = [[TexStone1,TexStone1],Cx,Cy+p,Cz+p,4,1,0,1,1,0]
            marche_part2 = [[TexStone2,TexStone2],Cx,Cy+p+1,Cz+p,4,0,1,1,0,1]
            list.append(marche_part1)
            list.append(marche_part2)
    if dz==0:
        for p in range (dx):
            marche_part1 = [[TexStone1,TexStone1],Cx,Cy+p,Cz+p,4,1,0,1,1,0]
            marche_part2 = [[TexStone2,TexStone2],Cx,Cy+p+1,Cz+p,4,0,1,1,0,1]
            list.append(marche_part1)
            list.append(marche_part2)
    return list

def createMechant(x,y,z,vitesse,map):
    global list_mechants
    mechant={}
    mechant['x']=x
    mechant['y']=y
    mechant['z']=z
    mechant['vitesse']=vitesse
    mechant['angle']= random.randint(0,360)
    mechant['iter']=random.randint(0,4)
    mechant['seq']=0
    mechant['etat'] = marche
    mechant['map']=map  #xmin,xmax,zmin,zmax

    list_mechants.append(mechant)


def nonObstacle(dx,dy,dz) :
    x = player_x + dx
    y = player_y + dy
    z = player_z + dz
    d = 1

    for cube in list_cube :
        r = cube[-1]
        x_min = cube[1] -d
        x_max = cube[1] + r + d
        y_min = cube[2] -d
        y_max = cube[2] + r +d
        z_min = cube[3]-d
        z_max = cube[3] + r +d
        if  ( x_min < x and x < x_max) and( z_min < z and z < z_max):
            for i in range(taille):
                if y_min < y-i and y-i < y_max:
                    return False

    for pave in list_pave :
        x_min = pave[1] -d
        x_max = pave[1] + pave[4] + d
        y_min = pave[2] -d
        y_max = pave[2] + pave[5] +d
        z_min = pave[3]-d
        z_max = pave[3] + pave[6] +d
        if  ( x_min < x and x < x_max) and( z_min < z and z < z_max):
            for i in range(taille):
                if y_min < y-i and y-i < y_max:
                    return False

    return True

def canClimb() :
    x = player_x
    y = player_y -taille +1
    z = player_z
    d =2
    for ech in list_ech :
        x_min = ech[1] -d
        x_max = ech[1] + ech[4] + d
        y_min = ech[2] -d
        y_max = ech[2] + ech[5] +d
        z_min = ech[3]-d
        z_max = ech[3] + ech[6] +d
        if  ( x_min < x and x < x_max) and( z_min < z and z < z_max) and (y_min < y and y < y_max):
            return True
    return False

def Affichage3D():

    Sol()

    for cube in list_cube :
        TextID = cube[0][0]
        Cx = cube[1]
        Cy = cube[2]
        Cz = cube[3]
        R = cube[4]
        Cube(TextID,Cx,Cy,Cz,R)

    for pave in list_pave:
        Cx = pave[1]
        Cy = pave[2]
        Cz = pave[3]
        dx = pave[4]
        dy = pave[5]
        dz = pave[6]
        if pave[0][1]=="":
            TextID = pave[0][0]
            Pave(TextID,Cx,Cy,Cz,dx,dy,dz)
        else:
            TextID = pave[0]
            if len(pave)>7:
                px=pave[7]
                py=pave[8]
                pz=pave[9]
            else:
                px=4
                py=4
                pz=4
            Surface(TextID,Cx,Cy,Cz,dx,dy,dz,px,py,pz)

    for mechant in list_mechants :
        if mechant['etat']==mort:
            IdSprite = DMechantSpriteDead[(7,0)]
            Mechant(IdSprite,mechant['x'],mechant['y'],mechant['z'])
        else:
            iter = mechant['iter']
            mechant['iter'] += 1
            if mechant['etat']==tir:
                id = (iter // 5 ) % 4
                IdSprite = DMechantSpriteTir[(mechant['seq'],id)]
                Mechant(IdSprite,mechant['x'],mechant['y'],mechant['z'])
            if mechant['etat']==toucher:
                id = (iter // 4 ) % 8
                IdSprite = DMechantSpriteDead[(id,0)]
                Mechant(IdSprite,mechant['x'],mechant['y'],mechant['z'])
            if mechant['etat']==marche:
                id = (iter // 5 ) % 3
                IdSprite = DMechantSprite[(mechant['seq'],id)]
                Mechant(IdSprite,mechant['x'],mechant['y'],mechant['z'])


#################################################################################
#
#    Boucle du jeu
#
#################################################################################

done = False

noneState =-1
menu = 0
play = 1
dead = 2
victory = 3
gameState = menu

bouton_jouer = [360,665,450,525]
bouton_quitter = [382,650,566,625]
bouton_rejouer = [395,600,440,480]
bouton_quit = [444,541,606,645]

while not done:

    #################################################################################
    #
    #    Menu principale
    #
    #################################################################################

    Image_main_menu = pygame.image.load(os.path.join(assets, "main_menu.png"))
    screen = pygame.display.set_mode([screenwidth,screenheight])


    while gameState ==menu :

        pygame.mouse.set_visible(1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        KeysPressed = pygame.key.get_pressed()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            x = pos[0]
            y = pos[1]

            # jouer
            xmin= bouton_jouer[0]
            xmax= bouton_jouer[1]
            ymin= bouton_jouer[2]
            ymax= bouton_jouer[3]
            if xmin < x and x < xmax and ymin < y and y < ymax :
                gameState = play

            #quitter
            xmin= bouton_quitter[0]
            xmax= bouton_quitter[1]
            ymin= bouton_quitter[2]
            ymax= bouton_quitter[3]
            if xmin < x and x < xmax and ymin < y and y < ymax :
                gameState = noneState
                done = True



        screen.blit(Image_main_menu,(0,0))

        pygame.display.flip()


    #################################################################################
    #
    #    Partie de jeux
    #
    #################################################################################

    if gameState == play:

        # INIT de Pygame
        pygame.quit()
        pygame.init()
        display = (screenwidth,screenheight)
        pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

        # INIT OPENGL
        glEnable(GL_DEPTH_TEST)
        FOV = 45
        ratio = (display[0]/display[1])
        dist_min = 0.01
        dist_max = 100 # au dela de 100 m => les objets ne sont plus affichés
        gluPerspective(FOV, ratio, dist_min, dist_max)

        # Init position joueur/camera dans la scène
        taille = 2
        player_x = 10
        player_z = 10  # un peu derrière le centre (0,0,0) de la scène, on peut donc voir tout objet placé au centre
        player_y = taille  # hauteur de la caméra = hauteur des yeux = 1.7m
        player_pv = 100
        Dy = 0
        player_tir = False
        player_iter = 0
        player_mun = 5
        player_reload = False
        player_shoot_distance = 20

        g = 9.81
        speed = 0.2
        hauteur_saut = 0.5
        # rotation du joueur/camera autours de l'axe vertical
        rotdegres_Oy = 180   # 0 => regarde vers le fond Z-  et sens trigonometrique
        rotdegres_Ox_player = 0
        sensibilite_vision = 0.15
        angle_vision_max =80

        #################################################################################
        #
        #    Charger les images et textures
        #
        #################################################################################

        DMechantSprite = {}
        ChargeSerieSprites("marche.png",72,64,DMechantSprite)
        DMechantSpriteTir ={}
        ChargeSerieSprites("fire.png",72,64,DMechantSpriteTir)
        DMechantSpriteDead ={}
        ChargeSerieSprites("dead.png",72,64,DMechantSpriteDead)
        DShotGunTir = {}
        ChargeSerieSprites("shotgun.png",101,89,DShotGunTir)
        DShotGunRe = {}
        ChargeSerieSprites("shotgun_reload.png",140,80,DShotGunRe)



        TexBlack       = LoadTexture("color_black.png")
        TexRed         = LoadTexture("color_red.png")
        TexMUR         = LoadTexture("DoomWall.png")
        TexMURinv      = LoadTexture("DoomWallinv.png")
        TexGrey25      = LoadTexture("color_gray25.png")
        TexGrey50      = LoadTexture("color_gray50.png")
        TexEchelle     = LoadTexture("echelle.png")
        TexIronBar     = LoadTexture("ironbar.png")
        TexIronBar2    = LoadTexture("ironbar2.png")
        TexStone1      = LoadTexture("stone1.png")
        TexStone2      = LoadTexture("stone2.png")
        TexCrosshair   = LoadTexture("crosshair.png")
        TexAmmo        = LoadTexture("ammo.png")
        TexVictory     = LoadTexture("victory.png")



        size = 0.3


        #################################################################################
        #
        #    Creation de l'interface
        #
        #################################################################################



        List_interface=[]

        element={}
        element['visible']=True
        element['IdSprite']=TexBlack
        element['x']=399
        element['y']=760
        element['width']=202
        element['height']=10

        List_interface.append(element)

        crosshair = {}
        crosshair['visible']=True
        crosshair['IdSprite']=TexCrosshair
        crosshair['width']=50
        crosshair['height']=50
        crosshair['x']= screenwidth /2 - crosshair['width'] /2
        crosshair['y']= screenheight /2 - crosshair['height']/2

        List_interface.append(crosshair)

        #pygame.draw.rect(screen,color,pygame.Rect())

        #################################################################################
        #
        #    Creation de la map
        #
        #################################################################################

        # creation des cubes ####
        list_cube=[]

        # creation des pavés ####

        #creation des surface
        sol_2 = [[TexGrey25,TexGrey50],40,12,0,12,0,24]
        sol_3 = [[TexGrey25,TexGrey50],0,12,36,40,0,12]
        sol_4 = [[TexGrey25,TexGrey50],4,12,24,36,0,12]
        ironbar1 = [[TexIronBar,TexIronBar],40,12,0,10,6,0]
        ironbar2 = [[TexIronBar2,TexIronBar2],52,12,0,0,6,24]
        ironbar3 = [[TexIronBar,TexIronBar],40,12,24,10,6,0]
        ironbar4 = [[TexIronBar2,TexIronBar2],40,12,24,0,6,24]
        ironbar5 = [[TexIronBar,TexIronBar],0,12,48,40,6,0]
        ironbar6 = [[TexIronBar2,TexIronBar2],0,12,0,0,6,48]
        ironbar7 = [[TexIronBar,TexIronBar],0,0,0,38,18,0]
        mur1 = [[TexMUR,TexMUR],40,0,0,0,12,48]
        mur2 = [[TexMUR,TexMUR], 0,0,0,0,12,36]
        mur3 = [[TexMURinv,TexMURinv],4,0,24,36,12,0]
        mur4 = [[TexMUR,TexMUR],4,0,24,0,12,12]
        list_surface = [mur1,mur2,mur3,mur4,sol_2,sol_3,sol_4,ironbar1,ironbar2,ironbar3,ironbar4, ironbar5,ironbar6,ironbar7]

        #creation des echelles
        ech_1=[[TexEchelle,TexEchelle],39.8,0,11,0,12,2,1,3,2]
        list_ech = [ech_1]

        #creation des marches
        list_marche=[]
        escalier1 = escalier(0,0,24,0,12)
        list_marche += escalier1
        list_ech += list_marche

        list_pave = list_ech + list_surface

        #creation map limite mechant
        map1=[0,40,0,24]
        map2=[0,40,36,48]
        map3=[40,52,0,24]

        #################################################################################
        #
        #    Creation des mechant
        #
        #################################################################################

        list_mechants=[]
        marche=0
        tir=1
        toucher=2
        mort=3

        #mechant map 1
        createMechant(30,0,20,1/20,map1)
        createMechant(20,0,5,1/20,map1)

        #machant map 2
        createMechant(20,12,40,1/20,map2)

        #machant map 3
        createMechant(45,12,8,1/20,map3)


        #################################################################################
        #
        #    Boucle de la partie
        #
        #################################################################################

        pygame.mouse.set_visible(False)
        pygame.time.wait(100)
        time_init = int(pygame.time.get_ticks())
        iter_gun = 0

        while gameState==play:
            player_iter += 1

            #print(player_x,player_y,player_z)
            #print(Dy)
            #print(player_pv)
            #print(player_x, player_z)

        # EVENEMENTS

            # détecte le clic sur le bouton close de la fenêtre
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            # LOGIQUE
            KeysPressed = pygame.key.get_pressed()

            if KeysPressed[pygame.K_ESCAPE]:
                gameState = menu

            rotdegres_Oy = rotdegres_Oy%360
            rotrad = math.radians(rotdegres_Oy)
            rotrad2 = math.radians(rotdegres_Ox_player)
            dir_cam_x =  - math.sin(rotrad)
            dir_cam_z =  - math.cos(rotrad)
            dir_Rcam_x = math.cos(-rotrad)
            dir_Rcam_z = math.sin(-rotrad)

            #sprint
            if KeysPressed[pygame.K_LSHIFT]:
                speed = 0.7
            else :
                speed = 0.5

            # tourne la caméra selon le pointeur
            if event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                x = pos[0]
                y = pos[1]
                xx = x - screenwidth/2
                yy = y - screenheight/2

                if abs(xx) > 0.01:
                    T = -xx* sensibilite_vision
                    rotdegres_Oy += T

                if  abs(yy) > 0.01:
                    T = -yy* sensibilite_vision
                    rotdegres_Ox_player += T
                    if rotdegres_Ox_player>angle_vision_max:
                        rotdegres_Ox_player = angle_vision_max
                    if rotdegres_Ox_player<-angle_vision_max:
                        rotdegres_Ox_player = -angle_vision_max
                pygame.mouse.set_pos(screenwidth/2,screenheight/2)

            # tir/recharger
            if event.type == pygame.MOUSEBUTTONDOWN and not player_tir and not player_reload and player_mun > 0:
                M_rota1 = M_rotation(rotrad,[0,1,0])
                M_rota2 = M_rotation( rotrad2, np.dot( M_rota1 , np.array([1,0,0]) ) )
                M_rota = np.dot( M_rota1, M_rota2 )
                M = np.linalg.inv(M_rota)
                player_tir = True
                player_iter = 0
                player_mun -=1
                d=player_shoot_distance
                indice_mechant_toucher = -1

                for i in range(len(list_mechants)):
                    mechant = list_mechants[i]
                    if mechant['etat']!=mort :
                        vect = np.array([mechant['x']-player_x,mechant['y']-player_y,mechant['z']-player_z])
                        vect_base_player = np.dot(M,vect)
                        x = vect_base_player[0]
                        y = vect_base_player[1]
                        z = vect_base_player[2]
                        #print(int(x),int(y),int(z))
                        if x<3 and x>-3 and y<3 and y>-3 and z<0 and z>-d:
                            d=z
                            indice_mechant_toucher = i

                if indice_mechant_toucher !=-1:
                    list_mechants[indice_mechant_toucher]['etat'] = toucher
                    list_mechants[indice_mechant_toucher]['iter'] = 0

            if player_iter > 30 and player_tir :
                player_iter = 0
                player_tir = False

            if player_mun < 5 and KeysPressed[pygame.K_r] and not player_tir and not player_reload:
                player_iter = 0
                player_reload = True

            if player_iter > 25 and player_reload :
                player_mun += 1
                player_reload = False



            #saut
            if KeysPressed[pygame.K_SPACE] and Dy==0:
                Dy += hauteur_saut


            #gravité
            time = int(pygame.time.get_ticks())
            Dy -= g*(time-time_init)/10000
            time_init = time

            #recule
            if KeysPressed[pygame.K_s] :
                dx = -dir_cam_x * speed
                dz = -dir_cam_z * speed
                if nonObstacle(dx,0,dz):
                    player_x += dx
                    player_z += dz

            #avance
            if KeysPressed[pygame.K_z] :
                if canClimb() :
                    dy = 0.3
                    Dy = 0
                    time_init = time

                    if nonObstacle(0,dy,0):
                        player_y += dy
                else :
                    dx = dir_cam_x * speed
                    dz = dir_cam_z * speed
                    if nonObstacle(dx,0,dz):
                        player_x += dx
                        player_z += dz

            # translation sur la droite
            if KeysPressed[pygame.K_d]:
                dx = 0.5 * dir_Rcam_x * speed
                dz = 0.5 * dir_Rcam_z * speed
                if nonObstacle(dx,0,dz):
                    player_x += dx
                    player_z += dz

            #translation sur la gauche
            if KeysPressed[pygame.K_q]:
                dx = -0.5 * dir_Rcam_x * speed
                dz = -0.5 * dir_Rcam_z * speed
                if nonObstacle(dx,0,dz):
                    player_x += dx
                    player_z += dz

            if ( nonObstacle(0,Dy,0) and player_y + Dy >= taille ) :
                player_y += Dy
            else:
                if player_y + Dy < taille:
                    player_y = taille
                if Dy <= -1:
                    player_pv += int(Dy*10)

                Dy = 0

            # gestion des méchant

            for mechant in list_mechants:

                if mechant['etat']==toucher:
                    if mechant['iter']>28:
                        mechant['etat'] = mort

                if mechant['etat']==marche or mechant['etat']==tir :
                    vect = np.array([player_x-mechant['x'],player_y-mechant['y'],player_z-mechant['z']])
                    dist = math.sqrt(vect[0]**2 + vect[1]**2 + vect[2]**2)

                    if dist > 20 :

                        mechant['etat']=marche

                        map = mechant['map']
                        d=5
                        xmin = map[0]+d
                        xmax = map[1]-d
                        ymin = map[2]+d
                        ymax = map[3]-d
                        mechant['angle'] = mechant['angle']%360
                        mechant_angle_rad = math.radians(mechant['angle'])

                        mechant['x'] += math.cos(mechant_angle_rad) * mechant['vitesse']
                        mechant['z'] += math.sin(mechant_angle_rad) * mechant['vitesse']

                        if mechant['x'] > xmax :
                            mechant['x'] = xmax
                            mechant['angle'] = random.randint(0,360)

                        elif mechant['x'] < xmin :
                            mechant['x'] = xmin
                            mechant['angle'] = random.randint(0,360)

                        elif mechant['z'] > ymax :
                            mechant['z'] = ymax
                            mechant['angle'] = random.randint(0,360)

                        elif mechant['z'] < ymin :
                            mechant['z'] = ymin
                            mechant['angle'] *= random.randint(0,360)

                        d_angle = abs(mechant['angle']-(90-rotdegres_Oy))%360
                        delta_angle = 45/2

                        if (d_angle<delta_angle and d_angle<0) or (d_angle<360 and d_angle>360-d_angle):
                            mechant['seq']=0

                        for i in range(1,7):
                            if d_angle>i*45-delta_angle and d_angle<i*45+delta_angle:
                                mechant['seq']=8-i

                    elif  5 < dist and dist < 20: #le méchant est assez proche
                        mechant['etat']=marche
                        mechant['x'] += ((vect[0])/dist )*mechant['vitesse']
                        mechant['z'] += ((vect[2])/dist )*mechant['vitesse']
                        mechant['seq']=0

                    else :
                        mechant['seq']=0
                        if mechant['etat']==marche :
                            mechant['iter']=0
                            mechant['etat']=tir
                        if mechant['iter']>13:
                            mechant['iter']=0
                            player_pv -= 20

            # verif vivant
            if player_pv <= 0 :
                gameState=dead

            # verif victoire
            vict = True
            for mechant in list_mechants:
                if mechant['etat']!=mort:
                    vict =False
            if vict: gameState = victory

            # DESSIN  3D - Init3D et End3D doivent commencer et terminer ce bloc

            Init3D()

            Sol()

            for cube in list_cube :
                TextID = cube[0][0]
                Cx = cube[1]
                Cy = cube[2]
                Cz = cube[3]
                R = cube[4]
                Cube(TextID,Cx,Cy,Cz,R)

            for pave in list_pave:
                Cx = pave[1]
                Cy = pave[2]
                Cz = pave[3]
                dx = pave[4]
                dy = pave[5]
                dz = pave[6]
                if pave[0][1]=="":
                    TextID = pave[0][0]
                    Pave(TextID,Cx,Cy,Cz,dx,dy,dz)
                else:
                    TextID = pave[0]
                    if len(pave)>7:
                        px=pave[7]
                        py=pave[8]
                        pz=pave[9]
                    else:
                        px=4
                        py=4
                        pz=4
                    Surface(TextID,Cx,Cy,Cz,dx,dy,dz,px,py,pz)

            for mechant in list_mechants :
                if mechant['etat']==mort:
                    IdSprite = DMechantSpriteDead[(7,0)]
                    Mechant(IdSprite,mechant['x'],mechant['y'],mechant['z'])
                else:
                    iter = mechant['iter']
                    mechant['iter'] += 1
                    if mechant['etat']==tir:
                        id = (iter // 5 ) % 4
                        IdSprite = DMechantSpriteTir[(mechant['seq'],id)]
                        Mechant(IdSprite,mechant['x'],mechant['y'],mechant['z'])
                    if mechant['etat']==toucher:
                        id = (iter // 4 ) % 8
                        IdSprite = DMechantSpriteDead[(id,0)]
                        Mechant(IdSprite,mechant['x'],mechant['y'],mechant['z'])
                    if mechant['etat']==marche:
                        id = (iter // 5 ) % 3
                        IdSprite = DMechantSprite[(mechant['seq'],id)]
                        Mechant(IdSprite,mechant['x'],mechant['y'],mechant['z'])

            End3D()

            # affichage 2D  HUD

            HUDInit()

            if player_pv > 0:
                HUDBlit(TexRed,400,761,2*player_pv,8)

            for element in List_interface:
                if element['visible']:
                    IdSprite = element['IdSprite']
                    x = element['x']
                    y = element['y']
                    L = element['width']
                    H = element['height']
                    HUDBlit(IdSprite,x,y,L,H)

            if player_tir :
                id = (player_iter // 5 )%6
                IdSprite = DShotGunTir[(id,0)]
                HUDBlit(IdSprite, 396, 0,303,267 )

            elif player_reload :
                id = (player_iter // 5 )%5
                IdSprite = DShotGunRe[(id,0)]
                HUDBlit(IdSprite, 396, 0,303,267 )

            else :
                HUDBlit(DShotGunTir[(0,0)], 396, 0,303,267 )

            for i in range ( player_mun):
                HUDBlit(TexAmmo,800 + i* 20,100,20,60)

            HUDEnd()



            # Affichage Pygame

            pygame.display.flip()
            pygame.time.wait(30)

    #################################################################################
    #
    #    Game Over
    #
    #################################################################################
    if gameState == dead :
        screen = pygame.display.set_mode([screenwidth,screenheight])
        Image_game_over = pygame.image.load(os.path.join(assets, "game_over.png"))

    while gameState == dead:


        pygame.mouse.set_visible(1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameState = noneState
                done = True


        KeysPressed = pygame.key.get_pressed()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            x = pos[0]
            y = pos[1]

            # rejouer
            xmin= bouton_rejouer[0]
            xmax= bouton_rejouer[1]
            ymin= bouton_rejouer[2]
            ymax= bouton_rejouer[3]
            if xmin < x and x < xmax and ymin < y and y < ymax :
                gameState = play

            #quitter
            xmin= bouton_quit[0]
            xmax= bouton_quit[1]
            ymin= bouton_quit[2]
            ymax= bouton_quit[3]
            if xmin < x and x < xmax and ymin < y and y < ymax :
                gameState = noneState
                done=True

        screen.blit(Image_game_over,(0,0))

        pygame.display.flip()

    #################################################################################
    #
    #    Victory
    #
    #################################################################################



    while gameState == victory:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameState = noneState
                done = True


        #affichage de fin
        player_x = -9
        player_y = 30
        player_z = -9

        rotdegres_Oy = 230
        rotdegres_Ox_player = -30

        rotrad = math.radians(rotdegres_Oy)
        dir_Rcam_x = math.cos(-rotrad)
        dir_Rcam_z = math.sin(-rotrad)

        # DESSIN  3D - Init3D et End3D doivent commencer et terminer ce bloc

        Init3D()

        Sol()

        for cube in list_cube :
            TextID = cube[0][0]
            Cx = cube[1]
            Cy = cube[2]
            Cz = cube[3]
            R = cube[4]
            Cube(TextID,Cx,Cy,Cz,R)

        for pave in list_pave:
            Cx = pave[1]
            Cy = pave[2]
            Cz = pave[3]
            dx = pave[4]
            dy = pave[5]
            dz = pave[6]
            if pave[0][1]=="":
                TextID = pave[0][0]
                Pave(TextID,Cx,Cy,Cz,dx,dy,dz)
            else:
                TextID = pave[0]
                if len(pave)>7:
                    px=pave[7]
                    py=pave[8]
                    pz=pave[9]
                else:
                    px=4
                    py=4
                    pz=4
                Surface(TextID,Cx,Cy,Cz,dx,dy,dz,px,py,pz)

        for mechant in list_mechants :
            if mechant['etat']==mort:
                IdSprite = DMechantSpriteDead[(7,0)]
                Mechant(IdSprite,mechant['x'],mechant['y'],mechant['z'])
            else:
                iter = mechant['iter']
                mechant['iter'] += 1
                if mechant['etat']==tir:
                    id = (iter // 5 ) % 4
                    IdSprite = DMechantSpriteTir[(mechant['seq'],id)]
                    Mechant(IdSprite,mechant['x'],mechant['y'],mechant['z'])
                if mechant['etat']==toucher:
                    id = (iter // 4 ) % 8
                    IdSprite = DMechantSpriteDead[(id,0)]
                    Mechant(IdSprite,mechant['x'],mechant['y'],mechant['z'])
                if mechant['etat']==marche:
                    id = (iter // 5 ) % 3
                    IdSprite = DMechantSprite[(mechant['seq'],id)]
                    Mechant(IdSprite,mechant['x'],mechant['y'],mechant['z'])

        End3D()
        # affichage 2D  HUD

        HUDInit()


        HUDBlit(TexVictory, 250, 400,500,100 )



        HUDEnd()



        # Affichage Pygame

        pygame.display.flip()
        pygame.time.wait(30)

pygame.quit()
