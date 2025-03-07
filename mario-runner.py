import pygame
from sys import exit
from random import randint, choice

# Function to read the high score from a file
def read_high_score():
    try:
        with open('high_score.txt', 'r') as file:
            return int(file.read())
    except FileNotFoundError:
        return 0

# Function to save the high score to a file
def save_high_score(score):
    with open('high_score.txt', 'w') as file:
        file.write(str(score))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        player_walk_1 = pygame.image.load('mario.png').convert_alpha()
        player_walk_1 = pygame.transform.scale(player_walk_1, (80, 80))
        player_walk_2 = pygame.image.load('mario.png').convert_alpha()
        player_walk_2 = pygame.transform.scale(player_walk_1, (80, 80))
        self.player_walk = [player_walk_1, player_walk_2]
        self.player_index = 0
        self.player_jump = pygame.image.load('mari_jump.png').convert_alpha()
        self.player_jump = pygame.transform.scale(self.player_jump, (60, 60))
        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=(80, 310))
        self.gravity = 0

        self.jump_sound = pygame.mixer.Sound('jump.mp3')
        self.jump_sound.set_volume(0.5)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 310:
            self.gravity = -20
            self.jump_sound.play()

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 310:
            self.rect.bottom = 310

    def animation_state(self):
        if self.rect.bottom < 310:
            self.image = self.player_jump
        else:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk):
                self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation_state()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type, speed):
        super().__init__()

        if type == 'fly':
            fly_1 = pygame.image.load('fly1.png').convert_alpha()
            fly_2 = pygame.image.load('fly2.png').convert_alpha()
            self.frames = [fly_1, fly_2]
            self.y_pos = 210
            self.animation_index = 0
        else:
            ghost = pygame.image.load('ghost.png').convert_alpha()
            ghost = pygame.transform.scale(ghost, (60, 60))
            self.frames = [ghost]
            self.y_pos = 300

        self.image = self.frames[0]
        self.rect = self.image.get_rect(midbottom=(randint(900, 1100), self.y_pos))
        self.type = type  # Store the type of the obstacle
        self.speed = speed

    def animation_state(self):
        if self.type == 'fly':
            self.animation_index += 0.1
            if self.animation_index >= len(self.frames):
                self.animation_index = 0
            self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animation_state()
        self.rect.x -= self.speed
        self.destroy()

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()

    def is_under_player(self, player):
        return player.rect.bottom < self.rect.centery and player.rect.top < self.rect.centery

class GameManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 400))
        pygame.display.set_caption('Saad Ahmed')
        self.clock = pygame.time.Clock()
        self.test_font = pygame.font.Font(None, 35)
        self.game_active = False
        self.start_time = 0
        self.score = 0
        self.high_score = read_high_score()
        self.lives = 3
        self.bg_music = pygame.mixer.Sound('move.mp3')
        self.bg_music.play(loops=-1)

        self.player = pygame.sprite.GroupSingle()
        self.player.add(Player())

        self.obstacle_group = pygame.sprite.Group()

        self.sky_surface = pygame.image.load('sky5.png').convert_alpha()
        self.sky_surface = pygame.transform.scale(self.sky_surface, (800, 510))

        self.player_stand = pygame.image.load('mario.png').convert_alpha()
        self.player_stand = pygame.transform.scale(self.player_stand, (100, 100))
        self.player_stand = pygame.transform.rotozoom(self.player_stand, 0, 2)
        self.player_stand_rect = self.player_stand.get_rect(center=(400, 200))

        self.game_name = self.test_font.render('Jump Star', False, (111, 196, 169))
        self.game_name_rect = self.game_name.get_rect(center=(400, 20))

        self.game_message = self.test_font.render('Press space to run', False, (111, 196, 169))
        self.game_message_rect = self.game_message.get_rect(center=(400, 350))

        self.ghost = pygame.image.load('ghost.png').convert_alpha()
        self.ghost = pygame.transform.scale(self.ghost, (50, 50))
        self.fly = pygame.image.load('fly1.png').convert_alpha()
        self.fly = pygame.transform.scale(self.fly, (60, 30))

        self.obstacle_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.obstacle_timer, 1500)

        self.speed_increase_timer = 0
        self.obstacle_speed = 6

    def display_score(self):
        current_time = int(pygame.time.get_ticks() / 1000) - self.start_time
        score_surf = self.test_font.render(f'Score: {self.score}', False, (64, 64, 64))
        score_rect = score_surf.get_rect(topleft=(10, 10))
        self.screen.blit(score_surf, score_rect)
        return current_time

    def display_lives(self):
        lives_surf = self.test_font.render(f'Lives: {self.lives}', False, (255, 0, 0))
        lives_rect = lives_surf.get_rect(topright=(790, 10))
        self.screen.blit(lives_surf, lives_rect)

    def collision_sprite(self):
        collided = pygame.sprite.spritecollide(self.player.sprite, self.obstacle_group, False)
        for obstacle in collided:
            if obstacle.is_under_player(self.player.sprite):
                if obstacle.type == 'fly':
                    self.score += 10
                else:
                    self.score += 5
                obstacle.kill()
            else:
                self.obstacle_group.empty()
                return False
        return True

    def increase_speed(self):
        if pygame.time.get_ticks() - self.speed_increase_timer > 30000:
            self.speed_increase_timer = pygame.time.get_ticks()
            self.obstacle_speed += 1

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if self.game_active:
                    if event.type == self.obstacle_timer:
                        self.obstacle_group.add(Obstacle(choice(['fly', 'ghost', 'ghost', 'fly', 'ghost', 'fly', 'ghost', 'ghost']), self.obstacle_speed))

                else:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        if self.lives == 0:
                            self.lives = 3
                            self.score = 0
                            self.high_score = read_high_score()
                        self.game_active = True
                        self.start_time = int(pygame.time.get_ticks() / 1000)

            if self.game_active:
                self.screen.blit(self.sky_surface, (0, -110))
                self.display_score()
                self.display_lives()
                self.increase_speed()

                self.player.draw(self.screen)
                self.player.update()

                self.obstacle_group.draw(self.screen)
                self.obstacle_group.update()

                if not self.collision_sprite():
                    self.lives -= 1
                    self.game_active = self.lives > 0

                if not self.game_active and self.score > self.high_score:
                    self.high_score = self.score
                    save_high_score(self.high_score)

            else:
                self.screen.fill((10, 10, 40))
                self.screen.blit(self.player_stand, self.player_stand_rect)

                score_message = self.test_font.render(f'Your score: {self.score}', False, (111, 196, 169))
                score_message_rect = score_message.get_rect(center=(400, 350))
                self.screen.blit(self.game_name, self.game_name_rect)

                if self.score == 0:
                    self.screen.blit(self.game_message, self.game_message_rect)
                else:
                    self.screen.blit(score_message, score_message_rect)

                high_score_message = self.test_font.render(f'High Score: {self.high_score}', False, (111, 196, 169))
                high_score_message_rect = high_score_message.get_rect(center=(400, 320))

                rules_message = self.test_font.render("Jump on the top of obstacles to get points", False, (111, 196, 169))
                rules_rect = rules_message.get_rect(center=(400, 60))

                ghost_points_message = self.test_font.render("= 5", False, (111, 196, 169))
                ghost_points_rect = ghost_points_message.get_rect(midleft=(80, 315))

                fly_points_message = self.test_font.render("= 10", False, (111, 196, 169))
                fly_points_rect = fly_points_message.get_rect(midleft=(80, 355))

                self.screen.blit(high_score_message, high_score_message_rect)
                self.screen.blit(rules_message, rules_rect)

                # Display snail image with the points text
                ghost_image_rect = self.ghost.get_rect(midright=(70, 315))
                self.screen.blit(self.ghost, ghost_image_rect)
                self.screen.blit(ghost_points_message, ghost_points_rect)

                # Display fly image with the points text
                fly_image_rect = self.fly.get_rect(midright=(70, 355))
                self.screen.blit(self.fly, fly_image_rect)
                self.screen.blit(fly_points_message, fly_points_rect)

            pygame.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    game_manager = GameManager()
    game_manager.run()

#Muhammad Ahmed Sheikh 271058474
#Saad Zahid Khan 271057507
