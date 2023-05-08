import os
import random
import time
import pygame

# Tamanho do grid
WIDTH = 30
HEIGHT = 20
GRID_SIZE = 20

# Cores
WHITE, BLACK, RED, GREEN, BLUE, YELLOW = [(255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]

# Objetos do jogo
HEAD, BODY, FRUIT, WALL = [1, 2, 3, 4]

# Direções
UP, DOWN, LEFT, RIGHT = [(0, -1), (0, 1), (-1, 0), (1, 0)]

def create_grid():
    """Cria um grid vazio"""
    return [[None] * WIDTH for _ in range(HEIGHT)]

def place_object(grid, obj, pos):
    """Coloca um objeto no grid"""
    x, y = pos
    grid[y][x] = obj

def get_random_position(grid):
    """Retorna uma posição aleatória vazia no grid"""
    while True:
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)
        if grid[y][x] is None:
            return (x, y)

def place_objects(grid, count, obj_type):
    """Coloca objetos aleatórios no grid"""
    for _ in range(count):
        pos = get_random_position(grid)
        place_object(grid, obj_type, pos)

def create_snake():
    """Cria uma cobra com um tamanho inicial"""
    x = random.randint(3, WIDTH - 4)
    y = random.randint(3, HEIGHT - 4)
    return [(x, y), (x - 1, y), (x - 2, y)]

def move_snake(snake, direction):
    """Move a cobra em uma direção"""
    head = snake[0]
    x, y = head
    if isinstance(direction, tuple):
        dx, dy = direction
        x += dx
        y += dy
    snake.insert(0, (x, y))
    snake.pop()

def draw_head(screen, x, y, direction, color):
    rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(screen, color, rect)
    eye_color = WHITE
    eye_size = GRID_SIZE // 4
    offset = GRID_SIZE // 4

    if direction == UP:
        pygame.draw.circle(screen, eye_color, (x * GRID_SIZE + offset, y * GRID_SIZE + offset), eye_size)
        pygame.draw.circle(screen, eye_color, (x * GRID_SIZE + GRID_SIZE - offset, y * GRID_SIZE + offset), eye_size)
    elif direction == DOWN:
        pygame.draw.circle(screen, eye_color, (x * GRID_SIZE + offset, y * GRID_SIZE + GRID_SIZE - offset), eye_size)
        pygame.draw.circle(screen, eye_color, (x * GRID_SIZE + GRID_SIZE - offset, y * GRID_SIZE + GRID_SIZE - offset), eye_size)
    elif direction == LEFT:
        pygame.draw.circle(screen, eye_color, (x * GRID_SIZE + offset, y * GRID_SIZE + offset), eye_size)
        pygame.draw.circle(screen, eye_color, (x * GRID_SIZE + offset, y * GRID_SIZE + GRID_SIZE - offset), eye_size)
    elif direction == RIGHT:
        pygame.draw.circle(screen, eye_color, (x * GRID_SIZE + GRID_SIZE - offset, y * GRID_SIZE + offset), eye_size)
        pygame.draw.circle(screen, eye_color, (x * GRID_SIZE + GRID_SIZE - offset, y * GRID_SIZE + GRID_SIZE - offset), eye_size)
        
def draw_fruit(screen, x, y, color):
    pygame.draw.circle(screen, color, (x * GRID_SIZE + GRID_SIZE // 2, y * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 2)

def draw_wall(screen, x, y):
    rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(screen, WHITE, rect) 

def draw_body(screen, x, y, color):
    rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(screen, color, rect)    

def draw_grid(screen, grid, snake, snake_color, snake_direction):
    """Desenha o grid e a cobra na tela"""
    screen.fill(BLACK)
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell == FRUIT:
                draw_fruit(screen, x, y, snake_color)
            elif cell == WALL:
                draw_wall(screen, x, y)

    for i, (x, y) in enumerate(snake):
        if i == 0:
            draw_head(screen, x, y, snake_direction, snake_color)
        else:
            draw_body(screen, x, y, snake_color)

def get_input_direction(current_direction, buffer, paused):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            key_directions = {pygame.K_w: UP, pygame.K_s: DOWN, pygame.K_a: LEFT, pygame.K_d: RIGHT,
                              pygame.K_UP: UP, pygame.K_DOWN: DOWN, pygame.K_LEFT: LEFT, pygame.K_RIGHT: RIGHT}
            if event.key in key_directions and not paused and isinstance(current_direction, tuple) and key_directions[event.key] != (-current_direction[0], -current_direction[1]):
                buffer.append(key_directions[event.key])
            if event.key == pygame.K_p:
                if paused:
                    paused = False
                else:
                    paused = True

    return buffer.pop(0) if buffer else current_direction, paused
    
def countdown(screen, font, seconds):
    for i in range(seconds, 0, -1):
        text = font.render(str(i), True, WHITE)
        screen.blit(text, (WIDTH * GRID_SIZE // 2 - text.get_width() // 2, HEIGHT * GRID_SIZE // 2 - text.get_height() // 2))
        pygame.display.flip()
        time.sleep(1)

def create_level(level_number):
    base_speed = 0.5
    speed_decrease_per_level = 0.03
    fruits_per_level = 5
    walls_per_level = 5

    return {
        "speed": max(base_speed - speed_decrease_per_level * (level_number - 1), 0.1),
        "fruit_count": fruits_per_level * level_number,
        "wall_count": walls_per_level * level_number,
        "snake_color": (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
    }

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH * GRID_SIZE, HEIGHT * GRID_SIZE))
    font = pygame.font.Font(None, 36)

    level_number = 1
    max_level = 10

    while level_number <= max_level:
        pygame.display.set_caption(f"Snake Game - Level {level_number}")
        current_level = create_level(level_number)
        grid = create_grid()
        place_objects(grid, current_level["fruit_count"], FRUIT)
        place_objects(grid, current_level["wall_count"], WALL)
        snake = create_snake()
        snake_direction = RIGHT
        direction_buffer = []
        fruits_eaten = 0
        paused = False

        while True:
            snake_direction, paused = get_input_direction(snake_direction, direction_buffer, paused)

            if paused:
                time.sleep(0.1)
                continue

            move_snake(snake, snake_direction)
            head = snake[0]
            x, y = head

            if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
                break

            if grid[y][x] == WALL or head in snake[1:]:
                break

            if grid[y][x] == FRUIT:
                grid[y][x] = None
                fruits_eaten += 1
                snake.append(snake[-1])

                if fruits_eaten == current_level["fruit_count"]:
                    level_number += 1
                    break

            draw_grid(screen, grid, snake, current_level["snake_color"], snake_direction)
            pygame.display.flip()
            time.sleep(current_level["speed"])

    pygame.quit()

if __name__ == "__main__":
    main()

pygame.quit()