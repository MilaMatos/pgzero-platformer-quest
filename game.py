import pgzrun
from pgzero.builtins import Actor, Rect, keyboard, sounds, music

WIDTH = 800
HEIGHT = 600
TITLE = "Platformer"

# --- Variaveis Globais ---
game_state = 'main_menu' 
music_on = True
GRAVITY = 0.3
elapsed_time = 0.0
final_time = 0.0

# --- ATORES DA INTERFACE (UI) ---
play_button = Actor('button_start.png')
restart_button = Actor('button_restart')
menu_button = Actor('button_menu')
sound_button = Actor('button_sound_on')
exit_button = Actor('button_exit') 
timer_plate = Actor('timer_plate', topleft=(10, 10))

music.play('background_music.wav')
music.set_volume(0.8)
if not music_on:
    music.pause()

class AnimatedActor:
    def __init__(self, image_files, pos, anchor=('center', 'bottom')):
        self.actor = Actor(image_files[0], pos=pos, anchor=anchor)
        self.animations = {'default': image_files}; self.current_anim = 'default'
        self.anim_frame = 0; self.anim_timer = 0; self.anim_speed = 0.15 
    def update_animation(self):
        self.anim_timer += 1 / 60.0 
        if self.anim_timer > self.anim_speed:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % len(self.animations[self.current_anim])
            image_name = self.animations[self.current_anim][self.anim_frame]
            self.actor.image = image_name

class Player(AnimatedActor):
    def __init__(self, pos):
        super().__init__(['hero_idle_1', 'hero_idle_2'], pos)
        self.animations = {'idle': ['hero_idle_1', 'hero_idle_2'], 'run': ['hero_run_1', 'hero_run_2'], 'jump': ['hero_jump']}
        self.current_anim = 'idle'
        self.vx = 0; self.vy = 0; self.on_ground = False; self.direction = 1

    def update(self, platforms):
        if keyboard.left: self.vx = -4; self.direction = -1; self.current_anim = 'run'
        elif keyboard.right: self.vx = 4; self.direction = 1; self.current_anim = 'run'
        else: self.vx = 0; self.current_anim = 'idle'
        
        self.vy += GRAVITY
        if self.vy > 10: self.vy = 10
        
        self.actor.x += self.vx; self.actor.y += self.vy
        
        if self.actor.left < 0:
            self.actor.left = 0
        if self.actor.right > WIDTH:
            self.actor.right = WIDTH

        self.actor.flip_x = self.direction == -1
        if not self.on_ground: self.current_anim = 'jump'
        self.update_animation()
        
        self.on_ground = False
        for platform in platforms:
            if self.actor.colliderect(platform) and self.vy > 0:
                if self.actor.bottom < platform.bottom:
                    self.actor.bottom = platform.top
                    self.vy = 0; self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.vy = -7.5
            if music_on: sounds.jump_sound.play()

class Enemy(AnimatedActor):
    def __init__(self, platform, pos_offset_x=10):
        pos = (platform.left + pos_offset_x, platform.top)
        super().__init__(['enemy_walk_1', 'enemy_walk_2'], pos)
        self.platform_left = platform.left; self.platform_right = platform.right
        self.speed = 0.7
    def update(self):
        self.actor.x += self.speed
        if self.actor.right > self.platform_right or self.actor.left < self.platform_left:
            self.speed *= -1; self.actor.flip_x = self.speed > 0
        self.update_animation()

def setup_game():
    global player, platforms, enemies, goal_actor, elapsed_time, final_time
    elapsed_time = 0.0; final_time = 0.0
    timer_plate.topleft = (10, 10)
    player = Player((50, HEIGHT - 100))
    platforms = [
        Rect((0, HEIGHT - 40), (300, 40)), Rect((400, HEIGHT - 120), (100, 20)),
        Rect((200, HEIGHT - 200), (150, 20)), Rect((50, HEIGHT - 280), (100, 20)),
        Rect((250, HEIGHT - 360), (150, 20)), Rect((500, HEIGHT - 280), (100, 20)),
        Rect((650, HEIGHT - 360), (100, 20)), Rect((450, HEIGHT - 440), (150, 20)),
        Rect((200, HEIGHT - 520), (150, 20)),
    ]
    goal_actor = Actor('heart', pos=(300, HEIGHT - 570))
    enemies = [ Enemy(platform=platforms[1]), Enemy(platform=platforms[2]),
                Enemy(platform=platforms[3]), Enemy(platform=platforms[4]),
                Enemy(platform=platforms[5]), Enemy(platform=platforms[6]),
                Enemy(platform=platforms[7]), Enemy(platform=platforms[8]), ]
setup_game()

