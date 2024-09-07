import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PLANE_WIDTH = 100
PLANE_HEIGHT = 20
BALL_RADIUS = 15
PLANE_COLOR = (0, 0, 255)  # Blue
BALL_COLOR = (255, 0, 0)   # Red
BOX_COLORS = {
    'green': (0, 255, 0),
    'red': (255, 0, 0),
    'blue': (0, 0, 255)
}
RED_BOX_COLOR = BOX_COLORS['red']
GREEN_BOX_COLOR = BOX_COLORS['green']
BLUE_BOX_COLOR = BOX_COLORS['blue']
POWERUP_COLORS = [(255, 215, 0), (255, 165, 0)]  # Gold, Orange
BACKGROUND_COLOR = (0, 0, 0) 
TEXT_COLOR = (255, 255, 255) 
FPS = 60
BOX_WIDTH = 80
BOX_HEIGHT = 20
POWERUP_WIDTH = 20
POWERUP_HEIGHT = 20
MAX_EXPAND_POWERUPS = 3  

# Set up display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Plane and Ball Game')

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def draw_objects(start_screen=False, level_selection=False, victory_screen=False, game_over=False):
    screen.fill(BACKGROUND_COLOR)
    
    if start_screen:
        draw_text('Click Start to Begin', font, TEXT_COLOR, screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)
        draw_text('Start', font, TEXT_COLOR, screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)
    if level_selection:
        draw_text('Select Level:', font, TEXT_COLOR, screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)
        draw_text('Level 1', font, TEXT_COLOR, screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        draw_text('Level 2', font, TEXT_COLOR, screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)
        draw_text('Level 3', font, TEXT_COLOR, screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100)
    elif victory_screen:
        draw_text('Victory!', font, TEXT_COLOR, screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)
        draw_text('Next Level', font, TEXT_COLOR, screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)
    elif game_over:
        draw_text('Game Over', font, TEXT_COLOR, screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)
    else:
        pygame.draw.rect(screen, PLANE_COLOR, plane)
        for ball, _, _ in balls:
            pygame.draw.ellipse(screen, BALL_COLOR, ball)
        
        for box in boxes:
            pygame.draw.rect(screen, box['color'], box['rect'])
        
        for powerup in powerups:
            color = (255, 255, 255) if powerup['type'] == 'triple' else (173, 216, 230)
            pygame.draw.rect(screen, color, powerup['rect'])
        
        draw_text(f'Score: {score}', font, TEXT_COLOR, screen, 100, 30)
        draw_text(f'High Score: {high_score}', font, TEXT_COLOR, screen, WINDOW_WIDTH - 100, 30)
    
    pygame.display.flip()




def move_ball():
    global balls, score, game_over

    for i, (ball, dx, dy) in enumerate(balls):
        ball.x += dx
        ball.y += dy
        
        if ball.left < 0 or ball.right > WINDOW_WIDTH:
            dx *= -1
        if ball.top < 0:
            dy *= -1
        
        if ball.colliderect(plane):
            dy *= -1
            ball.top = plane.top - BALL_RADIUS * 2
            score += 1

        global boxes
        boxes_to_remove = []
        for box in boxes:
            if ball.colliderect(box['rect']):
                if box['color'] == GREEN_BOX_COLOR:
                    boxes_to_remove.append(box)
                elif box['color'] == RED_BOX_COLOR:
                    box['color'] = GREEN_BOX_COLOR
                    box['hp'] = 1
                elif box['color'] == BLUE_BOX_COLOR:
                    box['color'] = RED_BOX_COLOR
                    box['hp'] = 2
                
                dy *= -1
                score += 5
                
                if random.random() < 0.2:
                    powerup_type = random.choice(['triple', 'expand'])
                    if powerup_type == 'expand' and sum(1 for p in powerups if p['type'] == 'expand') < MAX_EXPAND_POWERUPS:
                        powerup = {
                            'type': powerup_type,
                            'rect': pygame.Rect(box['rect'].centerx - POWERUP_WIDTH // 2, box['rect'].bottom, POWERUP_WIDTH, POWERUP_HEIGHT),
                            'color': random.choice(POWERUP_COLORS)
                        }
                        powerups.append(powerup)
                    elif powerup_type == 'triple':
                        powerup = {
                            'type': powerup_type,
                            'rect': pygame.Rect(box['rect'].centerx - POWERUP_WIDTH // 2, box['rect'].bottom, POWERUP_WIDTH, POWERUP_HEIGHT),
                            'color': random.choice(POWERUP_COLORS)
                        }
                        powerups.append(powerup)
        
        for box in boxes_to_remove:
            if box in boxes:
                boxes.remove(box)
        
        if ball.bottom > WINDOW_HEIGHT:
            balls.pop(i)
            if not balls:
                game_over = True
        else:
            balls[i] = (ball, dx, dy)

def move_powerups():
    global powerups
    for powerup in powerups[:]:  # Iterate over a copy to safely modify the list
        powerup['rect'].y += 2  # Decrease the speed here
        if powerup['rect'].top > WINDOW_HEIGHT:
            powerups.remove(powerup)

def check_powerup_collision():
    global powerups, plane, balls

    for powerup in powerups[:]:  # Iterate over a copy to safely modify the list
        if powerup['rect'].colliderect(plane):
            if powerup['type'] == 'triple':
                # Find the highest ball
                highest_ball = max(balls, key=lambda b: b[0].top)[0]
                # Determine the spawn positions
                spawn_positions = [
                    (highest_ball.left, highest_ball.top),
                    (highest_ball.centerx - BALL_RADIUS * 2, highest_ball.top),
                    (highest_ball.centerx + BALL_RADIUS * 2, highest_ball.top)
                ]
                random.shuffle(spawn_positions)  # Shuffle to ensure different locations
                
                for pos in spawn_positions[:2]:  # Only add 2 more balls
                    new_ball_location = pygame.Rect(
                        pos[0],
                        pos[1] - BALL_RADIUS * 2,
                        BALL_RADIUS * 2, BALL_RADIUS * 2
                    )
                    new_ball_dx = random.choice([-4, 4])
                    new_ball_dy = -4
                    balls.append((new_ball_location, new_ball_dx, new_ball_dy))
                    
            elif powerup['type'] == 'expand':
                global PLANE_WIDTH
                PLANE_WIDTH += 20  # Increase width incrementally
                plane.width = PLANE_WIDTH
                plane.x = plane.centerx - plane.width // 2

            powerups.remove(powerup)

def initialize_level_1():
    global plane, score, ball_dx, ball_dy, game_over, start_game, plane_speed, high_score, boxes, powerups, balls
    game_over = False
    start_game = False
    plane = pygame.Rect(WINDOW_WIDTH // 2 - PLANE_WIDTH // 2, WINDOW_HEIGHT - PLANE_HEIGHT - 10, PLANE_WIDTH, PLANE_HEIGHT)
    ball = pygame.Rect(plane.centerx - BALL_RADIUS, plane.top - BALL_RADIUS * 2, BALL_RADIUS * 2, BALL_RADIUS * 2)
    ball_dx = random.choice([-4, 4])
    ball_dy = -4
    balls = [(ball, ball_dx, ball_dy)]
    score = 0
    high_score = 0
    
    boxes = []
    for i in range(5):  # Create 5 rows of boxes
        for j in range(10):  # Each row has 10 boxes
            box = pygame.Rect(j * (BOX_WIDTH + 10) + 10, i * (BOX_HEIGHT + 10) + 10, BOX_WIDTH, BOX_HEIGHT)
            boxes.append({'rect': box, 'color': GREEN_BOX_COLOR, 'hp': 1})
    
    powerups = []

def initialize_level_2():
    global plane, score, ball_dx, ball_dy, game_over, start_game, plane_speed, high_score, boxes, powerups, balls
    game_over = False
    start_game = False
    plane = pygame.Rect(WINDOW_WIDTH // 2 - PLANE_WIDTH // 2, WINDOW_HEIGHT - PLANE_HEIGHT - 10, PLANE_WIDTH, PLANE_HEIGHT)
    ball = pygame.Rect(plane.centerx - BALL_RADIUS, plane.top - BALL_RADIUS * 2, BALL_RADIUS * 2, BALL_RADIUS * 2)
    ball_dx = random.choice([-4, 4])
    ball_dy = -4
    balls = [(ball, ball_dx, ball_dy)]
    score = 0
    high_score = 0
    
    boxes = []
    for i in range(7):  # Create 7 rows of boxes
        for j in range(10):  # Each row has 10 boxes
            box = pygame.Rect(j * (BOX_WIDTH + 10) + 10, i * (BOX_HEIGHT + 10) + 10, BOX_WIDTH, BOX_HEIGHT)
            boxes.append({'rect': box, 'color': RED_BOX_COLOR, 'hp': 2})
    
    powerups = []

def initialize_level_3():
    global plane, score, ball_dx, ball_dy, game_over, start_game, plane_speed, high_score, boxes, powerups, balls
    game_over = False
    start_game = False
    plane = pygame.Rect(WINDOW_WIDTH // 2 - PLANE_WIDTH // 2, WINDOW_HEIGHT - PLANE_HEIGHT - 10, PLANE_WIDTH, PLANE_HEIGHT)
    ball = pygame.Rect(plane.centerx - BALL_RADIUS, plane.top - BALL_RADIUS * 2, BALL_RADIUS * 2, BALL_RADIUS * 2)
    ball_dx = random.choice([-4, 4])
    ball_dy = -4
    balls = [(ball, ball_dx, ball_dy)]
    score = 0
    high_score = 0
    
    boxes = []
    for i in range(9):  # Create 9 rows of boxes
        for j in range(10):  # Each row has 10 boxes
            box_color = BLUE_BOX_COLOR if random.random() < 0.3 else RED_BOX_COLOR if random.random() < 0.3 else GREEN_BOX_COLOR
            box = pygame.Rect(j * (BOX_WIDTH + 10) + 10, i * (BOX_HEIGHT + 10) + 10, BOX_WIDTH, BOX_HEIGHT)
            boxes.append({'rect': box, 'color': box_color, 'hp': 3 if box_color == BLUE_BOX_COLOR else 2 if box_color == RED_BOX_COLOR else 1})
    
    powerups = []


def main():
    global plane, score, ball_dx, ball_dy, game_over, plane_speed, high_score, boxes, powerups, balls
    level = None
    level_selection = True
    victory_screen = False

    while True:
        if level_selection:
            draw_objects(level_selection=True)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    if WINDOW_WIDTH // 2 - 100 <= mouse_x <= WINDOW_WIDTH // 2 + 100:
                        if WINDOW_HEIGHT // 2 - 25 <= mouse_y <= WINDOW_HEIGHT // 2 + 25:
                            level = 1
                        elif WINDOW_HEIGHT // 2 + 25 <= mouse_y <= WINDOW_HEIGHT // 2 + 75:
                            level = 2
                        elif WINDOW_HEIGHT // 2 + 75 <= mouse_y <= WINDOW_HEIGHT // 2 + 125:
                            level = 3
                        if level:
                            level_selection = False
                            break

        if level:
            if level == 1:
                initialize_level_1()
            elif level == 2:
                initialize_level_2()
            elif level == 3:
                initialize_level_3()

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = event.pos

                        if victory_screen:
                            if WINDOW_WIDTH // 2 - 50 <= mouse_x <= WINDOW_WIDTH // 2 + 50 and WINDOW_HEIGHT // 2 + 20 <= mouse_y <= WINDOW_HEIGHT // 2 + 80:
                                level += 1
                                victory_screen = False
                                if level > 3:  # Or however many levels you have
                                    level = 1  # Loop back to level 1 or end the game
                                break

                        elif game_over:
                            if WINDOW_WIDTH // 2 - 100 <= mouse_x <= WINDOW_WIDTH // 2 + 100 and WINDOW_HEIGHT // 2 + 20 <= mouse_y <= WINDOW_HEIGHT // 2 + 80:
                                level = None
                                level_selection = True
                                victory_screen = False
                                game_over = False
                                break

                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] and plane.left > 0:
                    plane.x -= plane_speed
                if keys[pygame.K_RIGHT] and plane.right < WINDOW_WIDTH:
                    plane.x += plane_speed

                move_ball()
                move_powerups()
                check_powerup_collision()

                if not boxes:  # No boxes left means the player has completed the level
                    victory_screen = True
                    draw_objects(victory_screen=victory_screen)
                    pygame.display.flip()
                    pygame.time.wait(2000)  # Show the victory screen for 2 seconds
                    break  # Exit the level loop to proceed to the next level

                if game_over:
                    if score > high_score:
                        high_score = score
                    draw_objects(game_over=True)
                    pygame.display.flip()
                    pygame.time.wait(2000)
                    score = 0  # Reset the score here
                    level = None  # Return to level selection
                    level_selection = True
                    break

                draw_objects()
                clock.tick(FPS)

if __name__ == "__main__":
    plane_speed = 15 
    main()
    pygame.quit()