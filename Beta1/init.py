import pygame, sys, time, math, random
from pygame.constants import K_SPACE, K_ESCAPE, K_w, K_a, K_s, K_d, K_UP, K_DOWN, K_LEFT, K_RIGHT
pygame.init()

size = width, height =  800, 800
# size = width, height = pygame.display.get_window_size()
cycle_time = 0.025

screen = pygame.display.set_mode(size)
surface = screen.copy()
# screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)

def distance(coord1, coord2):
    xdis = abs(coord1[0] - coord2[0])
    ydis = abs(coord1[1] - coord2[1])
    distance = math.sqrt(xdis**2 + ydis**2)
    return distance

def if_point_on_line(x1, y1, x2, y2, coord, buffer):
    if abs(distance((x1, y1),coord) + distance((x2, y2), coord) - distance((x1, y1), (x2, y2))) < buffer:
        return True
    return False

def get_collision_angle(ball_angle, wall_angle):
    return(wall_angle-ball_angle)

def on_screen(size, coord, coord_type = None, buffer=None): #buffer should be size/2 for circle #coord_type ("x", "y" or "(x, y)")
    if buffer == None: buffer = 0
    response = [True,True]
    if coord[0] < buffer or coord[0] > size[0]-buffer: 
        response[0] = False
    if coord[1] < buffer or coord[1] > size[1]-buffer: 
        response[1] = False
    return tuple(response)

