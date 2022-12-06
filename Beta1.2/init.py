#from sprites import Node, Laser, Ball, Player, Pickup, UI
import sprites
import pygame, sys, time, math, random
import game_objects as gobs
import settings as stgs

#from pygame.constants import K_SPACE, K_ESCAPE, K_w, K_a, K_s, K_d, K_UP, K_DOWN, K_LEFT, K_RIGHT
pygame.init()




def shake(shake_amount):
    return -1*shake_amount//2

def run():
    #------------SETUP------------#
    cycle_time = 1/stgs.max_fps
    screen = pygame.display.set_mode(stgs.screen_size)
    surface = screen.copy()
    node_a = sprites.Node(200, 400, stgs.bindings, "A", 10, (-stgs.ns, stgs.ns), (-stgs.ns, stgs.ns), stgs.screen_size)
    node_b = sprites.Node(600, 400, stgs.bindings, "B", 10, (-stgs.ns, stgs.ns), (-stgs.ns, stgs.ns), stgs.screen_size)
    laser = sprites.Laser((35, 50, 35), 40, stgs.bindings)
    player = sprites.Player(node_a, node_b, laser, stgs.bindings, stgs.screen_size)
    balls = [sprites.Ball(random.randint(100, 200), random.randint(100, 200), random.randint(0, int(math.pi*2)), random.randint(stgs.balls_speed_range[0], stgs.balls_speed_range[1]), random.randint(40, 75), (random.randint(35, 255),random.randint(35, 255), random.randint(35, 255)), stgs.screen_size) for i in range(stgs.num_balls)]
    #pickups = [Pickup(random.randint(0,screen_width), random.randint(0, screen_height), "node") for i in range(num_pickups)]
    ui = sprites.UI(stgs.screen_size)
    pickups = []
    gobs.score = 0


     

    while 1:
        ##--Runs no matter what--#
        surface.fill((35, 35, 35))
        keys=pygame.key.get_pressed()
        now = time.time() 
        if keys[stgs.bindings["QUIT"]]:
                quit()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT: sys.exit()

        #--Runs while Game is being played
        if len(player.nodes) > 0: 
            if now - gobs.last_hit > stgs.qhmulti_interval: gobs.quick_hit_multi = 1

            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == stgs.bindings["ZAP"]: gobs.shake_amount = -stgs.shake_levels["ZAP"]
            
            player.update(keys)
            for ball in balls: ball.update(laser)

            player.check_node_collisions(balls, pickups)

            ui.update(gobs.score, player)
            if gobs.score == stgs.max_score: 
                pickups.append(sprites.Pickup(random.randint(0, stgs.screen_size[0]), random.randint(0, stgs.screen_size[1]), "node"))
                gobs.score = 0

            player.draw(surface)
            for ball in balls: ball.draw(surface)
            for pickup in pickups: pickup.draw(surface)
            ui.display(surface)
        
        else:
            ui.display_game_over(surface)
            if keys[stgs.bindings["PLAY AGAIN"]]:
                return "RUN AGAIN"


        gobs.shake_amount = shake(gobs.shake_amount)
        screen.blit(surface, (gobs.shake_amount, gobs.shake_amount))
        pygame.display.flip()
        elapsed = time.time()-now
        if elapsed < cycle_time:
            time.sleep(cycle_time-elapsed)
        

def main():
    while run() == "RUN AGAIN":
        continue

main()
