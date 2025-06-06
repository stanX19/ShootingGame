# Constants
SCREEN_WIDTH = 1520
SCREEN_HEIGHT = 800
MAP_WIDTH = 8000
MAP_HEIGHT = 8000
PLAYER_RADIUS = 5
BULLET_RADIUS = 2
MISSILE_RADIUS = 7
UNIT_RADIUS = 10
COLLECTIBLE_RADIUS = 15

# color
PLAYER_COLOR = (255, 255, 0)  # Yellow
BULLET_COLOR = (255, 255, 255)  # White
MISSILE_COLOR = (0, 255, 0)  # Green
ENEMY_COLOR = (255, 102, 204)  # Pink
ENEMY_BULLET_COLOR = (255, 100, 255)
BACKGROUND_COLOR = (0, 0, 0)  # Black
EXPLOSION_COLOR = (255, 105, 0)
FLAME_COLOR = (255, 55, 0)

UNIT_SCORE = 10
UNIT_SHOOT_RANGE = min(SCREEN_WIDTH, SCREEN_HEIGHT) / 2 - 100
UNIT_BULLET_RAD = 4
MAX_ENEMY_COUNT = 250
PLAYER_HP = 50
HEAL_HP = 5
PLAYER_SPEED = 20
BULLET_SPEED = 15.0
MISSILE_SPEED = BULLET_SPEED
UNIT_SPEED = 2
MAX_PARTICLE_COUNT = 200
OVERDRIVE_DURATION = 5000.0  # miliseconds
OVERDRIVE_CD = 65000.0
GOOD_GRAPHICS = False
FPS = 30
SPAWN_CAP = 200
SPAWN_CD = 4  # seconds