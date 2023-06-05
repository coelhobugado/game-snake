import random
import time
import pygame
import sys

class Config:
    """A class used to store all configuration constants"""
    WIDTH = 900
    HEIGHT = 600
    GRID_SIZE = 30
    FPS = 10
    INITIAL_SPEED = 5
    MAX_LEVEL = 15
    POINTS_PER_LEVEL = 10

    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (231, 76, 60)
    GREEN = (46, 204, 113)
    BLUE = (52, 152, 219)
    YELLOW = (241, 196, 15)
    SNAKE_HEAD_COLOR = (46, 204, 113)
    SNAKE_BODY_COLOR = (39, 174, 96)
    FRUIT_COLORS = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (255, 0, 255),
        (0, 255, 255),
        (255, 165, 0),
        (128, 0, 128),
        (128, 128, 0),
        (0, 128, 128),
        (128, 128, 128),
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
    ]
    WALL_COLOR = (200, 200, 200)

    # Game objects
    HEAD = 1
    BODY = 2
    FRUIT = 3
    WALL = 4

    # Directions
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class GameObject:
    """A base class for all objects in the game"""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def draw(self, screen):
        pass


class Fruit(GameObject):
    """A class used to represent a Fruit"""

    def draw(self, screen):
        radius = Config.GRID_SIZE // 2
        center_x = self.x * Config.GRID_SIZE + radius
        center_y = self.y * Config.GRID_SIZE + radius
        pygame.draw.circle(screen, self.color, (center_x, center_y), radius)


class Wall(GameObject):
    """A class used to represent a Wall"""

    def draw(self, screen):
        rect = pygame.Rect(
            self.x * Config.GRID_SIZE,
            self.y * Config.GRID_SIZE,
            Config.GRID_SIZE,
            Config.GRID_SIZE,
        )
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, Config.BLACK, rect, 1)


class Snake:
    """A class used to represent the Snake"""

    def __init__(self, x, y, size):
        self.body = [(x, y)]
        self.direction = Config.RIGHT
        self.grow_counter = size - 1
        self.speed = Config.INITIAL_SPEED
        self.head_color = Config.SNAKE_HEAD_COLOR
        self.body_color = Config.SNAKE_BODY_COLOR

    def move(self):
        """Move the snake in the current direction"""
        head = self.body[0]
        dx, dy = self.direction
        x, y = head
        x += dx
        y += dy
        new_head = (x, y)
        self.body.insert(0, new_head)
        if self.grow_counter > 0:
            self.grow_counter -= 1
        else:
            self.body.pop()

    def grow(self, growth=1):
        """Increase the size of the snake by a specified amount"""
        self.grow_counter += growth

    def change_color(self, head_color, body_color):
        """Change the color of the snake"""
        self.head_color = head_color
        self.body_color = body_color

    def draw(self, screen):
        """Draw the snake on the screen"""
        for i, (x, y) in enumerate(self.body):
            rect = pygame.Rect(
                x * Config.GRID_SIZE,
                y * Config.GRID_SIZE,
                Config.GRID_SIZE,
                Config.GRID_SIZE,
            )
            if i == 0:  # Draw head with different color and eyes
                pygame.draw.rect(screen, self.head_color, rect)
                self.draw_eyes(screen, rect)
            else:
                pygame.draw.rect(screen, self.body_color, rect)

    def draw_eyes(self, screen, rect):
        """Draw the eyes of the snake's head"""
        eye_radius = Config.GRID_SIZE // 8
        eye_offset_x = Config.GRID_SIZE // 3
        eye_offset_y = Config.GRID_SIZE // 3
        eye_color = Config.BLACK

        # Calculate eye positions
        center_x = rect.x + rect.width // 2
        center_y = rect.y + rect.height // 2
        eye1_pos = (center_x - eye_offset_x, center_y - eye_offset_y)
        eye2_pos = (center_x + eye_offset_x, center_y - eye_offset_y)

        # Draw eyes
        pygame.draw.circle(screen, eye_color, eye1_pos, eye_radius)
        pygame.draw.circle(screen, eye_color, eye2_pos, eye_radius)


