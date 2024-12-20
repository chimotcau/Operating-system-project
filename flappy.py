import pygame, random, time
from pygame.locals import *

# Default constants
DEFAULT_SCREEN_WIDTH = 400
DEFAULT_SCREEN_HEIGHT = 600
SCREEN_WIDTH = DEFAULT_SCREEN_WIDTH
SCREEN_HEIGHT = DEFAULT_SCREEN_HEIGHT
SPEED = 10  # Adjusted for smoother jumps
GRAVITY = 1  # Reduced for slower falling
GAME_SPEED = 10
GROUND_HEIGHT = 100
PIPE_WIDTH = 80
PIPE_HEIGHT = 500
PIPE_GAP = 150
wing = 'assets/audio/wing.wav'
hit = 'assets/audio/hit.wav'

pygame.mixer.init()

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (255, 255, 255)
        self.text = text
        self.font = pygame.font.Font(None, 32)
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == KEYDOWN:
            if self.active:
                if event.key == K_RETURN:
                    return self.text
                elif event.key == K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, self.color)
        return None

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = [pygame.image.load('assets/sprites/redbird-upflap.png').convert_alpha(),
                       pygame.image.load('assets/sprites/redbird-midflap.png').convert_alpha(),
                       pygame.image.load('assets/sprites/redbird-downflap.png').convert_alpha()]
        self.speed = 0  # Start with no initial movement
        self.current_image = 0
        self.image = self.images[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDTH / 6
        self.rect[1] = SCREEN_HEIGHT / 2

    def update(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.speed += GRAVITY
        self.rect[1] += self.speed

    def bump(self):
        self.speed = -SPEED

class Pipe(pygame.sprite.Sprite):
    def __init__(self, inverted, xpos, ysize):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/pipe-red.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDTH, PIPE_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = - (self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect[0] -= GAME_SPEED

class Ground(pygame.sprite.Sprite):
    def __init__(self, xpos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/Universe-Astronomy-Art-Concept.jpg').convert_alpha()
        self.image = pygame.transform.scale(self.image, (2 * SCREEN_WIDTH, GROUND_HEIGHT))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT

    def update(self):
        self.rect[0] -= GAME_SPEED

def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2])

def get_random_pipes(xpos):
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return pipe, pipe_inverted

pygame.init()

# Create a temporary default screen for the input process
temp_screen = pygame.display.set_mode((DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird - Set Screen Size')

def input_screen():
    global SCREEN_WIDTH, SCREEN_HEIGHT
    clock = pygame.time.Clock()
    input_width = InputBox(100, 200, 200, 32, text=str(DEFAULT_SCREEN_WIDTH))
    input_height = InputBox(100, 250, 200, 32, text=str(DEFAULT_SCREEN_HEIGHT))  # Adjusted vertical position
    input_boxes = [input_width, input_height]
    font = pygame.font.Font(None, 36)
    while True:
        temp_screen.fill((0, 0, 0))
        title = font.render('       Width and Height', True, (255, 255, 255))
        temp_screen.blit(title, (40, 50))  # Moved title to top-left
        for box in input_boxes:
            box.draw(temp_screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            for box in input_boxes:
                result = box.handle_event(event)
                if result is not None:
                    try:
                        new_width = int(input_width.text)
                        new_height = int(input_height.text)
                        if new_width < 300 or new_height < 400:  # Validate minimum size
                            raise ValueError("Dimensions too small!")
                        SCREEN_WIDTH = new_width
                        SCREEN_HEIGHT = new_height
                        return
                    except ValueError:
                        print("Invalid dimensions entered!")
        clock.tick(30)

def start_screen():
    font = pygame.font.Font(None, 48)
    clock = pygame.time.Clock()
    while True:
        screen.fill((0, 0, 0))
        message = font.render("Press SPACE to Start", True, (255, 255, 255))
        screen.blit(message, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 24))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN and event.key == K_SPACE:
                return
        clock.tick(30)

# Call input screen
input_screen()

# Update screen and dependent variables
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')
GROUND_WIDTH = 2 * SCREEN_WIDTH

# Reload and scale the background
BACKGROUND = pygame.image.load('assets/sprites/milky-way-984050_1920.jpg')
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Show start screen
start_screen()

# Initialize sprite groups
bird_group = pygame.sprite.Group()
bird = Bird()
bird_group.add(bird)

ground_group = pygame.sprite.Group()
for i in range(2):
    ground = Ground(GROUND_WIDTH * i)
    ground_group.add(ground)

pipe_group = pygame.sprite.Group()
for i in range(2):
    pipes = get_random_pipes(SCREEN_WIDTH * i + 800)
    pipe_group.add(pipes[0])
    pipe_group.add(pipes[1])

clock = pygame.time.Clock()
running = True

while running:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_SPACE or event.key == K_UP:
                bird.bump()
                pygame.mixer.music.load(wing)
                pygame.mixer.music.play()
    screen.blit(BACKGROUND, (0, 0))

    if is_off_screen(ground_group.sprites()[0]):
        ground_group.remove(ground_group.sprites()[0])
        new_ground = Ground(GROUND_WIDTH - 20)
        ground_group.add(new_ground)

    if is_off_screen(pipe_group.sprites()[0]):
        pipe_group.remove(pipe_group.sprites()[0])
        pipe_group.remove(pipe_group.sprites()[0])
        pipes = get_random_pipes(SCREEN_WIDTH * 2)
        pipe_group.add(pipes[0])
        pipe_group.add(pipes[1])

    bird_group.update()
    ground_group.update()
    pipe_group.update()
    bird_group.draw(screen)
    pipe_group.draw(screen)
    ground_group.draw(screen)
    pygame.display.update()

    if (pygame.sprite.groupcollide(bird_group, ground_group, False, False, pygame.sprite.collide_mask) or
            pygame.sprite.groupcollide(bird_group, pipe_group, False, False, pygame.sprite.collide_mask)):
        pygame.mixer.music.load(hit)
        pygame.mixer.music.play()
        time.sleep(1)
        running = False

pygame.quit()