def draw_game_elements():
    for p in platforms:
        try:
            w = Rect((0,0), images.platform.get_size()).width
            for i in range(p.width // w + 1): screen.blit('platform', (p.x + i * w, p.y))
        except AttributeError: screen.draw.filled_rect(p, 'brown')
    goal_actor.draw(); player.actor.draw()
    for e in enemies: e.actor.draw()

def draw():
    screen.blit('background', (0, -170))
    if game_state in ['playing', 'paused', 'game_over', 'win']:
        draw_game_elements()

    if game_state == 'main_menu':
        play_button.pos = (WIDTH / 2, HEIGHT / 2 - 120)
        sound_button.pos = (WIDTH / 2, HEIGHT / 2)
        exit_button.pos = (WIDTH / 2, HEIGHT / 2 + 120)
        play_button.draw(); sound_button.draw(); exit_button.draw()
    
    elif game_state == 'playing':
        timer_plate.draw()
        screen.draw.text(f"{elapsed_time:.1f}", center=(timer_plate.centerx + 25, timer_plate.centery), fontsize=30, color="white")
    
    elif game_state == 'game_over' or game_state == 'win':
        screen.draw.filled_rect(Rect(0,0,WIDTH,HEIGHT), (0,0,0,150))
        restart_button.pos = (WIDTH/2 - 50, HEIGHT/2 + 120)
        menu_button.pos = (WIDTH/2 + 50, HEIGHT/2 + 120)
        sound_button.pos = (WIDTH - 50, 50) 
        
        if game_state == 'game_over':
            screen.draw.text("GAME OVER", center=(WIDTH/2, HEIGHT/2 - 50), fontsize=80, color="#d0bd7d", owidth=1.5)
        else:
            screen.draw.text("WIN", center=(WIDTH/2, HEIGHT/2 - 100), fontsize=100, color="#d0bd7d", owidth=1.5)
            timer_plate.center = (WIDTH/2, HEIGHT/2 + 30)
            timer_plate.draw()
            screen.draw.text(f"{final_time:.2f}", center=(timer_plate.centerx + 25, timer_plate.centery), fontsize=40, color="white")
        restart_button.draw(); menu_button.draw(); sound_button.draw()

    elif game_state == 'paused':
        screen.draw.filled_rect(Rect(0,0,WIDTH,HEIGHT), (0,0,0,150))
        screen.draw.text("PAUSE", center=(WIDTH/2, HEIGHT/2 - 100), fontsize=80, color="#d0bd7d", owidth=1.5)
        play_button.pos = (WIDTH / 2, HEIGHT / 2)
        restart_button.pos = (WIDTH/2 - 50, HEIGHT/2 + 120)
        menu_button.pos = (WIDTH/2 + 50, HEIGHT/2 + 120)
        sound_button.pos = (WIDTH - 50, 50)
        play_button.draw(); restart_button.draw(); menu_button.draw(); sound_button.draw()

def update():
    global game_state, elapsed_time, final_time
    if game_state == 'playing':
        elapsed_time += 1 / 60.0
        player.update(platforms)
        if player.actor.colliderect(goal_actor):
            game_state = 'win'; final_time = elapsed_time
        for e in enemies:
            e.update()
            if player.actor.colliderect(e.actor):
                if music_on: sounds.hit_sound.play()
                game_state = 'game_over'
        if player.actor.top > HEIGHT:
            game_state = 'game_over'

def on_key_down(key):
    global game_state
    if key == keys.ESCAPE and game_state in ['playing', 'paused']:
        if game_state == 'playing':
            game_state = 'paused'
        else: 
            game_state = 'playing'
    if game_state == 'playing':
        if key == keys.SPACE or key == keys.UP:
            player.jump()

def on_mouse_down(pos):
    global game_state, music_on
    if game_state in ['main_menu', 'paused', 'game_over', 'win']:
        if sound_button.collidepoint(pos):
            music_on = not music_on
            sound_button.image = 'button_sound_on' if music_on else 'button_sound_off'
            if music_on:
                music.unpause()
            else:
                music.pause()
            return

    if game_state == 'main_menu':
        if play_button.collidepoint(pos):
            game_state = 'playing'
        elif exit_button.collidepoint(pos):
            quit()
            
    elif game_state == 'paused':
        if play_button.collidepoint(pos):
            game_state = 'playing'
        elif restart_button.collidepoint(pos):
            setup_game()
            game_state = 'playing'
        elif menu_button.collidepoint(pos):
            setup_game()
            game_state = 'main_menu'
            
    elif game_state in ['game_over', 'win']:
        if restart_button.collidepoint(pos):
            setup_game()
            game_state = 'playing'
        elif menu_button.collidepoint(pos):
            setup_game()
            game_state = 'main_menu'

pgzrun.go()
