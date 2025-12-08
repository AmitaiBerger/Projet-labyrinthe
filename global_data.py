import enum

class Direction(enum.Enum):
    """
    Directions possibles
    """
    
    EST = 0
    NORD = 1
    OUEST = 2
    SUD = 3

K_RIGHT, K_UP, K_LEFT, K_DOWN = 0,1,2,3