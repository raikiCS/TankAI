import pygame
import random
import os
import time
import neat
import visualize 
import pickle
pygame.font.init()  # init font


"""
Load a bunch of images
"""
sprites = pygame.transform.scale(pygame.image.load("images/sprites.gif"), [192, 224])
img_tanks = [
    sprites.subsurface(32*2, 0, 13*2, 15*2),
	sprites.subsurface(48*2, 0, 13*2, 15*2),
	sprites.subsurface(64*2, 0, 13*2, 15*2),
	sprites.subsurface(80*2, 0, 13*2, 15*2)
]

img_arrows = [
	sprites.subsurface(81*2, 48*2, 7*2, 7*2),
	sprites.subsurface(88*2, 48*2, 7*2, 7*2)
]

img_enemies = [
	sprites.subsurface(32*2, 0, 13*2, 15*2),
	sprites.subsurface(48*2, 0, 13*2, 15*2),
	sprites.subsurface(64*2, 0, 13*2, 15*2),
	sprites.subsurface(80*2, 0, 13*2, 15*2),
	sprites.subsurface(32*2, 16*2, 13*2, 15*2),
	sprites.subsurface(48*2, 16*2, 13*2, 15*2),
	sprites.subsurface(64*2, 16*2, 13*2, 15*2),
	sprites.subsurface(80*2, 16*2, 13*2, 15*2)
]

bullet_img = sprites.subsurface(75*2, 74*2, 3*2, 4*2)

explosion_images = [
	sprites.subsurface(0, 80*2, 32*2, 32*2),
	sprites.subsurface(32*2, 80*2, 32*2, 32*2),
]

tile_images = [
	pygame.Surface((8*2, 8*2)),
	sprites.subsurface(48*2, 64*2, 8*2, 8*2),
	sprites.subsurface(48*2, 72*2, 8*2, 8*2),
	sprites.subsurface(56*2, 72*2, 8*2, 8*2),
	sprites.subsurface(64*2, 64*2, 8*2, 8*2),
	sprites.subsurface(64*2, 64*2, 8*2, 8*2),
	sprites.subsurface(72*2, 64*2, 8*2, 8*2),
	sprites.subsurface(64*2, 72*2, 8*2, 8*2)
]

tile_empty = tile_images[0]
tile_brick = tile_images[1]
tile_steel = tile_images[2]
tile_grass = tile_images[3]
tile_water = tile_images[4]
tile_water1= tile_images[4]
tile_water2= tile_images[5]
tile_froze = tile_images[6]

TILE_SIZE = 16
mapr = []
obstacle_rects = []
bullets = []
tanks = []



"""
draw images on screen
"""
def draw_window(win, tanks):
    win.fill((0,0,0))
    #win.blit(img_tanks[1], (100, 100))
    #win.blit(img_enemies[5], (150, 100))
    #win.blit(sprites.subsurface(0, 15*2, 16*2, 16*2), (120, 150))
    #win.blit(explosion_images[0], (30, 100))
    #win.blit(explosion_images[1], (60, 100))
    #win.blit(bullet, (30, 30))
    draw_level(win)
    for tank in tanks:
        tank.draw(win)
    for bullet in bullets:
        bullet.draw(win)
    win.fill([100, 100, 100], pygame.Rect([416, 0], [64, 416]))
    win.fill([100, 100, 100], pygame.Rect([0, 0], [416, 32]))

    pygame.display.flip()
    pygame.display.update()


