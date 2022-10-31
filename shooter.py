import pygame
import random
from os import path

# Directory calls
img_dir = path.join(path.dirname(r"C:\Users\Dagger\Documents\Development\Pygame\Space Shooter\test"), 'img')
sound_dir = path.join(path.dirname(r"C:\Users\Dagger\Documents\Development\Pygame\Space Shooter\test"), 'sound') 

# Window size, FPS, and Powerup Time
WIDTH = 480 # width of game window
HEIGHT = 600 # height of game window
FPS = 60 # frames per second 
POWERUP_TIME = 5000 # time lasting for powerups

# Colors (R,G,B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Initialize pygame and create window
pygame.init()
pygame.mixer.init() # for sound
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SPACE SHOOTER")
clock = pygame.time.Clock()

# Rendering text
font_name = pygame.font.match_font('arial')
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect() 
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

# Generation of new asteroids
def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

# Show shield bar on screen
def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

# Show lives on screen
def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

# Main character
class Player (pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)          # run built-in Sprite classes initializer
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20                             # Circular collision
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250                       # Measures how long in miliseconds the ship should wait before launching another bullet
        self.last_shot = pygame.time.get_ticks()     # Keep track of what time the last bullet was fired
        self.lives = 3                               # Next 3 lines refer to player's lives
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1                               # Track what the power level is
        self.power_time = pygame.time.get_ticks()    # After time has passed, drop the power back down

    def update(self):
        # Timeout for powerups
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        # If hidden after a death, unhide one'se self
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:                   # Moving left
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:                  # Moving Right
            self.speedx = 8
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:                   # Do not go off the screen if too far to the right
            self.rect.right = WIDTH
        if self.rect.left < 0:                        # Do not go off the screen if too far to the left
            self.rect.left = 0
    
    def powerup(self):                                # Set powerup properties
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()                         # Be able to hold space to keep shooting
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:                               # When power is one, default shooting
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                # shoot_sound.play()                          # Play shoot sound
            if self.power >= 2:                               # When power is greater than 2, can shoot 2 bullets spawned at wingtips
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                # shoot_sound.play()                          # Play shoot sound

    def hide(self):
        # hide the player temporarily
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)      # Move player off the screen to not get hit by meteors

# Asteroids
class Mob (pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        self.rect.x = random.randrange(WIDTH - self.rect.width)   # Spawn in random x values between the sides
        self.rect.y = random.randrange(-100, -40)                 # Spawn in y values that is above the top (y <0)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0                                              # Animation of rotating
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

# Shooting bullets
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = - 10

    def update(self):
        self.rect.y += self.speedy
        # kill if it moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()

# Powerups class
class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])         # Restore shield and boost firepower
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        # kill if it moves off the bottom of the screen
        if self.rect.top > HEIGHT:
            self.kill()

# Show explosion on screen
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

# Game Over Screen
def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "SPACE SHOOTER", 64, WIDTH / 2, HEIGHT / 4)                           # Game title
    draw_text(screen, "Arrow keys move, Space to fire", 22, WIDTH / 2, HEIGHT / 2)   # Instructions on how to play
    draw_text(screen, "Press a key to begin", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

# Load all game graphics - background, player, bullet, meteors, explosions, powerups
background = pygame.image.load(path.join(img_dir, "starfield.png")).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir, "playerShip1_orange.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))                              # Mini image used for death screen
player_mini_img.set_colorkey(BLACK)
# meteor_img = pygame.image.load(path.join(img_dir, "meteorBrown_med1.png")).convert()      # Singular meteor image
bullet_img = pygame.image.load(path.join(img_dir, "laserRed16.png")).convert()
meteor_images = []
meteor_list = ['meteorBrown_big1.png', 'meteorBrown_med1.png', 'meteorBrown_med1.png',
               'meteorBrown_med3.png', 'meteorBrown_small1.png', 'meteorBrown_small2.png',
               'meteorBrown_tiny1.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert())
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)                        # Mob hits player and player hits mob explosion
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)                          # Player explosion upon death
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)
powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield_gold.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert()

# Add player sprites
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
for i in range(8):
    newmob()

score = 0
pygame.mixer.music.play(loops=-1)           # Set music before game starts

# Game loop
game_over = True
running = True
while running:
    if game_over:                                # If game over, reset score, meteors, bullets, powerups, player, etc.
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            newmob()
        score = 0
    # keep loop running at the right speed
    clock.tick(FPS)

    # Process input (events)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False
    
    # Update
    all_sprites.update()

    # check to see if a bullet hit a mob // collision - player attacks mob
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius                    # Assign points based on size of meteor
        # random.choice(expl_sounds).play()         # Play random sound whenever we destroy a meteor
        expl = Explosion(hit.rect.center, 'lg')     # Spawn explosion when mob is destroyed
        all_sprites.add(expl)
        if random.random() > 0.9:                   # If player destroys a mob, there's a chance a powerup will drop (10% chance with 0.9)
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        newmob()

    # check to see if mob hits a player // collision - mob attacks player
    hits = pygame.sprite.spritecollide(player, mobs, False, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= 1                          # Remove one from player shield
        expl = Explosion(hit.rect.center, 'sm')     # Spawn explosion when player is hit
        all_sprites.add(expl)
        newmob()
        
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, 'player')           # Explosion animation upon death
            all_sprites.add(death_explosion)
            player.hide()                                                       # Hide the player, subtract the lives, and reset the shield
            player.lives -= 1
            player.shield = 100

    # check to see if player hit a powerup // collision - player gets powerup
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield += random.randrange(10, 30)
            if player.shield >= 100:
                player.shield = 100
        if hit.type == 'gun':
            player.powerup()
            # power_sound,play()                                                 # Play powerup sound

    if player.lives == 0 and not death_explosion.alive():                        # If player died and explosion is complete, end the game
        game_over = True

    # Render (draw)
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, "SCORE: " + str(score), 18, WIDTH / 2, 10)        # Put score on the screen
    draw_shield_bar(screen, 5, 5, player.shield)                        # Put shield bar on the screen
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)   # Put lifelines on the screem
    # *after* drawing everything, flip the display
    pygame.display.flip()

pygame.quit()
