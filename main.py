import pygame as pg 
import constants as c
from enemy import Enemy
from world import World
import json
from turret import Turret
from button import Button
#initialise pygame

pg.init()

clock = pg.time.Clock()




#create game window
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL,c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defense")

#game variables
last_enemy_spawn = pg.time.get_ticks()
placing_turrets = False
selected_turret = None
level_started = False
game_over = False
game_outcome = 0#-1 is loss, 1 is win

#load images
map_image = pg.image.load("assets/images/levelmaps/level.png").convert_alpha()
turret_spritesheets = []
for x in range(1,c.TURRET_LEVELS +1):
    turret_sheet =  pg.image.load(f"assets/images/turrets/turret_{x}.png").convert_alpha()
    turret_spritesheets.append(turret_sheet)
cursor_turret = pg.image.load("assets/images/turrets/cursor_turret.png").convert_alpha()
enemy_images = {
    "weak" : pg.image.load("assets/images/enemies/enemy_1.png").convert_alpha(),
    "medium" : pg.image.load("assets/images/enemies/enemy_2.png").convert_alpha(),
    "strong" : pg.image.load("assets/images/enemies/enemy_3.png").convert_alpha(),
    "elite" : pg.image.load("assets/images/enemies/enemy_4.png").convert_alpha()
}
#buttons
buy_turret_image = pg.image.load("assets/images/buttons/buy_turret.png").convert_alpha()
cancel_image = pg.image.load("assets/images/buttons/cancel.png").convert_alpha()
upgrade_turret_image = pg.image.load("assets/images/buttons/upgrade_turret.png").convert_alpha()
begin_image = pg.image.load("assets/images/buttons/begin.png").convert_alpha()
restart_image = pg.image.load("assets/images/buttons/restart.png").convert_alpha()
fast_forward_image = pg.image.load("assets/images/buttons/fast_forward.png").convert_alpha()

#gui
heart_image = pg.image.load("assets/images/gui/heart.png").convert_alpha()
coin_image = pg.image.load("assets/images/gui/coin.png").convert_alpha()
logo_image = pg.image.load("assets/images/gui/logo.png").convert_alpha ()

#load sounds
shot_fx = pg.mixer.Sound('assets/audio/shot.wav')
shot_fx.set_volume(0.5)

#load json data
with open("assets/images/levelmaps/level.tmj") as file:
    world_data = json.load(file)

#load fonts fot displaying text on the screen
text_font = pg.font.SysFont("Consolas", 24,  bold = True)
large_font = pg.font.SysFont("Consolas", 36)

#Function for outputting text on the screen
def draw_text(text,font, text_col, x,y):
    img = font.render(text,True, text_col)
    screen.blit(img,(x,y))

def display_data():
    #draw panel
    pg.draw.rect(screen, "maroon", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, c.SCREEN_HEIGHT))
    pg.draw.rect(screen, "grey0", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, 400), 2)
    screen.blit(logo_image,(c.SCREEN_WIDTH, 400))

    #display data
    draw_text("Level:" +str(world.level), text_font, "grey100", c.SCREEN_WIDTH+10 ,10)
    screen.blit(heart_image, (c.SCREEN_WIDTH+10,35))
    draw_text(str(world.health), text_font, "grey100", c.SCREEN_WIDTH+50,40)
    screen.blit(coin_image, (c.SCREEN_WIDTH+10,65))
    draw_text(str(world.money), text_font, "grey100", c.SCREEN_WIDTH +50, 70)


def create_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE 
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE 
    #calculate  the sequential number of the tile
    mouse_tile_num = (mouse_tile_y*c.COLS)+ mouse_tile_x
    #check if that tile is grass
    if world.tile_map[mouse_tile_num] == 1164 or world.tile_map[mouse_tile_num] == 248 or world.tile_map[mouse_tile_num] == 1163:
        #check if chosen tile already has a turret on it
        space_is_free =  True
        for turret in turret_group:
            if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
                space_is_free = False
        if space_is_free:
            new_turret = Turret(turret_spritesheets,mouse_tile_x,mouse_tile_y, shot_fx)
            turret_group.add(new_turret)
            #deduct cost of money
            world.money -= c.BUY_COST
def select_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE 
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE 
    for turret in turret_group:
        if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
            return turret
        
def clear_selection():
    for turret in turret_group:
        turret.selected = False
#create world
world = World(world_data, map_image)
world.process_data()
world.process_enemies()
#create groups 

enemy_group =   pg.sprite.Group()
turret_group = pg.sprite.Group()


