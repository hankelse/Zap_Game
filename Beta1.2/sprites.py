import math, pygame, random
import settings as stgs
import pygame.font
import time
pygame.font.init()
import game_objects as gobs

def point_in_tri(t1, t2, t3, p, buffer=0):
    #point1, point2, point3 = (tri.x+tri.radius*math.cos(tri.angle), tri.y-tri.radius*math.sin(tri.angle)), (tri.x+tri.radius*math.cos(tri.angle-(2*pi/3)), tri.y-tri.radius*math.sin(tri.angle-(2*pi/3))), (tri.x+tri.radius*math.cos(tri.angle+(2*pi/3)), tri.y-tri.radius*math.sin(tri.angle+(2*pi/3)))
    ax, ay = t1[0], t1[1]
    bx, by = t2[0], t2[1]
    cx, cy = t3[0], t3[1]
    px, py = p
    w1 = (ax*(cy-ay) + (py-ay)*(cx-ax)-px*(cy-ay))  /  ((by-ay)*(cx-ax) - (bx-ax)*(cy-ay))
    w2 = (py-ay-w1*(by-ay)) / (cy-ay)
    if w1 >= 0-buffer and w2 >= 0-buffer and (w1+w2) <= 1+buffer: return(True)
    return(False)

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


class Node:
    def __init__(self, startingx, startingy, bindings, type, size, xv_range, yv_range, screen_size):
        
        self.screen_size = screen_size
        self.x, self.y, self.size = startingx, startingy, size 
        self.max_size = 20
        self.min_size = 10
        self.type = type
        self.bindings = bindings
        self.color = stgs.node_colors[type]
        #self.base_color = self.color
 
        self.xv, self.yv = 0, 0
        self.acceleration = 2
        self.deceleration = 0.5
        self.xv_range = self.xv_min, self.xv_max = xv_range
        self.yv_range = self.yv_min, self.yv_max = yv_range
        self.screen_size = screen_size

    def update(self, keys, nodes):
        self.color = stgs.node_colors[self.type]
        self.update_motion(keys, nodes) 
    
    def zap(self):
        self.color = (255, 0, 0)

    def update_motion(self, keys, nodes):
        if self.type == "A" or self.type == "B":
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
            x_is_valid, y_is_valid = on_screen(self.screen_size, (new_x, new_y), buffer=self.size/2)
            if x_is_valid: self.x = new_x
            if y_is_valid: self.y = new_y
        
        elif self.type == "C":
            node_a, node_b = nodes[0], nodes[1]
            node_distance = distance((node_a.x, node_a.y), (node_b.x, node_b.y))
            angle = math.atan2(node_a.y-node_b.y, node_a.x-node_b.x) - 2*math.pi/3
            self.x = node_a.x + math.cos(angle)*node_distance
            self.y = node_a.y + math.sin(angle)*node_distance
            if self.x < self.size/2: self.x = self.size/2
            elif self.x > stgs.screen_width-self.size/2: self.x = stgs.screen_width-self.size/2

            if self.y < self.size/2: self.y = self.size/2
            elif self.y > stgs.screen_height-self.size/2: self.y = stgs.screen_height-self.size/2




    def adjust_size(self, ratio):
        self.size = self.max_size - self.max_size*ratio
        if self.size < self.min_size: self.size = self.min_size

    def draw(self, surface):
        
        pygame.draw.ellipse(surface, self.color, pygame.Rect(self.x-self.size/2, self.y-self.size/2, self.size, self.size))