def shake(shake_amount, shake_level):
    sl = shake_level
    if shake_amount != 0:
        if shake_amount == sl:
            return (-sl)
        elif shake_amount == -sl:
            return (sl-1)
        elif shake_amount == sl-1:
            return (-sl+1)
        elif shake_amount == -sl+1:
            return (sl//2)
        elif shake_amount == sl//2:
            return (-sl//2)
        elif shake_amount == -sl//2:
            return (0)
    return 0

class Node:
    def __init__(self, startingx, startingy, color, bindings, type, size, xv_range, yv_range):
        self.x, self.y, self.size = startingx, startingy, size 
        self.max_size = 20
        self.min_size = 10
        self.type = type
        self.bindings = bindings
        self.color = color
        self.base_color = color

        self.xv, self.yv = 0, 0
        self.acceleration = 2
        self.deceleration = 0.5
        self.xv_range = self.xv_min, self.xv_max = xv_range
        self.yv_range = self.yv_min, self.yv_max = yv_range

    def update(self, keys):
        self.color = self.base_color
        self.update_motion(keys) 
    
    def zap(self):
        self.color = (255, 0, 0)

    def update_motion(self, keys):
        #UP and DOWN VELOCITY
        if keys[self.bindings[self.type+" UP"]]:
            self.yv -= self.acceleration
            if self.yv < self.yv_min: self.yv = self.yv_min
        elif keys[self.bindings[self.type+" DOWN"]]:
            self.yv += self.acceleration
            if self.yv > self.yv_max: self.yv = self.yv_max
        else:
            if self.yv != 0:
                if self.yv>0: 
                    self.yv -= self.deceleration
                    if self.yv <0: self.yv = 0
                if self.yv<0: 
                    self.yv += self.deceleration
                    if self.yv >0: self.yv = 0
        #LEFT AND RIGHT VELOCITY
        if keys[self.bindings[self.type+" LEFT"]]:
            self.xv -= self.acceleration
            if self.xv < self.xv_min: self.xv = self.xv_min
        elif keys[self.bindings[self.type+" RIGHT"]]:
            self.xv += self.acceleration
            if self.xv > self.xv_max: self.xv = self.xv_max
        else:
            if self.xv != 0:
                if self.xv>0: 
                    self.xv -= self.deceleration
                    if self.xv <0: self.xv = 0
                if self.xv<0: 
                    self.xv += self.deceleration
                    if self.xv >0: self.xv = 0

        # MOVEMENT
        new_x, new_y = self.x + self.xv, self.y + self.yv
        x_is_valid, y_is_valid = on_screen(size, (new_x, new_y), buffer=self.size/2)
        if x_is_valid: self.x = new_x
        if y_is_valid: self.y = new_y

    def adjust_size(self, ratio):
        self.size = self.max_size - self.max_size*ratio
        if self.size < self.min_size: self.size = self.min_size

    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, pygame.Rect(self.x-self.size/2, self.y-self.size/2, self.size, self.size))

class Player:
    def __init__(self, node_a, node_b, laser, bindings):
        self.nodes = self.node_a, self.node_b = node_a, node_b
        self.laser = laser
        self.bindings = bindings
    
    def update(self, keys): 
        if keys[self.bindings["ZAP"]]:
            for node in self.nodes: node.zap()
            self.laser.zap()
        else:
            node_dist = self.node_distance()
            for node in self.nodes: node.update(keys)
            self.laser.update(keys, self.nodes, node_dist)
            for node in self.nodes: node.adjust_size(node_dist)
    
    def node_distance(self):

        xdis = abs(self.nodes[0].x-self.nodes[1].x)
        ydis = abs(self.nodes[0].y-self.nodes[1].y)
        distance = math.sqrt(xdis**2 + ydis**2)

        distance = 1*distance/1131
        return distance


    def draw(self, surface):
        self.laser.draw(surface)
        for node in self.nodes: node.draw(surface)
        
class Laser:
    def __init__(self, color, size, bindings):
        self.base_color = color
        self.color,  self.size = color, size,
        self.min_size = 5
        self.max_size = 10
        self.x1, self.x2, self.y1, self.y2 = 0, 0, 0, 0
        self.bindings = bindings
        self.on=False
    
        
    def zap(self): 
        self.on = True
        self.color = (150, 25, 25)
    
    def update(self, keys, nodes, node_dist):
        self.on = False
        self.color = self.base_color
        self.x1, self.y1 = nodes[0].x, nodes[0].y
        self.x2, self.y2 = nodes[1].x, nodes[1].y

        self.size =self.max_size - self.max_size * node_dist
        if self.size < self.min_size: self.size = self.min_size

        #print(self.get_angle())
    
    def get_angle(self):
        xdis = self.x1 - self.x2
        ydis = self.y1 - self.y2
        if ydis < 0:
            xdis = self.x2 - self.x1
            ydis = self.y2 - self.y1 

        return math.atan2(ydis, xdis)

    
    def draw(self, surface):
        pygame.draw.line(surface, self.color, (self.x1, self.y1), (self.x2, self.y2), int(self.size))

class Ball:
    def __init__(self, x, y, angle, velocity, size, color):
        self.x, self.y = x, y
        self.size = size
        self.color = color
        self.xv = velocity*math.cos(angle)
        self.yv = velocity*math.sin(angle)
        self.velocity = velocity

    def bounce_off_line(self, laser, collision):
        #print("yay")
        original_xv = self.xv
        if collision == "1": recip = laser.get_angle()+math.pi/2
        elif collision == "2": recip = laser.get_angle()-math.pi/2
        self.xv = (self.velocity*1.3)*math.cos(recip)
        self.yv = (self.velocity*1.3)*math.sin(recip)    
        # if (original_xv< 0 and self.xv <0) or (original_xv> 0 and self.xv >0):
        #     self.xv *= -1
        #     self.yv *= -1


    def update(self, laser):
        if laser.on == True:
            
            collision_point1 = self.x + self.size/2 * math.cos(laser.get_angle() - math.pi/2), self.y + self.size/2 *  math.sin(laser.get_angle() - math.pi/2)
            collision_point2 = self.x - self.size/2 * math.cos(laser.get_angle() - math.pi/2), self.y - self.size/2 *  math.sin(laser.get_angle() - math.pi/2)

            if if_point_on_line(laser.x1, laser.y1, laser.x2, laser.y2, collision_point1, 0.3): 
                self.bounce_off_line(laser, "1")
            elif if_point_on_line(laser.x1, laser.y1, laser.x2, laser.y2, collision_point2, 0.3): 
                self.bounce_off_line(laser, "2")
        
        new_x, new_y = self.x + self.xv, self.y + self.yv
        x_is_valid, y_is_valid = on_screen(size, (new_x, new_y), buffer=self.size/2)
        if x_is_valid: self.x = new_x
        else:
            self.xv *= -1
            self.x += self.xv
        if y_is_valid: self.y = new_y
        else:
            self.yv *= -1
            self.y += self.yv
        
        laser_angle = laser.get_angle()
        perpendicular= laser_angle - math.pi//2



    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, pygame.Rect(self.x-self.size/2, self.y-self.size/2, self.size, self.size))


#--SETTING--#
#general
shake_level = 5
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
}

#player
node_speed = ns = 8

num_balls = 3

node_a = Node(200, 400, (0, 150, 0), bindings, "A", 10, (-ns, ns), (-ns, ns))
node_b = Node(600, 400, (0, 150, 0), bindings, "B", 10, (-ns, ns), (-ns, ns))
laser = Laser((35, 50, 35), 40, bindings)
player = Player(node_a, node_b, laser, bindings)
balls = [Ball(random.randint(100, 700), random.randint(100, 700), random.randint(0, int(math.pi*2)), random.randint(5, 10), random.randint(40, 75), (random.randint(35, 255),random.randint(35, 255), random.randint(35, 255))) for i in range(num_balls)]
shake_amount = 0

while 1:
    now = time.time()
    surface.fill((35, 35, 35))
    keys=pygame.key.get_pressed()
    if keys[K_ESCAPE]:
        quit()
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == bindings["ZAP"]: shake_amount = -shake_level
    
    player.update(keys)
    for ball in balls: ball.update(laser)

    player.draw(surface)
    for ball in balls: ball.draw(surface)
    
    shake_amount = shake(shake_amount, shake_level)
    screen.blit(surface, (shake_amount, shake_amount))

    pygame.display.flip()
    elapsed = time.time()-now
    if elapsed < cycle_time:
        time.sleep(cycle_time-elapsed)

