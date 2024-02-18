import pygame
import random
import math
import os

# initialize Pygame
pygame.init()

# screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# colors
BACKGROUND_COLOR = (0, 105, 148)  # Ocean blue

# backgound image
background_image = pygame.image.load("./bg.png").convert_alpha()
background_image = pygame.transform.scale(background_image, (800, 600))

# game settings
FPS = 60
ENEMY_SPAWN_RATE = 90  # number of frames between each new enemy spawn



class EnemyFish(pygame.sprite.Sprite):
    def __init__(self, point, speed, size):
        super().__init__()

        self.image_sizes = [(20, 10), (15, 30), (40, 40), (50, 35), (90, 60), (160, 80) ]

        self.image = pygame.image.load(f"./sprites/{str(point)}/image_1.png")
        self.image = pygame.transform.scale(self.image, self.image_sizes[point - 1])


        # self.image = pygame.Surface((size, size // 2))
        self.original_color = (255, 255, 255)  # original color
        self.eatable_color = (255, 0, 0)  # color for eatable fish
        # self.image.fill(self.original_color)
        self.rect = self.image.get_rect()
        if speed > 0:
            self.rect.x = -self.rect.width
        else:
            self.rect.x = SCREEN_WIDTH
        self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)
        self.point = point
        self.speed = speed

        self.frame_delay = 20  # Number of updates to wait before changing frames
        self.frame_delay_counter = 0  # Counter to keep track of updates
        self.frame_index = 0

        # self.frames = [pygame.image.load(f"./sprites/fish1/image_{str(i)}.png") for i in range(1, 7)]
        frame_count = [4, 4, 6, 6, 4, 4]
        self.frames = []
        for i in range(frame_count[point - 1]):
            img = pygame.image.load(f"./sprites/{str(point)}/image_{str(i)}.png")
            img = pygame.transform.scale(img, self.image_sizes[point - 1])
            self.frames.append(img)

    def update(self, player_level):
        self.rect.x += self.speed
        # if self.point <= player_level:
        #     self.image.fill(self.eatable_color)
        # else:
        #     self.image.fill(self.original_color)
        self.animate_movement()
        # remove the sprite when it leaves the screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

    def animate_movement(self):

        self.frame_delay_counter += 1

        if self.frame_delay_counter >= self.frame_delay:
            self.frame_delay_counter = 0

            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

            if self.speed > 0:
                self.image = pygame.transform.flip(self.image, True, False)


