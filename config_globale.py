import enum
#import pygame

class Direction(enum.Enum):
    """
    Directions possibles
    """
    
    EST = 0
    NORD = 1
    OUEST = 2
    SUD = 3




# VALEURS PAR DEFAUT de toutes les variables

# --- ECRAN ---
SCREEN_WIDTH = 750
SCREEN_HEIGHT = 650
FPS = 60

# --- COULEURS ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (150, 150, 150)
LIGHT_GREY = (240, 240, 245)
RED = (231, 76, 60)
GREEN = (46, 204, 113)
BLUE = (52, 152, 219)
DARK_BLUE = (44, 62, 80)
BUTTON_COLOR = (200, 220, 255)
BUTTON_HOVER = (180, 200, 240)

# Couleurs Items
GOLD = (255, 215, 0)      # Marteau
ORANGE = (255, 165, 0)    # Boussole
BROWN = (139, 69, 19)     # Piège
PURPLE = (147, 112, 219)  # Téléporteur

# --- COULEURS JOUEURS ---
PLAYER_COLORS = [
    (255, 0, 0),    # J1: Rouge
    (0, 0, 255),    # J2: Bleu
    (0, 200, 0),    # J3: Vert
    (255, 255, 0),  # J4: Jaune
    (255, 0, 255),  # J5: Magenta
    (0, 255, 255)   # J6: Cyan
]

# --- PARAMETRES JEU ---
DEFAULT_LABY_SIZE = (10, 10)
VIEW_DISTANCE_NETWORK = 8 

"""# --- ITEMS ID ---
ITEM_NONE = 0
ITEM_HAMMER = 1
ITEM_COMPASS = 2
ITEM_TRAP = 3
ITEM_TELEPORT = 4"""