#create buttons
turret_button = Button(c.SCREEN_WIDTH+30, 120 , buy_turret_image, True)
cancel_button = Button(c.SCREEN_WIDTH+50, 180 , cancel_image, True)
upgrade_button = Button(c.SCREEN_WIDTH+5, 240 , upgrade_turret_image, True)
begin_button = Button(c.SCREEN_WIDTH+60, 300 , begin_image, True)
restart_button = Button(310, 300 , restart_image, True)
fast_forward_button = Button(c.SCREEN_WIDTH+50, 300 , fast_forward_image, False)
#game loop
run = True
while run:
    #fps cap
    clock.tick(c.FPS)

    ########################
    #Updating section
    ########################
    
    if game_over == False:
        #check if player has lost
        if world.health<= 0:
            game_over = True
            game_outcome = -1

        #check if player has won
        if world.level > c.TOTAL_LEVELS:
            game_over = True
            game_outcome = 1
        #update groups
        enemy_group.update(world)
        turret_group.update(enemy_group, world)

        #highlight selected turret
        if selected_turret:
            selected_turret.selected = True


    ########################
    #Drawing section
    ########################

    #draw level
    world.draw(screen)


    #draw groups 
    enemy_group.draw(screen)
    for turret in turret_group:
        turret.draw(screen)

    display_data()



    if game_over == False:

        #check if the level has been started or not
        if level_started == False:
            if begin_button.draw(screen):
                level_started = True
        else:
            #fast forward
            world.game_speed = 1
            if fast_forward_button.draw(screen):
                world.game_speed = 2
            #spawn enemies
            if pg.time.get_ticks() - last_enemy_spawn> c.SPAWN_COOLDOWN:
                if world.spawned_enemies<   len(world.enemy_list):
                    enemy_type = world.enemy_list[world.spawned_enemies]
                    enemy = Enemy(enemy_type, world.waypoints,enemy_images)
                    enemy_group.add(enemy)
                    world.spawned_enemies+=1
                    last_enemy_spawn = pg.time.get_ticks()
        #check if the wave if finished
        if world.check_leve_complete():
            world.money += c.LEVEL_COMPLETE
            world.level += 1
            level_started = False
            last_enemy_spawn = pg.time.get_ticks()
            world.reset_level()
            world.process_enemies()
        #draw buttons
        #button for placing down turrets
        #for the "turret button show" cost of turret and draw the button
        draw_text(str(c.BUY_COST), text_font,"grey100", c.SCREEN_WIDTH + 215, 135)
        screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 130))
        if turret_button.draw(screen):
            placing_turrets = True
            #switch the buy button with the cancel button while buy is active
            
            #if placing turrets show cancel button as well
        if placing_turrets == True:
            #show cursor turret
            cursor_rect = cursor_turret.get_rect()
            cursor_pos = pg.mouse.get_pos()
            cursor_rect.center = cursor_pos
            if cursor_pos[0]<=c.SCREEN_WIDTH:
                screen.blit(cursor_turret, cursor_rect)
            if cancel_button.draw(screen):
                placing_turrets = False
            #if a turret is selected then show the upgrade button
        if selected_turret:
            #if a turret can be selected show selected button
            if selected_turret.upgrade_level<c.TURRET_LEVELS:
                #show cost of upgrade and draw the button
                draw_text(str(c.UPGRADE_COST), text_font, "grey100", c.SCREEN_WIDTH + 215, 255)
                screen. blit(coin_image,(c.SCREEN_WIDTH + 260, 250))
                if upgrade_button.draw(screen):
                    if world.money >= c.UPGRADE_COST:
                        selected_turret.upgrade()
                        world.money -= c.UPGRADE_COST

    else:
        pg.draw.rect(screen, "dodgerblue", (200,200,400,200), border_radius = 30)
        if game_outcome == -1:
            draw_text("Game over", large_font, "grey0" , 310, 230)
            #restart level
        elif game_outcome == 1:
            draw_text("You win", large_font, "grey0" , 315, 230)
        if restart_button.draw(screen):
           game_outcome = 0
           game_over = False
           level_started = False
           selected_turret = None
           last_enemy_spawn = pg.time.get_ticks()
           world = World(world_data, map_image)
           world.process_data()
           world.process_enemies()    
           #empty groups
           enemy_group.empty()
           turret_group.empty()
    #event handdler
    for event in pg.event.get():
    #quit program
        if event.type ==pg.QUIT:
            run = False
    #mouseclick
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos =pg.mouse.get_pos()
            #check if mouse is on the game area
            if mouse_pos[0]<c.SCREEN_WIDTH and mouse_pos[1]< c.SCREEN_HEIGHT:
                #clear selected turrets
                clear_selection()
                if placing_turrets == True:
                    #Check if there is enough money for turret
                    if world.money >= c.BUY_COST:
                        create_turret(mouse_pos)
                else:
                    selected_turret = select_turret(mouse_pos)
    #update display  
    pg.display.flip()
pg.quit()