class Player:
    def __init__(self, node_a, node_b, laser, bindings, screen_size):
        self.screen_size = screen_size
        self.nodes = [node_a, node_b]
        self.laser = laser
        self.bindings = bindings
    
    def update(self, keys): 
        if keys[self.bindings["ZAP"]]:
            
            for node in self.nodes: node.zap()
            self.laser.zap()
            gobs.last_zap = time.time()

        else: #If Zap is not active
            #update Nodes position
            for node in self.nodes: node.update(keys, self.nodes)
            

            #find distance for updated nodes and use to update laser and nodes_size
            if len(self.nodes) > 1: node_dist = self.node_distance()
            else: node_dist = 0.1

            self.laser.update(keys, self.nodes, node_dist)
            for node in self.nodes: node.adjust_size(node_dist)
    
    def check_node_collisions(self, balls, pickups): #checks if nodes have been hit by ball or pickup
        for ball in balls:
            for node in self.nodes:
                if distance((ball.x, ball.y), (node.x, node.y))<= node.size/2 + ball.size/2:
                    gobs.score = gobs.score//2
                    gobs.shake_amount = stgs.shake_levels["NODE HIT"]
                    self.nodes.remove(node)
                    if len(self.nodes) == 2 and (node.type == "A" or node.type == "B"):
                        if self.nodes[0].type == "C": self.nodes[0].type = node.type
                        elif self.nodes[1].type == "C": self.nodes[1].type = node.type
                    pickups.append(Pickup(random.randint(0, self.screen_size[0]), random.randint(0, self.screen_size[1]), "node"))
        
        if len(self.nodes) == 1:
            for pickup in pickups:
                node = self.nodes[0]
                if distance((node.x, node.y), (pickup.x, pickup.y))<= node.size/2 + ball.size/2:
                    if pickup.type == "node":
                        node_type = "A"
                        if self.nodes[0].type == "A": node_type = "B"
                        self.nodes.append(Node(pickup.x, pickup.y, self.bindings, node_type, self.nodes[0].size, self.nodes[0].xv_range, self.nodes[0].yv_range, self.nodes[0].screen_size))
                        pickups.remove(pickup)
        if len(self.nodes) == 2:
            for node in self.nodes:
                for pickup in pickups:
                    if distance((node.x, node.y), (pickup.x, pickup.y))<= node.size/2 + ball.size/2:
                        if pickup.type == "node":
                            node_type = "C"
                            self.nodes.append(Node(pickup.x, pickup.y, self.bindings, node_type, self.nodes[0].size, self.nodes[0].xv_range, self.nodes[0].yv_range, self.nodes[0].screen_size))
                            pickups.remove(pickup)


    
    def node_distance(self):

        xdis = abs(self.nodes[0].x-self.nodes[1].x)
        ydis = abs(self.nodes[0].y-self.nodes[1].y)
        distance = math.sqrt(xdis**2 + ydis**2)

        distance = 1*distance/1131
        return distance


    def draw(self, surface):
        if len(self.nodes) > 1:
            self.laser.draw(surface)
        for node in self.nodes: node.draw(surface)
        
class Laser:
    def __init__(self, color, size, bindings):
        self.base_color = color
        self.color,  self.size = color, size
        self.min_size = 5
        self.max_size = 10
        self.x1, self.x2, self.y1, self.y2 = 0, 0, 0, 0
        self.bindings = bindings
        self.on=False
        self.triangulate = False
    
        
    def zap(self): 
        self.on = True
        self.color = (150, 25, 25)
    
    def update(self, keys, nodes, node_dist):
        self.color = self.base_color
        if len(nodes) == 3:
            self.triangulate = True
            self.on = False
            self.x1, self.y1 = nodes[0].x, nodes[0].y
            self.x2, self.y2 = nodes[1].x, nodes[1].y
            self.x3, self.y3 = nodes[2].x, nodes[2].y
        
        elif len(nodes) == 2:
            self.triangulate = False
            self.on = False
            self.color = self.base_color
            self.x1, self.y1 = nodes[0].x, nodes[0].y
            self.x2, self.y2 = nodes[1].x, nodes[1].y

            self.size =self.max_size - self.max_size * node_dist
            if self.size < self.min_size: self.size = self.min_size
        else: 
            self.triangulate = False
            self.x1 = self.x2 = self.y1 = self.y2 = -10000

    
    def get_angle(self):
        if self.triangulate == False:
            xdis = self.x1 - self.x2
            ydis = self.y1 - self.y2
            if ydis < 0:
                xdis = self.x2 - self.x1
                ydis = self.y2 - self.y1 

            return math.atan2(ydis, xdis)
        else:
            xdis = self.x1 - self.x2
            ydis = self.y1 - self.y2
            if ydis < 0:
                xdis = self.x2 - self.x1
                ydis = self.y2 - self.y1 
            angle1 = math.atan2(ydis, xdis)

            xdis = self.x1 - self.x3
            ydis = self.y1 - self.y3
            if ydis < 0:
                xdis = self.x3 - self.x1
                ydis = self.y3 - self.y1 
            angle2 = math.atan2(ydis, xdis)

            xdis = self.x2 - self.x3
            ydis = self.y2 - self.y3
            if ydis < 0:
                xdis = self.x3 - self.x2
                ydis = self.y3 - self.y2 
            angle3 = math.atan2(ydis, xdis)

            return angle1, angle2, angle3


    
    def draw(self, surface):
        if self.triangulate == True:
            if self.on == False: pygame.draw.polygon(surface, self.color, ((self.x1, self.y1), (self.x2, self.y2), (self.x3, self.y3)), int(self.size))
            else: 
                pygame.draw.polygon(surface, self.color, ((self.x1, self.y1), (self.x2, self.y2), (self.x3, self.y3)))
                pygame.draw.polygon(surface, self.color, ((self.x1, self.y1), (self.x2, self.y2), (self.x3, self.y3)), int(self.size))
        else: pygame.draw.line(surface, self.color, (self.x1, self.y1), (self.x2, self.y2), int(self.size))
        #angle = self.get_angle() - math.pi/2
        # pygame.draw.line(surface, (255, 0, 0), (self.x1+math.cos(angle)/2, self.y1+math.sin(angle)/2), (self.x2+math.cos(angle)/4, self.y2+math.sin(angle)/4), int(self.size/2))
        # pygame.draw.line(surface, (0, 0, 255), (self.x1-math.cos(angle)/2, self.y1-math.sin(angle)/2), (self.x2-math.cos(angle)/4, self.y2-math.sin(angle)/4), int(self.size/2))
        