"""
Load a txt file, convert it to an array of a tuple which contains 'x','y', and type of tile.
"""
def loadLevel(level_nr = 1):
	""" Load specified level
	@return boolean Whether level was loaded
	"""
	filename = "./"+str(level_nr)
	if (not os.path.isfile(filename)):
		return False
	level = []
	f = open(filename, "r")
	data = f.read().split("\n")
	x, y = 0, 0
	for row in data:
		for ch in row:
            # TILE SIZE IS STIRICTLY 16 but for bug issues, it is reduced

			if ch == "#":
				mapr.append((pygame.Rect(x, y, 16, 16),1))
			elif ch == "@":
				mapr.append((pygame.Rect(x, y, 16, 16), 2))
			elif ch == "~":
				mapr.append((pygame.Rect(x, y, 16, 16), 4))
			elif ch == "%":
				mapr.append((pygame.Rect(x, y, 16, 16), 3))
			elif ch == "-":
				mapr.append((pygame.Rect(x, y, 16, 16), 4))
			x += TILE_SIZE
		x = 0
		y += TILE_SIZE
    
	

"""
draw level
"""
def draw_level(win):
    for tile, img_num in mapr:
        win.blit(tile_images[img_num], (tile.left, tile.top))

def update_level():
    for tile, _ in mapr:
        obstacle_rects.append(tile)


#fitness config
def main(genomes, config):

    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)


        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)
        clock = pygame.time.Clock()
        win = pygame.display.set_mode((480, 416))
        loadLevel()
        run = True
        tank = Tank(16 * TILE_SIZE, 16 * TILE_SIZE)
        #enemy = Enemy(random.randrange(1, 10, 1) * 4 * TILE_SIZE, random.randrange(1, 10, 1) * 4 * TILE_SIZE)
        enemy = Enemy(4 * TILE_SIZE, 4 * TILE_SIZE)
        tanks = [tank, enemy]
        totaltime = 0
        enemy.health = 200
        previous_enemy_health = enemy.health
        previous_tank_health = tank.health

        while run:
            
            pygame.event.get()
            enemy.update(tank)

            #keys = pygame.key.get_pressed()
            #update_level()
            #pygame.time.set_timer(enemy.update(), 1000)
            
            tank.hit_bullet()
            enemy.hit_bullet()
            for bullet in bullets:
                if bullet.state == 0:
                    bullets.remove(bullet)
                else:
                    bullet.update()

            """
            keys = pygame.key.get_pressed()
            if keys:
                if keys[pygame.K_UP]:
                    tank.rotate(0)
                elif keys[pygame.K_DOWN]:
                    tank.rotate(2)
                elif keys[pygame.K_LEFT]:
                    tank.rotate(3)
                elif keys[pygame.K_RIGHT]:
                    tank.rotate(1)
                elif keys[pygame.K_g]:
                    tank.fire()
            """
            if enemy.line_sight(tank):
                genome.fitness -= 5

            if (abs(tank.position.x - enemy.position.x) <= 8) or (abs(tank.position.y - enemy.position.y) <= 8):
                genome.fitness += 1

            #genome.fitness += 0.01
            if tank.collide(tank.direction):
                genome.fitness -= 1

            if previous_enemy_health > enemy.health:
                genome.fitness += 5
                previous_enemy_health = enemy.health

            if previous_tank_health > tank.health:
                genome.fitness -= 5
                previous_tank_health = tank.health


            output = net.activate((abs(tank.position.x - enemy.position.x), abs(tank.position.y - enemy.position.y)))
            #print(output)
            """
            if -1 <= output[0] <= -0.4:
                tank.rotate(0)
                tank.fire()
            if -0.4 < output[0] <= -0.8:
                tank.rotate(2)
                tank.fire()
            if -0.8 < output[0] <= 1.2:
                tank.rotate(3)
                tank.fire()
            if 1.2 < output[0] <= 1.6:
                tank.rotate(1)
                tank.fire()
            if 1.6 < output[0] <= 2:
                tank.fire()
            """


            action = output.index(max(output))
            
            #print(output)
            if action == 0:
                tank.fire()
            elif action == 1:
                tank.rotate(0)
            elif action == 2:
                tank.rotate(1)
            elif action == 3:
                tank.rotate(2)
            elif action == 4:
                tank.rotate(3)
            
            if random.randrange(0, 2, 1) > 0:
                #action = random.randrange(0, 5, 1)
                if action == 0:
                    tank.fire()
                elif action == 1:
                    tank.rotate(0)
                elif action == 2:
                    tank.rotate(1)
                elif action == 3:
                    tank.rotate(2)
                elif action == 4:
                    tank.rotate(3)

            """
            if output[0] > 0.2:
                tank.fire()
            if output[1] > 0.2:
                tank.rotate(0)
            if output[2] > 0.2:
                tank.rotate(1)
            if output[3] > 0.2:
                tank.rotate(2)
            if output[4] > 0.2:
                tank.rotate(3)
            """


            if tank.state == 1:
                genome.fitness -= 100
                run == False
                #quit()
                break
            
            if enemy.state == 1:
                genome.fitness += 100
                run == False
                #quit()
                break

            draw_window(win, tanks)
    


