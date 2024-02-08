import pygame
import random
import math

# initialize Pygame
pygame.init()

# screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# colors
BACKGROUND_COLOR = (0, 105, 148)  # Ocean blue

# game settings
FPS = 60
ENEMY_SPAWN_RATE = 90  # number of frames between each new enemy spawn


class EnemyFish(pygame.sprite.Sprite):
    def __init__(self, point, speed, size):
        super().__init__()
        self.image = pygame.Surface((size, size // 2))
        self.original_color = (255, 255, 255)  # original color
        self.eatable_color = (255, 0, 0)  # color for eatable fish
        self.image.fill(self.original_color)
        self.rect = self.image.get_rect()
        if speed > 0:
            self.rect.x = -self.rect.width
        else:
            self.rect.x = SCREEN_WIDTH
        self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)
        self.point = point
        self.speed = speed

    def update(self, player_level):
        self.rect.x += self.speed
        if self.point <= player_level:
            self.image.fill(self.eatable_color)
        else:
            self.image.fill(self.original_color)
        # remove the sprite when it leaves the screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()


class PlayerFish(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 15))  # initial size
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.speed = 2
        self.point = 1
        self.level = 1
        self.points_to_next_level = 10

    def update(self, keys_pressed):
        if keys_pressed[pygame.K_UP]:
            self.rect.y -= math.ceil(self.speed)
        if keys_pressed[pygame.K_DOWN]:
            self.rect.y += math.ceil(self.speed)
        if keys_pressed[pygame.K_LEFT]:
            self.rect.x -= math.ceil(self.speed)
        if keys_pressed[pygame.K_RIGHT]:
            self.rect.x += math.ceil(self.speed)

        # prevent player from leaving the screen
        self.rect.clamp_ip(screen.get_rect())

        if self.point >= self.points_to_next_level:
            self.level += 1
            self.points_to_next_level += 10 * self.level  # adjust level

        base_width = 30
        base_height = 15
        self.image = pygame.Surface((base_width + (self.level - 1) * 15, base_height + (self.level - 1) * 7.5))
        self.image.fill((0, 255, 0))
        self.speed = 2 + self.level * 0.2


def spawn_enemy_fish(enemies):
    point = random.randint(1, 10)  # random point value

    # make speed inversely proportional to point
    speed = random.choice([-1, 1]) * math.ceil(2 / point)

    # make size proportional to point
    size = point * 10
    enemy_fish = EnemyFish(point, speed, size)
    enemies.add(enemy_fish)


def check_collisions(player, enemies):
    for enemy in enemies:
        if pygame.sprite.collide_rect(player, enemy) and player.level >= enemy.point:
            player.point += enemy.point
            enemy.kill()


def draw_status_bar(player_points, player_level, progress, next_level_points):

    # status Bar Background
    pygame.draw.rect(screen, (0, 77, 64), (0, 0, SCREEN_WIDTH, 40))

    # display Current Points
    font = pygame.font.SysFont(None, 30)
    points_text = font.render(f'Points: {player_points}', True, (255, 255, 255))
    screen.blit(points_text, (10, 10))

    # display Current Level
    level_text = font.render(f'Level: {player_level}', True, (255, 255, 255))
    screen.blit(level_text, (SCREEN_WIDTH - 150, 10))

    # progress Bar Background
    pygame.draw.rect(screen, (255, 255, 255), (200, 10, 200, 20), 1)  # White border

    # progress Bar Fill
    fill_width = (progress / next_level_points) * 200
    pygame.draw.rect(screen, (255, 165, 0), (200, 10, fill_width, 20))


def main():
    clock = pygame.time.Clock()
    running = True
    enemy_fish = pygame.sprite.Group()
    player = PlayerFish()
    player_group = pygame.sprite.GroupSingle(player)
    spawn_timer = ENEMY_SPAWN_RATE

    while running:
        keys_pressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # spawn new enemy fish periodically
        spawn_timer -= 1
        if spawn_timer <= 0:
            spawn_enemy_fish(enemy_fish)
            spawn_timer = ENEMY_SPAWN_RATE

        # update enemy fish colors based on the player's size
        enemy_fish.update(player.level)
        player_group.update(keys_pressed)

        check_collisions(player, enemy_fish)

        screen.fill(BACKGROUND_COLOR)
        enemy_fish.draw(screen)
        player_group.draw(screen)

        # draw status and progress bars
        draw_status_bar(player.point, player.level, player.point, player.points_to_next_level)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