class Ball:
    def __init__(self, x, y, angle, velocity, size, color, screen_size):
        self.x, self.y = x, y
        self.size = size
        self.color = color
        self.xv = velocity*math.cos(angle)
        self.yv = velocity*math.sin(angle)
        self.velocity = velocity
        self.screen_size = screen_size

    def bounce_off_line(self, laser, collision, index=None):
        #print("yay")
        if index == None:
            original_xv = self.xv
            if collision == "1": recip = laser.get_angle()+math.pi/2
            elif collision == "2": recip = laser.get_angle()-math.pi/2
            

        else:
            angles = laser.get_angle()
            if collision == "1": recip = angles[index]+math.pi/2
            elif collision == "2": recip = angles[index]-math.pi/2
        
        self.xv = (self.velocity*1.3)*math.cos(recip)
        self.yv = (self.velocity*1.3)*math.sin(recip)



    def update(self, laser, nodes): #checks for bounces off laser, adds to score, checks for off screen, moves ball
        if laser.on == True:
            if laser.triangulate== False:
            
                collision_point1 = self.x + self.size/2 * math.cos(laser.get_angle() - math.pi/2), self.y + self.size/2 *  math.sin(laser.get_angle() - math.pi/2)
                collision_point2 = self.x - self.size/2 * math.cos(laser.get_angle() - math.pi/2), self.y - self.size/2 *  math.sin(laser.get_angle() - math.pi/2)

                collisions = 1
                if if_point_on_line(laser.x1, laser.y1, laser.x2, laser.y2, collision_point1, 0.3): 
                    
                    self.bounce_off_line(laser, "1")
                    if gobs.last_side_hit == "2": gobs.alt_streak_multi *= stgs.alt_strk_multi
                    elif gobs.last_hit == "1": gobs.alt_streak_multi = 1
                    gobs.last_side_hit = "1"
                    #print(gobs.last_side_hit)   
                elif if_point_on_line(laser.x1, laser.y1, laser.x2, laser.y2, collision_point2, 0.3):
                    
                    self.bounce_off_line(laser, "2")
                    if gobs.last_side_hit == "1": gobs.alt_streak_multi *= stgs.alt_strk_multi
                    elif gobs.last_hit == "2": gobs.alt_streak_multi = 1
                    gobs.last_side_hit = "2"
                    #print(gobs.last_side_hit) 
                else: collisions = 0           
                if collisions == 1: 
                    if time.time() - gobs.last_hit < stgs.qhmulti_interval: 
                        gobs.quick_hit_multi *= stgs.quick_hit_multi
                    gobs.last_hit = time.time()
                    laser_length = distance((laser.x1, laser.y1), (laser.x2, laser.y2))
                    gobs.shake_amount = stgs.shake_levels["BALL HIT"]/1131 * (1131-laser_length)
                    score_addition = collisions * (   (20/1131) *  ( 1131 -  laser_length)  ) * gobs.quick_hit_multi * gobs.alt_streak_multi 
                    if score_addition != 0:
                        #print(round(score_addition, 2))
                        if gobs.score+score_addition <= stgs.max_score: gobs.score += score_addition
                        else: gobs.score = stgs.max_score
                
                # score_addition += points_earned * (20/1131)*()
            elif len(nodes) == 3:

                if point_in_tri((laser.x1, laser.y1), (laser.x2, laser.y2), (laser.x3, laser.y3), (self.x, self.y)):
                    gobs.shake_amount = stgs.shake_levels["BALL DESTROYED"]
                    gobs.score += (stgs.max_score - gobs.score)//stgs.num_balls
                    return False
                
                else:
                    angles = laser.get_angle()
                    for index, laser_side in enumerate([((laser.x1, laser.y1), (laser.x2, laser.y2)), ((laser.x1, laser.y1), (laser.x3, laser.y3)), ((laser.x3, laser.y3), (laser.x2, laser.y2))]):
                        point1, point2 = laser_side
                        collision_point1 = self.x + self.size/2 * math.cos(angles[index] - math.pi/2), self.y + self.size/2 *  math.sin(angles[index] - math.pi/2)
                        collision_point2 = self.x - self.size/2 * math.cos(angles[index] - math.pi/2), self.y - self.size/2 *  math.sin(angles[index] - math.pi/2)
                        collisions = 1
                        if if_point_on_line(point1[0], point1[1], point2[0], point2[1], collision_point1, 0.3): 
                            self.bounce_off_line(laser, "1", index)
                        elif if_point_on_line(point1[0], point1[1], point2[0], point2[1], collision_point2, 0.3):
                            self.bounce_off_line(laser, "2", index)
                        else: collisions = 0           
                        if collisions == 1: 
                            if time.time() - gobs.last_hit < stgs.qhmulti_interval: 
                                gobs.quick_hit_multi *= stgs.quick_hit_multi
                            gobs.last_hit = time.time()
                            laser_length = distance((laser.x1, laser.y1), (laser.x2, laser.y2))
                            gobs.shake_amount = stgs.shake_levels["BALL HIT"]/1131 * (1131-laser_length)
                            score_addition = collisions * (   (20/1131) *  ( 1131 -  laser_length)  ) * gobs.quick_hit_multi * gobs.alt_streak_multi
                            if score_addition != 0:
                                #print(round(score_addition, 2))
                                if gobs.score+score_addition <= stgs.max_score: gobs.score += score_addition
                                else: gobs.score = stgs.max_score
                



        new_x, new_y = self.x + self.xv, self.y + self.yv
        x_is_valid, y_is_valid = on_screen(self.screen_size, (new_x, new_y), buffer=self.size/2)
        if x_is_valid: self.x = new_x
        else:
            self.xv *= -1
            self.x += self.xv
        if y_is_valid: self.y = new_y
        else:
            self.yv *= -1
            self.y += self.yv

        
        #laser_angle = laser.get_angle()
        #perpendicular= laser_angle - math.pi//2


        #return score_addition
    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, pygame.Rect(self.x-self.size/2, self.y-self.size/2, self.size, self.size))

