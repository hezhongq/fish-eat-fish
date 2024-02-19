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
popup_color = (0, 0, 0, 128)
PLAYER_SIZE = [(45, 30), (54, 36), (60, 40), (66, 44), (90, 60), (120, 90)]
ENEMY_SPAWN_RATE = 90  # number of frames between each new enemy spawn
ENEMY_FISH_SIZE = [(20, 10), (15, 30), (40, 40), (50, 35), (90, 60), (120, 60) ]
ENEMY_FISH_SPEED = []

# initialize game states
STATE_INSTRUCTIONS = "instructions"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"

def show_game_over_screen(text):
    font = pygame.font.SysFont(None, 36)
    if text == "lose":
        game_over_text = font.render('Game Over', True, (255, 255, 255))
    else:
        game_over_text = font.render('You Won!', True, (255, 255, 255))
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
    
    popup_surface = pygame.Surface((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3), pygame.SRCALPHA)
    popup_surface.fill((0, 0, 0, 128))  # Semi-transparent black
    popup_position = ((SCREEN_WIDTH - popup_surface.get_width()) // 2, (SCREEN_HEIGHT - popup_surface.get_height()) // 2)

    screen.blit(background_image, (0, 0))
    screen.blit(popup_surface, popup_position)
    screen.blit(game_over_text, game_over_rect)
    pygame.display.flip()

class EnemyFish(pygame.sprite.Sprite):
    def __init__(self, point, speed, size):
        super().__init__()

        self.image = pygame.image.load(f"./sprites/{str(point)}/image_1.png")
        self.image = pygame.transform.scale(self.image, ENEMY_FISH_SIZE[point - 1])

        self.rect = self.image.get_rect()
        if speed > 0:
            self.rect.x = -self.rect.width
        else:
            self.rect.x = SCREEN_WIDTH
        self.rect.y = random.randint(80, SCREEN_HEIGHT - 80)

        self.point = point
        self.speed = speed

        self.frame_delay = 20  # Number of updates to wait before changing frames
        self.frame_delay_counter = 0  # Counter to keep track of updates
        self.frame_index = 0

        # number of frames that each fish has
        frame_count = [4, 4, 6, 6, 4, 4]
        self.frames = []
        for i in range(frame_count[point - 1]):
            img = pygame.image.load(f"./sprites/{str(point)}/image_{str(i)}.png")
            img = pygame.transform.scale(img, ENEMY_FISH_SIZE[point - 1])
            self.frames.append(img)

    def update(self):
        self.rect.x += self.speed
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
        self.image = pygame.transform.scale(self.image, PLAYER_SIZE[self.level - 1])

        self.frames = []
        for i in range(6):
            img = pygame.image.load(f"./sprites/player/player_{str(i)}.png")
            img = pygame.transform.scale(img, PLAYER_SIZE[self.level - 1])
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
            if self.level >= 6:
                show_game_over_screen("win")
            new_frames = []
            for i in range(6):
                img = pygame.image.load(f"./sprites/player/player_{str(i)}.png")
                img = pygame.transform.scale(img, PLAYER_SIZE[self.level - 1])
                new_frames.append(img)
                self.frames = new_frames

        old_center = self.rect.center if hasattr(self, 'rect') else (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
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


def spawn_enemy_fish(enemies, player):
    points = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 5, 6]
    points.extend([player.level] * 4)

    point = random.choice(points)  # random point value

    # make speed inversely proportional to point
    speed = random.choice([-1, 1]) * 1

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
                    
                    # add some game over action


def draw_status_bar(player_points, player_level, progress, next_level_points, lives, heart_image):

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

    # Display Lives as Hearts
    for i in range(lives):
        heart_position = (180 + i * 30, 10)  # Adjust positioning as needed
        screen.blit(heart_image, heart_position)

def show_instruction_screen(clock):
    running = True
    font = pygame.font.SysFont(None, 36)
    instructions = font.render('Press any arrow key to start', True, (255, 255, 255))
    instructions_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    
    rules_text = "Game Rules: Eat smaller fish to grow. Avoid larger fish."
    rules = font.render(rules_text, True, (255, 255, 255))
    rules_rect = rules.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))

    popup_surface = pygame.Surface((SCREEN_WIDTH // 7 * 6, SCREEN_HEIGHT // 4 * 3), pygame.SRCALPHA)
    popup_color = (0, 0, 0, 128)  # Semi-transparent black
    popup_surface.fill(popup_color)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                    running = False
        
        screen.blit(background_image, (0, 0))
        screen.blit(popup_surface, (SCREEN_WIDTH // 16, SCREEN_HEIGHT // 16))
        screen.blit(rules, rules_rect)
        screen.blit(instructions, instructions_rect)
        pygame.display.flip()
        clock.tick(FPS)

def reset_game():
    global player, enemy_fish, player_group
    enemy_fish = pygame.sprite.Group()
    player = PlayerFish()
    player_group = pygame.sprite.GroupSingle(player)


def main():
    clock = pygame.time.Clock()
    running = True
    enemy_fish = pygame.sprite.Group()
    player = PlayerFish()
    player_group = pygame.sprite.GroupSingle(player)
    spawn_timer = ENEMY_SPAWN_RATE

    game_state = STATE_INSTRUCTIONS
    show_instruction_screen(clock)
    reset_game()
    heart_image = pygame.image.load('heart.png').convert_alpha()
    heart_image = pygame.transform.scale(heart_image, (25, 25)) 

    while running:
        # draw background image
        screen.blit(background_image, (0, 0))
        current_time = pygame.time.get_ticks()

        keys_pressed = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if game_state == STATE_INSTRUCTIONS:
            show_instruction_screen(clock)
            game_state = STATE_PLAYING
            reset_game() 

        elif game_state == STATE_GAME_OVER:
            show_game_over_screen("lose")  
            game_state = STATE_INSTRUCTIONS 
        
        elif game_state == STATE_PLAYING:
            # spawn new enemy fish periodically
            spawn_timer -= 1
            if spawn_timer <= 0:
                spawn_enemy_fish(enemy_fish, player)
                spawn_timer = ENEMY_SPAWN_RATE

            # update enemy fish colors based on the player's size
            enemy_fish.update()
            player_group.update(keys_pressed, current_time)

            check_collisions(player, enemy_fish, current_time)

            if player.lives <= 0:
                show_game_over_screen("lose")
                reset_game()
                continue

            # screen.fill(BACKGROUND_COLOR)
            enemy_fish.draw(screen)
            player_group.draw(screen)

            # draw circle around eatable enemy
            for enemy in enemy_fish:
                if enemy.point <= player.level:
                    pygame.draw.circle(screen, (0, 255, 0), enemy.rect.center, max(enemy.rect.width, enemy.rect.height) // 2 + 5, 2)

            # draw status and progress bars
            draw_status_bar(player.point, player.level, player.point, player.points_to_next_level, player.lives, heart_image)

            if player.lives <= 0:
                game_state = STATE_GAME_OVER

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