class PlayerFish(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # self.image = pygame.Surface((30, 15))  # initial size
        # self.image.fill((0, 255, 0))

        self.speed = 2
        self.point = 1
        self.level = 1
        self.points_to_next_level = 10
        self.lives = 3
        self.is_immune = False
        self.immune_time = 0
        self.flash_time = 0
        self.facing_left = True

        self.frame_delay = 10  # Number of updates to wait before changing frames
        self.frame_delay_counter = 0  # Counter to keep track of updates

        self.image = pygame.image.load("./sprites/player/player_1.png")
        self.image = pygame.transform.scale(self.image, (45, 30))
        # self.frames = [pygame.image.load(f"./sprites/fish/2/image_{str(i)}.png") for i in range(0, 6)]
        self.frames = []
        for i in range(6):
            img = pygame.image.load(f"./sprites/player/player_{str(i)}.png")
            img = pygame.transform.scale(img, (45, 30))
            self.frames.append(img)
        self.frame_index = 0
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    def update(self, keys_pressed, current_time):
        moving = False
        if keys_pressed[pygame.K_UP]:
            moving = True
            self.rect.y -= math.ceil(self.speed)
        if keys_pressed[pygame.K_DOWN]:
            moving = True
            self.rect.y += math.ceil(self.speed)
        if keys_pressed[pygame.K_LEFT]:
            moving = True
            self.facing_left = True
            self.rect.x -= math.ceil(self.speed)
        if keys_pressed[pygame.K_RIGHT]:
            moving = True
            self.facing_left = False
            self.rect.x += math.ceil(self.speed)

        if moving:
            self.animate_movement()
        # prevent player from leaving the screen

        allowable_area = screen.get_rect()
        allowable_area.height -= 40
        allowable_area.y += 40
        self.rect.clamp_ip(allowable_area)

        if self.point >= self.points_to_next_level:
            self.level += 1
            self.points_to_next_level += 10 * self.level  # adjust level

        base_width = 30
        base_height = 15
        old_center = self.rect.center if hasattr(self, 'rect') else (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        # self.image = pygame.Surface((base_width + (self.level - 1) * 15, base_height + (self.level - 1) * 7.5))
        # self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        self.speed = 2 - self.level * 0.1

        # update immunity and flashing
        if self.is_immune:
            if current_time - self.immune_time > 2000:
                self.is_immune = False
            else:
                self.flash_time += 1
                if self.flash_time % 10 in range(0, 5):
                    self.image.set_alpha(100 if self.image.get_alpha() == 255 else 150)
        else:
            self.image.set_alpha(255)

    def animate_movement(self):

        self.frame_delay_counter += 1

        if self.frame_delay_counter >= self.frame_delay:
            self.frame_delay_counter = 0

            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

            if self.facing_left:
                self.image = pygame.transform.flip(self.image, True, False)

        # self.frame_index = (self.frame_index + 1) % len(self.frames)

def spawn_enemy_fish(enemies, player):
    points = [1, 2, 3, 4, 5, 6]
    points.extend([player.level] * len(points))

    point = random.choice(points)  # random point value

    # make speed inversely proportional to point
    speed = random.choice([-1, 1]) * math.ceil(2 / point)

    # make size proportional to point
    size = point * 10
    enemy_fish = EnemyFish(point, speed, size)
    enemies.add(enemy_fish)


def check_collisions(player, enemies, current_time):
    for enemy in enemies:
        if pygame.sprite.collide_rect(player, enemy):
            if player.level >= enemy.point:
                player.point += enemy.point
                enemy.kill()
            elif not player.is_immune:
                player.lives -= 1
                player.is_immune = True
                player.immune_time = current_time
                player.flash_time = 0
                if player.lives <= 0:
                    print("Game Over")
                    
                    # add some game over action


def draw_status_bar(player_points, player_level, progress, next_level_points, lives):

    # status Bar Background
    pygame.draw.rect(screen, (0, 77, 64), (0, 0, SCREEN_WIDTH, 40))

    # display Current Points
    font = pygame.font.SysFont(None, 30)
    points_text = font.render(f'Points: {player_points - 1}', True, (255, 255, 255))
    screen.blit(points_text, (10, 10))

    # display Current Level
    level_text = font.render(f'Level: {player_level}', True, (255, 255, 255))
    screen.blit(level_text, (SCREEN_WIDTH - 150, 10))

    # progress Bar Background
    pygame.draw.rect(screen, (255, 255, 255), (380, 10, 200, 20), 1)  # White border

    # progress Bar Fill
    fill_width = (progress / next_level_points) * 200
    pygame.draw.rect(screen, (255, 165, 0), (380, 10, fill_width, 20))

    # Display Lives as Red Circles
    for i in range(lives):
        pygame.draw.circle(screen, (255, 0, 0), (180 + i * 30, 20), 10)


def main():
    clock = pygame.time.Clock()
    running = True
    enemy_fish = pygame.sprite.Group()
    player = PlayerFish()
    player_group = pygame.sprite.GroupSingle(player)
    spawn_timer = ENEMY_SPAWN_RATE

    while running:
        # draw background image
        screen.blit(background_image, (0, 0))


        current_time = pygame.time.get_ticks()
        keys_pressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # spawn new enemy fish periodically
        spawn_timer -= 1
        if spawn_timer <= 0:
            spawn_enemy_fish(enemy_fish, player)
            spawn_timer = ENEMY_SPAWN_RATE

        # update enemy fish colors based on the player's size
        enemy_fish.update(player.level)
        player_group.update(keys_pressed, current_time)

        check_collisions(player, enemy_fish, current_time)

        # screen.fill(BACKGROUND_COLOR)
        enemy_fish.draw(screen)
        player_group.draw(screen)

        # draw status and progress bars
        draw_status_bar(player.point, player.level, player.point, player.points_to_next_level, player.lives)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
