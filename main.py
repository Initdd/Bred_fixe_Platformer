import pygame
from pygame.locals import *
from pygame import mixer
import pickle
import os

mixer.init(44100, -16, 2, 512)
pygame.init()

clock = pygame.time.Clock()
fps = 60

cp = 'D:\Programming\pyton\projects\Bred_fixe_Platformer\\'
tile_size = 35
cols = 20
margin = 100
screen_width = tile_size * cols
screen_height = (tile_size * cols) + margin

screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption('Bred Fixe Platformer')
icon = pygame.image.load(cp+'images\sm.png')        # A variable for the icon of the game
pygame.display.set_icon(icon) 

#define font
font = pygame.font.SysFont("Bauhaus 93", 60)
font_score = pygame.font.SysFont("Bauhaus 93", 30)

#define game variables
game_over = 0
level = 1
max_levels = 8
score = 0
loop1 = True
loop2 = False
loop3 = False
loop4 = False
loop5 = False
music_paused = False
vol = 0.5


#define colors
white = (255, 255, 255)
blue = (0, 0, 255)

#load images
scale = 2
sm_img = pygame.image.load(cp+"images/ce.png")
width = sm_img.get_width()
height = sm_img.get_height()
sm_img = pygame.transform.scale(sm_img, (int(width * scale), int(height * scale)))
sun_img = pygame.image.load(cp+'images/sun.png')
bg_img = pygame.image.load(cp+'images/sky.png')
restart_img = pygame.image.load(cp+'images/restart.png')
start_img = pygame.image.load(cp+'images/start2.png')
level_img = pygame.image.load(cp+'images/level.png')
stop_img = pygame.image.load(cp+'images/stop.png')
img_0 = pygame.image.load(cp+'images/num/0.png')
img_1 = pygame.image.load(cp+'images/num/1.png')
img_2 = pygame.image.load(cp+'images/num/2.png')
img_3 = pygame.image.load(cp+'images/num/3.png')
img_4 = pygame.image.load(cp+'images/num/4.png')
img_5 = pygame.image.load(cp+'images/num/5.png')
img_6 = pygame.image.load(cp+'images/num/6.png')
img_7 = pygame.image.load(cp+'images/num/7.png')
exit_img = pygame.image.load(cp+'images/exit.png')
menu_img = pygame.image.load(cp+'images/menu.png')
sound_img = pygame.image.load(cp+'images/sound.png')