class Pickup:
    def __init__ (self, x, y, type):
        self.type = type
        self.x, self.y = x, y
        self.get_info()
    
    def get_info(self):
        if self.type == "node":
            self.size = 15
            self.color = (0, 150, 0)
    
    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, pygame.Rect(self.x-self.size/2, self.y-self.size/2, self.size, self.size))
        pygame.draw.ellipse(surface, (35, 35, 35), pygame.Rect(self.x-self.size/4, self.y-self.size/4, self.size/2, self.size/2))

class UI:
    def __init__(self, screen_size):
        self.scrn_size = self.scrn_width, self.scrn_height = screen_size
        self.max_score = stgs.max_score
        self.score = 0
        self.potential_score = 0
        self.width, self.height =  self.scrn_width/4, self.scrn_width/40
        self.p_font = pygame.font.SysFont(stgs.font_name, int(self.height*1/2))
        self.s_font = pygame.font.SysFont(stgs.font_name, int(self.height))
        self.m_font = pygame.font.SysFont(stgs.font_name, int(self.height*1/3))
        

        self.game_over_font = pygame.font.SysFont(stgs.font_name, stgs.screen_height//10)
        self.game_over_surface = self.game_over_font.render(("GAME OVER"), None, (140, 150, 140))
        self.game_over_text_coords = 400-self.game_over_surface.get_width()/2, 400-self.game_over_surface.get_height()/2

        self.win_font = pygame.font.SysFont(stgs.font_name, stgs.screen_height//10)
        self.win_surface = self.win_font.render(("YOU WON!"), None, (140, 150, 140))
        self.win_text_coords = 400-self.win_surface.get_width()/2, 400-self.win_surface.get_height()/2

        self.play_again_font = pygame.font.SysFont(stgs.font_name, stgs.screen_height//40)
        self.play_again_surface = self.play_again_font.render(("press 'r' to play again!"), None, (140, 150, 140))
        #self.play_again_surface = self.play_again_font.render(("press '"+str(stgs.bindings["PLAY AGAIN"])+"' to play again!"), None, (140, 150, 140))
        self.play_again_text_coords = 400-self.play_again_surface.get_width()/2, 600-self.play_again_surface.get_height()/2

        self.welc_font = pygame.font.SysFont(stgs.font_name, stgs.screen_height//20)
        self.welc_surface = self.welc_font.render(("Press Space to Begin"), None, (140, 150, 140))
        self.welc_text_coords = 400-self.welc_surface.get_width()/2, 400-self.welc_surface.get_height()/2

    def update(self, score, player):
        #self.potential_score = score*node_distance
        self.score = score
        if len(player.nodes) == 1:
            self.potential_score = score
        else: 
            self.potential_score = score +  (20/1131) *  ( 1131 - distance((player.laser.x1, player.laser.y1), (player.laser.x2, player.laser.y2)) )
            if self.potential_score > self.max_score: self.potential_score = self.max_score
        
    
    def display(self, surface):
        score_percent = self.score/self.max_score
        potential_score_percent = self.potential_score/self.max_score
        bonus_score_percent = (((self.potential_score-self.score)*gobs.quick_hit_multi*gobs.alt_streak_multi)+self.score)/self.max_score
        self.x, self.y = self.scrn_width*(1/20), self.scrn_height*(1/40)
        pygame.draw.rect(surface, (50, 50, 50), pygame.Rect(self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, (50, 200, 50), pygame.Rect(self.x, self.y, self.width*(bonus_score_percent), self.scrn_width/40))
        pygame.draw.rect(surface, (50, 150, 50), pygame.Rect(self.x, self.y, self.width*potential_score_percent, self.scrn_width/40))
        pygame.draw.rect(surface, (50, 100, 50), pygame.Rect(self.x, self.y, self.width*score_percent, self.scrn_width/40))
        
        multi_surface = self.m_font.render(str(" x"+str(round(gobs.quick_hit_multi*gobs.alt_streak_multi, 2))), None, (140, 150, 140))
        score_surface = self.s_font.render(str( str(math.floor(gobs.score)) + " "), None, (255, 255, 255))
        potent_surface = self.p_font.render(str("+" + str(math.floor(self.potential_score-gobs.score))), None, (150, 150, 150))
        
        surface.blit(score_surface, ( (self.x+self.width/2) - score_surface.get_width()/2  , (self.y+self.height/2)-score_surface.get_height()/2))
        surface.blit(potent_surface, ( (self.x+self.width/2) + score_surface.get_width()/2 + potent_surface.get_width()/2 , (self.y+self.height*(1/2))-potent_surface.get_height()/2))
        surface.blit(multi_surface, ( (self.x+self.width/2) + score_surface.get_width()/2 + 1.25*potent_surface.get_width() + multi_surface.get_width()/2 , (self.y+self.height*(1/2))-multi_surface.get_height()/2))

    def display_game_over(self, surface):
        surface.blit(self.game_over_surface, (self.game_over_text_coords))
    
    def display_win(self, surface):
        surface.blit(self.win_surface, (self.win_text_coords))
    
    def display_play_again(self, surface):
        surface.blit(self.play_again_surface, (self.play_again_text_coords))

    def display_welcome(self, surface):
        surface.blit(self.welc_surface, (self.welc_text_coords))