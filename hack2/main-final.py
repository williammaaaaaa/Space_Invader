import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invader")

# Load images
RED_SPACE_SHIP = pygame.transform.scale(pygame.image.load("enemy.png"),(50,50))
GREEN_SPACE_SHIP = pygame.transform.scale(pygame.image.load("enemy2.png"),(50,50))
BLUE_SPACE_SHIP = pygame.transform.scale(pygame.image.load("enemy3.png"),(50,50))
BOSS_SPACE_SHIP = pygame.transform.scale(pygame.image.load("boss.png"),(75,75))
# Player player
YELLOW_SPACE_SHIP = pygame.transform.scale(pygame.image.load("player3.png"),(50,50))

# Lasers
RED_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_laser_red.png")), (50, 50))
GREEN_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_laser_green.png")),(50,50))
BLUE_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_laser_blue.png")),(50,50))
YELLOW_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png")),(50,50))

# Background
BG = pygame.transform.scale(pygame.image.load("background.png"), (WIDTH, HEIGHT))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        obj.health -= 100
                        if obj.health == 0:
                            objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Boss(Ship):
    COLOR_MAP = {
        "boss": (BOSS_SPACE_SHIP, BLUE_LASER)
    }
    def __init__(self, x, y, color, health=300):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.direction_timer = 0
        self.change_direction_interval = random.randint(50, 200)

    def move_random(self, vel):
        if self.direction_timer <= 0:
            self.direction = random.choice([-1, 1])  # Randomly choose -1 (left) or 1 (right)
            self.direction_timer = self.change_direction_interval
        new_x = self.x + self.direction * vel
        if 0 <= new_x <= WIDTH - self.get_width():
            self.x = new_x
        self.y += vel
        self.direction_timer -= 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER),
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.direction_timer = 0
        self.change_direction_interval = random.randint(50, 200)

    def move_random(self, vel):
        if self.direction_timer <= 0:
            self.direction = random.choice([-1, 1])
            self.direction_timer = self.change_direction_interval
        new_x = self.x + self.direction * vel
        if 0 <= new_x <= WIDTH - self.get_width():
            self.x = new_x
        self.y += vel
        self.direction_timer -= 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()

        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.clicked = False

    def draw(self):
        WIN.blit(self.image, (self.rect.x, self.rect.y))

    def clicker_action(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        return action

class Menu():
    def __init__(self):
        single_player_img = pygame.image.load("p1.png").convert_alpha()
        two_player_img = pygame.image.load("p2.png").convert_alpha()
        exit = pygame.image.load("exit.png").convert_alpha()
        self.p1 = Button(200, 260, single_player_img, 0.4)
        self.p2 = Button(200, 360, two_player_img, 0.38)
        self.exit =  Button(200, 460, exit, 0.4)

    def init_menu(self):
        # pygame.draw.rect(WIN, (47, 5, 105), pygame.Rect(100, 30, 600, 500))
        self.p1.draw()
        self.p2.draw()
        self.exit.draw()

class PauseMenu:
    def __init__(self):
        resume_img = pygame.image.load("p1.png").convert_alpha()
        exit_img = pygame.image.load("exit.png").convert_alpha()
        self.resume_button = Button(200, 260, resume_img, 0.4)
        self.exit_button = Button(200, 360, exit_img, 0.4)

    def draw_menu(self):
        self.resume_button.draw()
        self.exit_button.draw()

def main():
    pause_menu = PauseMenu()
    pause = False
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 36)
    lost_font = pygame.font.SysFont("comicsans", 36)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                if random.randrange(0, 10) == 1:  # Adjust the probability as needed
                    boss = Boss(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), "boss", health=300)
                    enemies.append(boss)
                else:
                    enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                                  random.choice(["red", "blue", "green"]))
                    enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause = not pause
                    pause_menu.draw_menu()

        if not pause:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] and player.x - player_vel > 0: # left
                player.x -= player_vel
            if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
                player.x += player_vel
            if keys[pygame.K_w] and player.y - player_vel > 0: # up
                player.y -= player_vel
            if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
                player.y += player_vel
            if keys[pygame.K_SPACE]:
                player.shoot()

            for enemy in enemies[:]:

                enemy.move_random(enemy_vel)
                enemy.move_lasers(laser_vel, player)

                if random.randrange(0, 2*60) == 1:
                    enemy.shoot()

                if collide(enemy, player):
                    player.health -= 10
                    enemies.remove(enemy)
                elif enemy.y + enemy.get_height() > HEIGHT:
                    lives -= 1
                    enemies.remove(enemy)

            player.move_lasers(-laser_vel, enemies)
    else:
        pygame.display.update()
        pause_menu.draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pause_menu.resume_button.clicker_action():
                    pause = not pause
                elif pause_menu.exit_button.clicker_action():
                    run = False