#load sounds
pygame.mixer.music.load(cp+'images/music.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
coin_fx = pygame.mixer.Sound(cp+'images/coin.wav')
coin_fx.set_volume(vol)
jump_fx = pygame.mixer.Sound(cp+'images/jump.wav')
jump_fx.set_volume(vol)
game_over_fx = pygame.mixer.Sound(cp+'images/game_over.wav')
game_over_fx.set_volume(vol)
#walk_fx = pygame.mixer.Sound(cp+'images/walk1.ogg')
#walk_fx.set_volume(0.25)


def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

#function to reset level
def reset_level(level):
	player.reset(100, screen_height - 130)
	coin_group.empty()
	blob_group.empty()
	platform_group.empty()
	lava_group.empty()
	exit_group.empty()

	# load level and create world
	if os.path.exists(cp+f"levels/level{level}_data"):
		pickle_in = open(cp+f"levels/level{level}_data", "rb")
		world_data = pickle.load(pickle_in)
	else:
		pickle_in = open(cp+f"levels/level0_data", "rb")
		world_data = pickle.load(pickle_in)
	world = World(world_data)

	return world

class Button():
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False

	def draw(self):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False


		#draw button
		screen.blit(self.image, self.rect)

		return action


class Player():
	def __init__(self, x, y):
		self.reset(x, y)



	def update(self, game_over):
		dx = 0
		dy = 0
		walk_cooldown = 5
		col_thresh = 20

		if game_over == 0:
			#get keypresses
			key = pygame.key.get_pressed()
			if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
				jump_fx.play()
				self.vel_y = -15
				self.jumped = True
			if key[pygame.K_SPACE] == False:
				self.jumped = False
			if key[pygame.K_LEFT]:
				dx -= 5
				self.counter += 1
				self.direction = -1
				
			if key[pygame.K_RIGHT]:
				dx += 5
				self.counter += 1
				self.direction = 1
				
			if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
				self.counter = 0
				self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			#handle animation
			if self.counter > walk_cooldown:
				self.counter = 0	
				self.index += 1
				if self.index >= len(self.images_right):
					self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			#add gravity
			self.vel_y += 1
			if self.vel_y > 10:
				self.vel_y = 10
			dy += self.vel_y

			#check for collision
			self.in_air = True
			for tile in world.tile_list:
				#check for collision in x direction
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#check for collision in y direction
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below the ground i.e. jumping
					if self.vel_y < 0:
						dy = tile[1].bottom - self.rect.top
						self.vel_y = 0
					#check if above the ground i.e. falling
					elif self.vel_y >= 0:
						dy = tile[1].top - self.rect.bottom
						self.vel_y = 0
						self.in_air = False


			#check for collision with enemies
			
			for blob in blob_group:
				#collision with the x direction
				if blob.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					game_over = -1
				#collision with the y direction
				if blob.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					self.rect.bottom = blob.rect.top - 1
					self.in_air = False
					dy = 0
					self.vel_y = -5
					self.jumped = True
					blob.kill()

			#check for collision with lava
			if pygame.sprite.spritecollide(self, lava_group, False):
				game_over = -1
				game_over_fx.play()
			
			#check collision with the exit
			if pygame.sprite.spritecollide(self, exit_group, False):
				game_over = 1

			#check for collision with platforms
			for platform in platform_group:
				#collision with the x direction
				if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#collision with the y direction
				if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below platform
					if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
						self.vel_y = 0
						dy = platform.rect.bottom - self.rect.top
					#check if above platform
					elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
						self.rect.bottom = platform.rect.top - 1
						self.in_air = False
						dy = 0
					#move sideways with platform
					if platform.move_x != 0:
						self.rect.x += platform.move_direction

			#update player coordinates
			self.rect.x += dx
			self.rect.y += dy


		elif game_over == -1:
			self.image = self.dead_image
			draw_text("GAME OVER!", font, blue, (screen_width // 2) - 200, screen_height // 2 )
			if self.rect.y > 200:
				self.rect.y -= 5

		#draw player onto screen
		screen.blit(self.image, self.rect)
		#pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

		return game_over


	def reset(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1, 5):
			img_right = pygame.image.load(cp+f'images/player/player_sprite.{num}.png')
			img_right = pygame.transform.scale(img_right, (30, 60))
			img_left = pygame.transform.flip(img_right, True, False)
			self.images_right.append(img_right)
			self.images_left.append(img_left)
		scale = 0.4
		dead_image = pygame.image.load(cp+"images/ghost.png")
		width = dead_image.get_width()
		height = dead_image.get_height()
		self.dead_image = pygame.transform.scale(dead_image, (int(width * scale), int(height * scale)))
		self.image = self.images_right[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.vel_y = 0
		self.jumped = False
		self.direction = 0
		self.in_air = True



class World():
	def __init__(self, data):
		self.tile_list = []

		#load images
		dirt_img = pygame.image.load(cp+'images/dirt.png')
		grass_img = pygame.image.load(cp+'images/grass.png')

		row_count = 0
		for row in data:
			col_count = 0
			for tile in row:
				if tile == 1:
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 2:
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 3:
					blob = Enemy(col_count * tile_size, row_count * tile_size + 8)
					blob_group.add(blob)
				if tile == 4:
					platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
					platform_group.add(platform)
				if tile == 5:
					platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1 )
					platform_group.add(platform)
				if tile == 6:
					lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
					lava_group.add(lava)
				if tile == 7:
					coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
					coin_group.add(coin)
				if tile == 8:
					exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
					exit_group.add(exit)

				col_count += 1
			row_count += 1

	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])
			#pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)



class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		scale = 0.035
		image = pygame.image.load(cp+"images\slime.png")
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_direction = 1
		self.move_counter = 0
		self.dead = False

	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 25:
			self.move_direction *= -1
			self.move_counter *= -1



class Platform(pygame.sprite.Sprite):
	def __init__(self, x, y, move_x, move_y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load(cp+"images\platform.png")
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_counter = 0
		self.move_direction = 1
		self.move_x = move_x
		self.move_y = move_y

	def update(self):
		self.rect.x += self.move_direction * self.move_x
		self.rect.y += self.move_direction * self.move_y
		self.move_counter += 1
		if abs(self.move_counter) > 25:
			self.move_direction *= -1
			self.move_counter *= -1	


class Lava(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load(cp+"images\lava.png")
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

class Coin(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load(cp+"images\coin.png")
		self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)

class Exit(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load(cp+"images\portal.png")
		self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

player = Player(100, screen_height - 130)

blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#create dummy coin to score
score_coin = Coin(tile_size // 2 - 5, tile_size // 2 + 10)
coin_group.add(score_coin)

# Load world data and create world
if os.path.exists(cp+f"levels/level{level}_data"):
	pickle_in = open(cp+f"levels/level{level}_data", "rb")
	world_data = pickle.load(pickle_in)
else:
	print(os.getcwd())
	pickle_in = open(cp+f"levels/level0_data", "rb")
	world_data = pickle.load(pickle_in)
world = World(world_data)

#create buttons
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img, 1)
start_button = Button(screen_width // 2 - 250, screen_height // 2 + 150, start_img, 0.5)
level_button = Button(screen_width // 2 - 80, screen_height // 2 + 149, level_img, 1.35)
stop_button = Button(screen_width // 2 + 50, screen_height // 2 + 150, stop_img, 0.5)
btn_0 = Button(100, 100, img_0, 1)
btn_1 = Button(200, 100, img_1, 1)
btn_2 = Button(300, 100, img_2, 1)
btn_3 = Button(400, 100, img_3, 1)
btn_4 = Button(500, 100, img_4, 1)
btn_5 = Button(100, 200, img_5, 1)
btn_6 = Button(200, 200, img_6, 1)
btn_7 = Button(300, 200, img_7, 1)
exit_button = Button(screen_width // 2 - 50, screen_height // 2 + 150, exit_img, 0.7)
menu_button = Button(590, 50, menu_img, 0.85)
sound_btn = Button(100, 100, sound_img, 1)


run = True

while run:
	
	key = pygame.key.get_pressed()
	if key[pygame.K_ESCAPE]:
		level = 0
		#reset level
		#coin_group.empty()
		world_data = []
		world = reset_level(level)
		game_over = 0
		
		score = 0
		loop2 = False
		loop1 = True
		loop3 = False
		loop4 = False
		loop5 = False
	
	clock.tick(fps)

	if loop1 == True:
		screen.fill((255, 152, 0))
		screen.blit(sm_img, (0, 100))

		if stop_button.draw():
			run = False
		if start_button.draw():
			loop1 = False
			loop2 = True
			loop3 = False
			loop4 = False
			loop5 = False
		"""
		if level_button.draw():
			loop1 = False
			loop2 = False
			loop3 = True
			loop4 = False
			loop5 = False
		"""
		if menu_button.draw():
			loop1 = False
			loop2 = False
			loop3 = False
			loop4 = False
			loop5 = True


	if loop2 == True:
		screen.blit(bg_img, (0, 0))
		screen.blit(sun_img, (100, 100))
		world.draw()

		if game_over == 0:
			blob_group.update()
			platform_group.update()
			coin_group.update()
			#update score
			#check if coin collected
			if pygame.sprite.spritecollide(player, coin_group, True):
				score += 1
				coin_fx.play()

			if pygame.sprite.spritecollide(player, blob_group, True):
				print("hi")

			draw_text("X " + str(score), font_score, white, tile_size - 10, 10)
			#print(score)

		
		blob_group.draw(screen)
		platform_group.draw(screen)
		lava_group.draw(screen)
		coin_group.draw(screen)
		exit_group.draw(screen)

		game_over = player.update(game_over)

		#if player has died
		if game_over == -1:
			if restart_button.draw():
				world_data = []
				world = reset_level(level)
				game_over = 0
				score = 0

		#if player has completed the level
		if game_over == 1:
			#reset game and go to the next level
			level += 1
			if level <= max_levels:
				#reset level
				world_data = []
				world = reset_level(level)
				game_over = 0
				
			else:
				draw_text("You Won with " + str(score) + " points", font, blue, (screen_width // 2) - 270, screen_height // 2)
				#restart game
				if restart_button.draw():
					level = 0
					#reset level
					world_data = []
					world = reset_level(level)
					game_over = 0
					score = 0

	if loop3 == True:
		screen.fill((255, 152, 0))

		# Buttons
		if btn_0.draw():
			cen = 5
			#change loop
			loop1 = False
			loop2 = False
			loop3 = False
			loop4 = True
			loop5 = False

		if btn_1.draw():
			print("hi")
		if btn_2.draw():
			print("hi")
		if btn_3.draw():
			print("hi")
		if btn_4.draw():
			print("hi")
		if btn_5.draw():
			print("hi")
		if btn_6.draw():
			print("hi")
		if btn_7.draw():
			print("hi")

	if loop4 == True:
		level = 7
		screen.blit(bg_img, (0, 0))
		screen.blit(sun_img, (100, 100))
		world.draw()

		if game_over == 0:
			level = 7
			blob_group.update()
			platform_group.update()
			#update score
			#check if coin collected
			if pygame.sprite.spritecollide(player, coin_group, True):
				score += 1
				coin_fx.play()
			for blob in blob_group:
				if blob.dead:
					blob_group.kill()

			draw_text("X " + str(score), font_score, white, tile_size - 10, 10)
			#print(score)

		
		blob_group.draw(screen)
		platform_group.draw(screen)
		lava_group.draw(screen)
		coin_group.draw(screen)
		exit_group.draw(screen)

		game_over = player.update(game_over)

		#if player has died
		if game_over == -1:
			if restart_button.draw():
				world_data = []
				world = reset_level(level)
				game_over = 0
				score = 0

		#if player has completed the level
		if game_over == 1:

			draw_text("You Won with " + str(score) + " points", font, blue, (screen_width // 2) - 300, screen_height // 2)
					#restart game
			if exit_button.draw():
				level = 0
				#reset level
				world_data = []
				world = reset_level(level)
				game_over = 0
				score = 0
				loop4 = False
				loop3 = True
				loop5 = False

	if loop5 == True:
		screen.fill((255, 152, 0))
		if sound_btn.draw():
			if not music_paused:
				pygame.mixer.music.pause()
				music_paused = True
			else:
				pygame.mixer.music.unpause()
				music_paused = False


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()

pygame.quit()