class Tank:
    (STATE_ALIVE, STATE_DEAD) = range(2)
    (DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)
    max_active_bullets = 1
    active_bullets = 0

    def __init__(self, position_x, position_y):
        self.health = 100
        #originally speed = 2
        self.speed = 2
        self.max_active_bullets = 1
        self.image = img_tanks[0]
        self.position = pygame.Rect(position_x, position_y, 26, 26)
        self.state = self.STATE_ALIVE
        self.direction = 0
        self.max_active_bullets = 1
        self.active_bullets = 0
        self.player = 0
        self.collided = False


        self.image_up = self.image
        self.image_left = pygame.transform.rotate(self.image, 90)
        self.image_down = pygame.transform.rotate(self.image, 180)
        self.image_right = pygame.transform.rotate(self.image, 270)

    def draw(self, win):
        if self.state == self.STATE_ALIVE:
            win.blit(self.image, (self.position.left, self.position.top))

    def rotate(self, direction):
        self.direction = direction
        
        #The next condition is for edge boundary
        if direction == self.DIR_UP and (self.position.y - 2) > 32:
            self.image = self.image_up
            self.position.y -= 2
        elif direction == self.DIR_RIGHT and (self.position.x + 2) < (416 - 26):
            self.image = self.image_right
            self.position.x += 2
        elif direction == self.DIR_DOWN and (self.position.y + 2) < (416 - 26):
            self.image = self.image_down
            self.position.y += 2
        elif direction == self.DIR_LEFT and (self.position.x - 2) > 0:
            self.image = self.image_left
            self.position.x -= 2

        self.collide(direction)

    def fire(self):
        if self.active_bullets > self.max_active_bullets:
            self.active_bullets = 0
            return False
        bullet = Bullet(self.position.topleft, self.direction, self.player)
        bullets.append(bullet)
        self.active_bullets += 1

    def collide(self, direction):
        for tile, _ in mapr:
            if self.position.colliderect(tile):
                if direction == 1: # Moving right; Hit the left side of the wall
                    self.position.right = tile.left
                    #self.position.x -= 2
                if direction == 3: # Moving left; Hit the right side of the wall
                    self.position.left = tile.right
                    #self.position.x += 2
                if direction == 2: # Moving down; Hit the top side of the wall
                    self.position.bottom = tile.top
                    #self.position.y -= 2
                if direction == 0: # Moving up; Hit the bottom side of the wall
                    self.position.top = tile.bottom
                    #self.position.y += 2
                self.collided = True
                #try to open path when collide
                if(random.randint(0, 1)==1):
                    self.direction = random.randint(0, 3)
                else:
                    self.fire()
                return True

                if direction == self.DIR_UP and (self.position.y - 2) > 32:
                    self.collided = True
                    #try to open path when collide
                    if(random.randint(0, 1)==1):
                        self.direction = random.randint(0, 3)
                    else:
                        self.fire()
                    return True
                elif direction == self.DIR_RIGHT and (self.position.x + 2) < (416 - 26):
                    self.collided = True
                    #try to open path when collide
                    if(random.randint(0, 1)==1):
                        self.direction = random.randint(0, 3)
                    else:
                        self.fire()
                    return True
                elif direction == self.DIR_DOWN and (self.position.y + 2) < (416 - 26):
                    self.collided = True
                    #try to open path when collide
                    if(random.randint(0, 1)==1):
                        self.direction = random.randint(0, 3)
                    else:
                        self.fire()
                    return True
                elif direction == self.DIR_LEFT and (self.position.x - 2) > 0:
                    self.collided = True
                    #try to open path when collide
                    if(random.randint(0, 1)==1):
                        self.direction = random.randint(0, 3)
                    else:
                        self.fire()
                    return True

        self.collided = False
        return False

    def hit_bullet(self):
        for bullet in bullets:
            if self.position.colliderect(bullet.rect):
                if bullet.owner != self.player:
                    bullet.state = 0
                    if bullet.owner != 0:
                        self.health -= bullet.damage
                    else:
                        self.health -= bullet.damage + 2
        if self.health < 0:
            self.state = self.STATE_DEAD
            if self.player == 0:
                print("enemy won")
            else:
                print("player won")