def main_two_players():
    pause_menu = PauseMenu()
    pause = False
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 36)
    lost_font = pygame.font.SysFont("comicsans", 36)

    enemies = []
    wave_length = 5
    enemy_vel = 1
    player_vel = 5
    laser_vel = 5
    player_p1 = Player(200, 630)  # Player 1 starting position
    player_p2 = Player(400, 630)  # Player 2 starting position

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0, 0))
        # draw text
        lives_label = main_font.render(f"Lives - Player 1: {lives} - Player 2: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player_p1.draw(WIN)
        player_p2.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player_p1.health <= 0 or player_p2.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                if random.randrange(0, 10) == 1:  # Adjust the probability as needed
                    boss = Boss(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), "boss", health=300)
                    enemies.append(boss)
                else:
                    enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                                  random.choice(["red", "blue", "green"]))
                    enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause = not pause
                    pause_menu.draw_menu()

        keys = pygame.key.get_pressed()

        if not pause:
        # Player 1 controls
            if keys[pygame.K_a] and player_p1.x - player_vel > 0:
                player_p1.x -= player_vel
            if keys[pygame.K_d] and player_p1.x + player_vel + player_p1.get_width() < WIDTH:
                player_p1.x += player_vel
            if keys[pygame.K_w] and player_p1.y - player_vel > 0:
                player_p1.y -= player_vel
            if keys[pygame.K_s] and player_p1.y + player_vel + player_p1.get_height() + 15 < HEIGHT:
                player_p1.y += player_vel
            if keys[pygame.K_SPACE]:
                player_p1.shoot()

            # Player 2 controls
            if keys[pygame.K_LEFT] and player_p2.x - player_vel > 0:
                player_p2.x -= player_vel
            if keys[pygame.K_RIGHT] and player_p2.x + player_vel + player_p2.get_width() < WIDTH:
                player_p2.x += player_vel
            if keys[pygame.K_UP] and player_p2.y - player_vel > 0:
                player_p2.y -= player_vel
            if keys[pygame.K_DOWN] and player_p2.y + player_vel + player_p2.get_height() + 15 < HEIGHT:
                player_p2.y += player_vel
            if keys[pygame.K_RETURN]:  # Use a different key for Player 2 shoot, e.g., ENTER
                player_p2.shoot()

            for enemy in enemies[:]:
                enemy.move_random(enemy_vel)
                enemy.move_lasers(laser_vel, player_p1)
                enemy.move_lasers(laser_vel, player_p2)

                if random.randrange(0, 2 * 60) == 1:
                    enemy.shoot()

                if collide(enemy, player_p1):
                    player_p1.health -= 10
                    enemies.remove(enemy)
                elif collide(enemy, player_p2):
                    player_p2.health -= 10
                    enemies.remove(enemy)
                elif enemy.y + enemy.get_height() > HEIGHT:
                    lives -= 1
                    enemies.remove(enemy)

            player_p1.move_lasers(-laser_vel, enemies)
            player_p2.move_lasers(-laser_vel, enemies)
        else:
            pygame.display.update()
            pause_menu.draw_menu()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pause_menu.resume_button.clicker_action():
                        pause = not pause
                    elif pause_menu.exit_button.clicker_action():
                        run = False

    pygame.quit()
def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    mode_font = pygame.font.SysFont("comicsans", 36)
    run = True
    selected_mode = None

    while run:
        WIN.blit(BG, (0, 0))
        x = Menu()
        x.init_menu()

        # button actions
        if x.p2.clicker_action():
            selected_mode = "two_player"
            main_two_players()
        if x.p1.clicker_action():
            selected_mode = "one_player"
            main()
        if x.exit.clicker_action():
            run = False
        title_label = title_font.render("Space Invaders", 1, (255,255,255))

        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 150))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_mode = "one_player"
                    main()
                elif event.key == pygame.K_2:
                    selected_mode = "two_player"
                    main_two_players()

    pygame.quit()
    return selected_mode


mode = main_menu()
