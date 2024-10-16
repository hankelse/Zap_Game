from pygame.constants import K_SPACE, K_ESCAPE, K_w, K_a, K_s, K_d, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_r


#----------SETTINGS-----------#

#---Screen_Settings---#
screen_size = screen_width, screen_height =  800, 800
font_name = 'Comic Sans MS'
shake_levels = {
    "ZAP": 10, 
    "BALL HIT": 5,
    "NODE HIT": 50,
    "BALL DESTROYED": 100,
}

#---Performance_Settings---#
max_fps = 50 #frames per second

#---Sprite Settings---#

#nodes
node_speed = ns = 7

#balls
balls_speed_range = [5, 8]
num_balls = 4

#pickups
num_pickups = 2

node_colors ={
    "A":(100, 150, 0),
    "B":(0, 150, 100),
    "C":(150, 150, 150),
}

#---GAMEPLAY SETTINGS---#
max_score = 100
alt_strk_multi = 1
quick_hit_multi = 1
qhmulti_interval = 2
zap_delay = 0.2
zap_length = 0.5

#---Control_Settings---#
 
bindings = {
    "A UP": K_w,
    "A DOWN": K_s,
    "A LEFT": K_a,
    "A RIGHT": K_d,

    "B UP": K_UP,
    "B DOWN": K_DOWN,
    "B LEFT": K_LEFT,
    "B RIGHT": K_RIGHT,

    "ZAP": K_SPACE,
    
    "QUIT": K_ESCAPE,
    "PLAY AGAIN": K_r,
    "BEGIN": K_SPACE,
}
