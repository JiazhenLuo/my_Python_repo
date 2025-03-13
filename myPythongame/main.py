import random 
import sys 
import pygame 
from pygame.locals import *

pygame.init() 
pygame.mixer.init()

window_width = 600
window_height = 500
framepersecond = 30
window = pygame.display.set_mode((window_width, window_height)) 

elevation = window_height * 0.8
game_images = {}

sound_effects = {
	"score": pygame.mixer.Sound("assets/score.mp3"),
	"gameover":pygame.mixer.Sound("assets/gameover.mp3")
}

pipeimage = 'images/pipe.png'
background_image = 'images/background.png'
birdplayer_image = 'images/bird.png'
sealevel_image = 'images/base.png'
bullet_image = pygame.image.load('images/bullet.png').convert_alpha()
cloud_images = [
	pygame.image.load('images/cloud1.png').convert_alpha(),
    pygame.image.load('images/cloud2.png').convert_alpha(),
    pygame.image.load('images/cloud3.png').convert_alpha(),
]

class Cloud:
	def __init__(self, images, window_width, window_height):
		self.images = images
		self.original_image = random.choice(self.images)
		scale_factor = 0.5
		new_size = (
			int(self.original_image.get_width() * scale_factor),
            int(self.original_image.get_height() * scale_factor)
        )
		self.image = pygame.transform.scale(self.original_image, new_size)
		self.x = random.randint(window_width, window_width + random.randint(100,200))
		self.y = random.randint(0,window_height - 300)
		self.speed = random.uniform(1,3)
		self.window_width = window_width
		self.reset()
		
	def move(self):
		self.x -= self.speed
		if self.x < - self.image.get_width():
			self.x = self.window_width + random.randint(50, 200)
			self.y = random.randint(50,250)
			self.original_image = random.choice(self.images)
			new_size = (
                int(self.original_image.get_width() * 0.5),
                int(self.original_image.get_height() * 0.5),
            )
			self.image = pygame.transform.smoothscale(self.original_image, new_size)
			
	def reset(self):
		self.original_image = random.choice(self.images)
		self.x = random.randint(window_width, window_width + random.randint(100,200))
		self.y = random.randint(0,window_height - 100)
		
	def draw(self, window):
		window.blit(self.image, (self.x, self.y))

clouds = [Cloud(cloud_images, window_width, window_height) for _ in range(3)]

class Bullet:
	def __init__(self, image, window_width, window_height):
		self.image = image 
		self.window_width = window_width
		self.window_height = window_height
		self.reset()
		
	def move(self):
		self.x -= self.speed
		if self.x < - self.image.get_width():
			self.reset()
			
	def reset(self):
		self.x = self.window_width + random.randint(50,100)
		self.y = random.randint(50, self.window_height -200)
		self.speed = random.uniform(6, 15)
		
	def draw(self, window):
		window.blit(self.image,(self.x, self.y))
		
	def check_collision(self, bird_x, bird_y, bird_width, bird_height):
		bullet_rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
		bird_rect = pygame.Rect(bird_x, bird_y, bird_width, bird_height)
		return bullet_rect.colliderect(bird_rect)  
		
bullet = Bullet(bullet_image, window_width, window_height)