class Bullet:
    (STATE_REMOVED, STATE_ACTIVE, STATE_EXPLODING) = range(3)
    (DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)
    (OWNER_PLAYER, OWNER_ENEMY) = range(2)

    def __init__(self, position, direction, owner):
        self.direction = direction
        self.damage = 5
        self.owner = owner
        self.image = bullet_img
        self.state = self.STATE_ACTIVE
        #originally 8
        self.speed = 8
        self.tanks = tanks

        if direction == self.DIR_UP:
            #self.rect = pygame.Rect(position.x, position.y, 6, 8)
            self.rect = pygame.Rect(position[0] + 11, position[1] - 8, 6, 8)
        elif direction == self.DIR_RIGHT:
            self.image = pygame.transform.rotate(self.image, 270)
            #self.rect = pygame.Rect(position.x, position.y, 8, 6)
            self.rect = pygame.Rect(position[0] + 26, position[1] + 11, 8, 6)
        elif direction == self.DIR_DOWN:
            self.image = pygame.transform.rotate(self.image, 180)
            #self.rect = pygame.Rect(position.x, position.y, 6, 8)
            self.rect = pygame.Rect(position[0] + 11, position[1] + 26, 6, 8)
        elif direction == self.DIR_LEFT:
            self.image = pygame.transform.rotate(self.image, 90)
            #self.rect = pygame.Rect(position.x, position.y, 8, 6)
            self.rect = pygame.Rect(position[0] - 8 , position[1] + 11, 8, 6)
    
    def draw(self, win):
        if self.state == self.STATE_ACTIVE:
            win.blit(self.image, self.rect.topleft)
        elif self.state == self.STATE_EXPLODING:
            self.explosion.draw()

    def update(self):
        if (self.rect.y - 2) < 32:
            self.state = 0
        elif (self.rect.x + 2) > (416):
            self.state = 0
        elif (self.rect.y + 2) > (416):
            self.state = 0
        elif (self.rect.x - 2) < 0:
            self.state = 0

        if self.direction == self.DIR_UP:
            self.rect.topleft = [self.rect.left, self.rect.top - self.speed]
            if self.rect.top < 0:
                return
        elif self.direction == self.DIR_RIGHT:
            self.rect.topleft = [self.rect.left + self.speed, self.rect.top]
            if self.rect.left > (416 - self.rect.width):
                return
        elif self.direction == self.DIR_DOWN:
            self.rect.topleft = [self.rect.left, self.rect.top + self.speed]
            if self.rect.top > (416 - self.rect.height):
                return
        elif self.direction == self.DIR_LEFT:
            self.rect.topleft = [self.rect.left - self.speed, self.rect.top]
            if self.rect.left < 0:
                return

        tile_list = [x[0] for x in mapr]
        collision = self.rect.collidelist(tile_list)
        if collision != -1:
            self.state = 0
            self.speed = 0
            mapr.remove(mapr[collision])
        return


