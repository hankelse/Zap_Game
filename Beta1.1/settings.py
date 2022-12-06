from pygame.constants import K_SPACE, K_ESCAPE, K_w, K_a, K_s, K_d, K_UP, K_DOWN, K_LEFT, K_RIGHT


#----------SETTINGS-----------#

#---Screen_Settings---#
screen_size = screen_width, screen_height =  800, 800
font_name = 'Comic Sans MS'
shake_levels = {
    "ZAP": 10, 
    "BALL HIT": 5,
    "NODE HIT": 50,
}

#---Performance_Settings---#
max_fps = 45 #frames per second

#---Sprite Settings---#
node_speed = ns = 8
num_balls = 3
num_pickups = 2

#---GAMEPLAY SETTINGS---#
max_score = 100
alt_strk_multi = 1.5
quick_hit_multi = 1.075
qhmulti_interval = 2

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
    
    "QUIT": K_ESCAPE
}