def flappygame(): 
	pygame.mixer.music.load("assets/trimbgm.mp3")
	pygame.mixer.music.play(-1)
	pygame.mixer.music.set_volume(0.1)
	
	your_score = 0
	horizontal = int(window_width/5) 
	vertical = int(window_width/2) 
	ground = 0
	mytempheight = 100

	first_pipe = createPipe() 
	second_pipe = createPipe() 

	down_pipes = [ 
		{'x': window_width+300-mytempheight, 
		'y': first_pipe[1]['y']}, 
		{'x': window_width+300-mytempheight+(window_width/2), 
		'y': second_pipe[1]['y']}, 
	] 

	up_pipes = [ 
		{'x': window_width+300-mytempheight, 
		'y': first_pipe[0]['y']}, 
		{'x': window_width+200-mytempheight+(window_width/2), 
		'y': second_pipe[0]['y']}, 
	] 

	pipeVelX = -4

	bird_velocity_y = -9
	bird_Max_Vel_Y = 10
	bird_Min_Vel_Y = -8
	birdAccY = 1

	bird_flap_velocity = -8
	bird_flapped = False
	bird_width = game_images['flappybird'].get_width()
	bird_height = game_images['flappybird'].get_height()
	
	while True: 
		for event in pygame.event.get(): 
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE): 
				pygame.quit() 
				sys.exit() 
			if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP): 
				if vertical > 0: 
					bird_velocity_y = bird_flap_velocity 
					bird_flapped = True

		game_over = isGameOver(horizontal, 
							vertical, 
							up_pipes, 
							down_pipes) 
		if game_over: 
			pygame.mixer.music.stop()
			sound_effects["gameover"].play()
			for cloud in clouds:
				cloud.reset()
			
			bullet.reset()
			return

		playerMidPos = horizontal + game_images['flappybird'].get_width()/2
		for pipe in up_pipes: 
			pipeMidPos = pipe['x'] + game_images['pipeimage'][0].get_width()/2
			if pipeMidPos <= playerMidPos < pipeMidPos + 4: 
				your_score += 1
				sound_effects["score"].set_volume(0.3)
				sound_effects["score"].play()
				print(f"Your your_score is {your_score}") 

		if bird_velocity_y < bird_Max_Vel_Y and not bird_flapped: 
			bird_velocity_y += birdAccY 

		if bird_flapped: 
			bird_flapped = False
		playerHeight = game_images['flappybird'].get_height() 
		vertical = vertical + min(bird_velocity_y, elevation - vertical - playerHeight) 

		for upperPipe, lowerPipe in zip(up_pipes, down_pipes): 
			upperPipe['x'] += pipeVelX 
			lowerPipe['x'] += pipeVelX 

		if 0 < up_pipes[0]['x'] < 5: 
			newpipe = createPipe() 
			up_pipes.append(newpipe[0]) 
			down_pipes.append(newpipe[1]) 

		if up_pipes[0]['x'] < -game_images['pipeimage'][0].get_width(): 
			up_pipes.pop(0) 
			down_pipes.pop(0) 

		window.blit(game_images['background'], (0, 0)) 
		
		for cloud in clouds:
			cloud.move()
			cloud.draw(window)
			
		bullet.move()
		bullet.draw(window)
			
		for upperPipe, lowerPipe in zip(up_pipes, down_pipes): 
			window.blit(game_images['pipeimage'][0], 
						(upperPipe['x'], upperPipe['y'])) 
			window.blit(game_images['pipeimage'][1], 
						(lowerPipe['x'], lowerPipe['y'])) 

		window.blit(game_images['sea_level'], (ground, elevation)) 
	

		numbers = [int(x) for x in list(str(your_score))] 
		width = 0

		for num in numbers: 
			width += game_images['scoreimages'][num].get_width() 
		Xoffset = window_width/2 - width/2

		for num in numbers: 
			score_img = game_images['scoreimages'][num].copy()
			score_img.set_alpha(150)
			window.blit(game_images['scoreimages'][num], 
						(Xoffset, window_height/2 - game_images['scoreimages'][num].get_height()/2 - 25 ) ) 
			Xoffset += game_images['scoreimages'][num].get_width()
			 
		window.blit(game_images['flappybird'], (horizontal, vertical)) 
		pygame.display.update() 
		framepersecond_clock.tick(framepersecond) 


def isGameOver(horizontal, vertical, up_pipes, down_pipes): 
	if vertical > elevation - 35 or vertical < 0: 
		return True

	for pipe in up_pipes: 
		pipeHeight = game_images['pipeimage'][0].get_height() 
		if(vertical < pipeHeight + pipe['y'] and abs(horizontal - pipe['x'] - 25) < game_images['pipeimage'][0].get_width()): 
			return True

	for pipe in down_pipes: 
		if (vertical + game_images['flappybird'].get_height() > pipe['y']) and abs(horizontal - pipe['x'] - 25) < game_images['pipeimage'][1].get_width(): 
			return True
		
	bird_width = game_images['flappybird'].get_width()
	bird_height = game_images['flappybird'].get_height()
	if bullet.check_collision(horizontal, vertical, bird_width, bird_height):
		return True   
	
	return False


def createPipe(): 
    offset = window_height / 3
    pipeHeight = game_images['pipeimage'][0].get_height()
    y2 = offset + random.randrange(
        0, int(window_height - game_images['sea_level'].get_height() - 1.2 * offset)
    ) 
    pipeX = window_width + 10
    y1 = pipeHeight - y2 + offset 

    return [
        {'x': pipeX, 'y': -y1},
        {'x': pipeX, 'y': y2}
    ]


if __name__ == "__main__": 

	framepersecond_clock = pygame.time.Clock() 

	pygame.display.set_caption('Flappy Bird Game') 

	game_images['scoreimages'] = []
	alphaVal = 50
	for i in range(10):
		img = pygame.image.load(f'images/{i}.png').convert_alpha()
		img.set_alpha(alphaVal)
		game_images['scoreimages'].append(img)
	
	game_images['flappybird'] = pygame.image.load( 
		birdplayer_image).convert_alpha() 
	game_images['sea_level'] = pygame.image.load( 
		sealevel_image).convert_alpha() 
	game_images['background'] = pygame.image.load( 
		background_image).convert_alpha()
	game_images['pipeimage'] = (pygame.transform.rotate(pygame.image.load( 
		pipeimage).convert_alpha(), 180), pygame.image.load( 
	pipeimage).convert_alpha()) 

	print("WELCOME TO THE FLAPPY BIRD GAME") 
	print("Press space or enter to start the game") 

	while True: 

		horizontal = int(window_width/5) 
		vertical = int( 
			(window_height - game_images['flappybird'].get_height())/2) 
		ground = 0
		while True: 
			for event in pygame.event.get(): 

				if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE): 
					pygame.quit() 
					sys.exit() 

				elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP): 
					flappygame() 

				else: 
					window.blit(game_images['background'], (0, 0)) 
					window.blit(game_images['flappybird'], 
								(horizontal, vertical)) 
					window.blit(game_images['sea_level'], (ground, elevation)) 
					pygame.display.update() 
					framepersecond_clock.tick(framepersecond) 