class GameManager:
    def __init__(self):
        """Initialize the game manager"""
        pygame.init()
        self.screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        self.font = pygame.font.Font("freesansbold.ttf", 24)
        self.clock = pygame.time.Clock()
        self.score = 0
        self.level = 1
        self.level_target = Config.POINTS_PER_LEVEL
        self.snake = Snake(
            Config.WIDTH // Config.GRID_SIZE // 2,
            Config.HEIGHT // Config.GRID_SIZE // 2,
            3,
        )
        self.grid = self.create_grid(
            Config.WIDTH // Config.GRID_SIZE, Config.HEIGHT // Config.GRID_SIZE
        )
        self.place_fruit()
        self.place_walls()  # Add walls to the grid
        self.game_over = False
        self.start_time = 0

    def create_grid(self, width, height):
        """Create an empty grid with the specified dimensions"""
        return [[None for _ in range(width)] for _ in range(height)]

    def place_fruit(self):
        """Place a fruit on a random empty cell in the grid"""
        empty_cells = self.get_empty_cells()
        if empty_cells:
            x, y = random.choice(empty_cells)
            fruit_color = random.choice(Config.FRUIT_COLORS)
            self.grid[y][x] = Fruit(x, y, fruit_color)

    def place_walls(self):
        """Place walls on the grid"""
        if self.level > 1:
            wall_positions = []
            num_walls = self.level + 1
            empty_cells = self.get_empty_cells()
            if len(empty_cells) >= num_walls:
                wall_positions = random.sample(empty_cells, num_walls)

            for x, y in wall_positions:
                self.grid[y][x] = Wall(x, y, Config.WALL_COLOR)

    def get_empty_cells(self):
        """Return a list of empty cells in the grid"""
        empty_cells = []
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell is None and (x, y) not in self.snake.body:
                    empty_cells.append((x, y))
        return empty_cells

    def draw_grid(self):
        """Draw the grid, snake, and game objects on the screen"""
        self.screen.fill(Config.BLACK)
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell is not None:
                    cell.draw(self.screen)

        self.snake.draw(self.screen)

    def update_speed(self):
        """Update the speed of the snake"""
        self.snake.speed = Config.INITIAL_SPEED + (self.level - 1) * 0.5

    def display_game_over(self):
        """Display the game over screen"""
        self.screen.fill(Config.BLACK)
        game_over_text = self.font.render("Game Over", True, Config.RED)
        level_text = self.font.render(f"Level: {self.level}", True, Config.WHITE)
        time_text = self.font.render(
            f"Time: {time.time() - self.start_time:.2f} seconds", True, Config.WHITE
        )
        score_text = self.font.render(f"Score: {self.score}", True, Config.WHITE)
        restart_text = self.font.render(
            "Press SPACE to restart or Esc to quit", True, Config.WHITE
        )

        self.screen.blit(
            game_over_text,
            (Config.WIDTH // 2 - game_over_text.get_width() // 2, 150),
        )
        self.screen.blit(
            level_text, (Config.WIDTH // 2 - level_text.get_width() // 2, 200)
        )
        self.screen.blit(
            time_text, (Config.WIDTH // 2 - time_text.get_width() // 2, 250)
        )
        self.screen.blit(
            score_text, (Config.WIDTH // 2 - score_text.get_width() // 2, 300)
        )
        self.screen.blit(
            restart_text, (Config.WIDTH // 2 - restart_text.get_width() // 2, 350)
        )

        pygame.display.flip()

    def display_game_win(self):
        """Display the game win screen"""
        self.screen.fill(Config.BLACK)
        game_win_text = self.font.render("You Win!", True, Config.GREEN)
        level_text = self.font.render(f"Level: {self.level}", True, Config.WHITE)
        time_text = self.font.render(
            f"Time: {time.time() - self.start_time:.2f} seconds", True, Config.WHITE
        )
        score_text = self.font.render(f"Score: {self.score}", True, Config.WHITE)
        restart_text = self.font.render(
            "Press SPACE to restart or Esc to quit", True, Config.WHITE
        )

        self.screen.blit(
            game_win_text,
            (Config.WIDTH // 2 - game_win_text.get_width() // 2, 150),
        )
        self.screen.blit(
            level_text, (Config.WIDTH // 2 - level_text.get_width() // 2, 200)
        )
        self.screen.blit(
            time_text, (Config.WIDTH // 2 - time_text.get_width() // 2, 250)
        )
        self.screen.blit(
            score_text, (Config.WIDTH // 2 - score_text.get_width() // 2, 300)
        )
        self.screen.blit(
            restart_text, (Config.WIDTH // 2 - restart_text.get_width() // 2, 350)
        )

        pygame.display.flip()

    def game_loop(self):
        """Main game loop"""
        self.start_time = time.time()
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                if self.snake.direction != Config.DOWN:
                    self.snake.direction = Config.UP
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                if self.snake.direction != Config.UP:
                    self.snake.direction = Config.DOWN
            elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                if self.snake.direction != Config.RIGHT:
                    self.snake.direction = Config.LEFT
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                if self.snake.direction != Config.LEFT:
                    self.snake.direction = Config.RIGHT

            # Snake moves
            self.snake.move()

            # Check if snake is out of bounds or collided with itself or a wall
            x, y = self.snake.body[0]
            if (
                x < 0
                or x >= Config.WIDTH // Config.GRID_SIZE
                or y < 0
                or y >= Config.HEIGHT // Config.GRID_SIZE
                or (x, y) in self.snake.body[1:]
                or isinstance(self.grid[y][x], Wall)
            ):
                self.game_over = True
                break

            # Check if snake eats fruit
            if isinstance(self.grid[y][x], Fruit):
                self.grid[y][x] = None
                self.place_fruit()
                self.snake.grow()
                self.score += 1
                if self.score >= self.level_target and self.level < Config.MAX_LEVEL:
                    self.level += 1
                    self.level_target += Config.POINTS_PER_LEVEL
                    self.update_speed()
                    self.place_walls()  # Add walls to the grid
                    head_color = random.choice(Config.FRUIT_COLORS)
                    body_color = random.choice(Config.FRUIT_COLORS)
                    self.snake.change_color(head_color, body_color)

            self.draw_grid()

            # Display Score
            score_text = self.font.render(f"Score: {self.score}", True, Config.WHITE)
            self.screen.blit(score_text, (10, 10))

            # Display Level
            level_text = self.font.render(f"Level: {self.level}", True, Config.WHITE)
            self.screen.blit(level_text, (10, 40))

            pygame.display.flip()
            self.clock.tick(Config.FPS)

        if self.level > Config.MAX_LEVEL:
            self.display_game_win()
        else:
            self.display_game_over()

    def start(self):
        """Start the game"""
        while True:
            self.game_loop()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.__init__()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()


if __name__ == "__main__":
    game = GameManager()
    game.start()