class Enemy(Tank):
    def __init__(self, position_x, position_y):
        Tank.__init__(self, position_x, position_y)
        self.image = img_tanks[3]
        self.image_up = self.image;
        self.image_left = pygame.transform.rotate(self.image, 90)
        self.image_down = pygame.transform.rotate(self.image, 180)
        self.image_right = pygame.transform.rotate(self.image, 270)
        self.player = 1
        self.rand_move = 0
        self.start_ticks = pygame.time.get_ticks()
        self.randomMovementCount = 1

    def update(self, tank):
        """

        if self.collide(self.direction) or ((self.position.y - 2) > 32) or ((self.position.x + 2) < (416 - 26)) or ((self.position.y + 2) < (416 - 26)) or ((self.position.x - 2) > 0):
            self.rotate(random.randrange(0, 4, 1))
            self.rotate(self.direction)
            self.rotate(self.direction)
            self.rotate(self.direction)
            self.fire()
        else:
            self.fire()
            
        """
        

        if self.line_sight(tank) and ((abs(tank.position.x - self.position.x) + abs(tank.position.y - self.position.y))  >= 32):
            #self.rotate(random.randrange(0, 4, 1))
            self.fire()
        else:
            if ((pygame.time.get_ticks()-self.start_ticks)/1000) > 0.01:
                self.randomMovementCount = self.randomMovementCount - 1
                if (self.randomMovementCount==0):
                    self.randomMovementCount = random.randrange(1, 40, 1)
                    self.direction = random.randint(0, 3)
                    self.rotate(self.direction)
                    self.rotate(self.direction)
                    self.rotate(self.direction)
                    self.rotate(self.direction)
                else:                    
                    self.rotate(self.direction)
                    self.rotate(self.direction)
                    self.rotate(self.direction)
                    self.rotate(self.direction)
                    if (random.randrange(0, 5, 1)==1):
                        self.fire() #chance of firing randomly
                self.start_ticks = pygame.time.get_ticks()

        """
        else:
            self.rotate(random.randrange(0, 4, 1))
            self.rotate(self.direction)
            self.rotate(self.direction)
            self.rotate(self.direction)
            self.rotate(self.direction)
            self.fire()
            self.rand_move = 0
        """




    def line_sight(self, tank):
        if (abs(tank.position.x - self.position.x) <= 10):
            if (tank.direction == 0 or tank.direction == 1 or tank.direction == 3):
                if (self.direction == 2) and ((self.position.y - tank.position.y) <= 0):
                    return True
                elif (self.direction == 0) and ((self.position.y - tank.position.y) >= 0):
                    return True
            if (tank.direction == 2 or tank.direction == 1 or tank.direction == 3):
                if (self.direction == 0) and ((self.position.y - tank.position.y) >= 0):
                    return True
                elif (self.direction == 2) and ((self.position.y - tank.position.y) <= 0):
                    return True
        elif (abs(tank.position.y - self.position.y) <= 10):
            if (tank.direction == 1 or tank.direction == 0 or tank.direction == 2):
                if (self.direction == 3) and ((self.position.x - tank.position.x) >= 0):
                    return True
                elif (self.direction == 1) and ((self.position.x - tank.position.x) <= 0):
                    return True
            if (tank.direction == 3 or tank.direction == 0 or tank.direction == 2):
                if (self.direction == 1) and ((self.position.x - tank.position.x) <= 0):
                    return True
                elif (self.direction == 3) and ((self.position.x - tank.position.x) >= 0):
                    return True
        
        return False



#Load config file
def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                    neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    #running fitness function
    winner = p.run(main, 5)
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)