import pygame
import random
import sys
import math
import os
import numpy as np
from array import array
import cv2
import mediapipe as mp

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("pogogogo")
clock = pygame.time.Clock()

EMOJI_NAMES = ["boom", "fire", "dash", "star", "zap", "earth_asia","skull_and_crossbones"]
ALL_EMOJIS = []
for name in EMOJI_NAMES:
    try:
        original_img = pygame.image.load(f"emojis/{name}.png").convert_alpha()
        ALL_EMOJIS.append((name, original_img))
    except Exception as e:
        print(f"image loading error: {name}.png -> {e}")

C_MAJOR_SCALE = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88]

def generate_sine(freq, duration=0.3, volume=0.3):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array('h')
    for i in range(n_samples):
        val = int(32767 * volume * math.sin(2 * math.pi * freq * i / sample_rate))
        buf.append(val)
    return pygame.mixer.Sound(buffer=buf)

def generate_drum(freq=100, duration=0.15, volume=0.5):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array('h')
    for i in range(n_samples):
        env = 1.0 - i / n_samples
        val = int(32767 * env * math.sin(2 * math.pi * freq * i / sample_rate))
        buf.append(val)
    return pygame.mixer.Sound(buffer=buf)

def generate_kick_drum(freq=60, duration=0.2, volume=0.7):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array('h')
    
    for i in range(n_samples):
        env = math.exp(-5.0 * i / n_samples)
        current_freq = freq * (1 - 0.5 * i / n_samples)
        val = int(32767 * volume * env * math.sin(2 * math.pi * current_freq * i / sample_rate))
        buf.append(val)
    
    return pygame.mixer.Sound(buffer=buf)

def generate_hihat(duration=0.1, volume=0.3):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array('h')
    
    for i in range(n_samples):
        env = math.exp(-10.0 * i / n_samples)
        val = int(32767 * volume * env * (random.random() * 2 - 1))
        buf.append(val)
    
    return pygame.mixer.Sound(buffer=buf)

sound_map = {
    "boom": [generate_drum(90), generate_drum(120)],
    "fire": [generate_sine(freq) for freq in C_MAJOR_SCALE[0:4]],
    "dash": [generate_sine(freq) for freq in C_MAJOR_SCALE[2:6]],
    "star": [generate_sine(freq) for freq in C_MAJOR_SCALE[4:]],
    "zap":  [generate_sine(freq*2) for freq in C_MAJOR_SCALE[3:]],
    "earth_asia": [generate_sine(freq/2) for freq in C_MAJOR_SCALE],
    "skull_and_crossbones": [generate_drum(70, duration=0.3, volume=0.8), generate_drum(40, duration=0.4, volume=0.9)]
}

kick_drum = generate_kick_drum()
hihat = generate_hihat()

class Particle:
    def __init__(self, x, y, emoji_data):
        self.x = x
        self.y = y
        self.emoji_name, original_emoji = emoji_data
        self.size = random.randint(32, 96)
        self.emoji = pygame.transform.scale(original_emoji, (self.size, self.size))
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(2, 5)
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed
        self.life = 60
        self.alpha = 255
        self.sound_played = False
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1
        self.alpha = max(0, self.alpha - 4)
        self.rotation += self.rotation_speed

        if not self.sound_played and self.life == 50:
            sounds = sound_map[self.emoji_name]
            sound = random.choice(sounds)
            pan = self.x / 800
            channel = sound.play()
            if channel:
                channel.set_volume(1 - pan, pan)
            
            if self.emoji_name == "star":
                extra = random.choice(sounds)
                ch2 = extra.play()
                if ch2:
                    ch2.set_volume(pan, 1 - pan)

            self.sound_played = True

    def draw(self, surface):
        if self.rotation != 0:
            rotated = pygame.transform.rotate(self.emoji, self.rotation)
            rot_rect = rotated.get_rect(center=(self.x + self.size/2, self.y + self.size/2))
            rotated.set_alpha(self.alpha)
            surface.blit(rotated, rot_rect)
        else:
            temp = self.emoji.copy()
            temp.set_alpha(self.alpha)
            surface.blit(temp, (self.x, self.y))

particles = []
first_burst = True

def create_explosion(x, y, count=20):
    emoji_choices = random.sample(ALL_EMOJIS, min(random.randint(2, 4), len(ALL_EMOJIS)))
    for _ in range(count):
        emoji = random.choice(emoji_choices)
        particles.append(Particle(x, y, emoji))

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]

NOSE_TIP = 4
NOSE_BOTTOM = 94
CHIN = 152
LEFT_TEMPLE = 162
RIGHT_TEMPLE = 389
FOREHEAD = 10

head_position_history = []
HEAD_HISTORY_MAX = 10
NOD_THRESHOLD = 0.03
SHAKE_THRESHOLD = 0.025
last_drum_time = 0
MIN_DRUM_INTERVAL = 300

USE_CAMERA = True
try:
    cap = cv2.VideoCapture(0)
    ret, test_frame = cap.read()
    if not ret or not cap.isOpened():
        print("摄像头无法正常工作，将使用普通背景模式")
        USE_CAMERA = False
    else:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
except Exception as e:
    print(f"摄像头初始化失败: {e}")
    USE_CAMERA = False

last_left_eye = None
last_right_eye = None
eye_move_threshold = 15

running = True
while running:
    if USE_CAMERA:
        ret, frame = cap.read()
        if not ret:
            print("无法获取摄像头画面，切换到普通背景模式")
            USE_CAMERA = False
            screen.fill((255, 255, 255))
        else:
            frame = cv2.flip(frame, 1)
            
            frame = cv2.resize(frame, (800, 600))
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            results = face_mesh.process(rgb_frame)
            
            pygame_frame = pygame.image.frombuffer(frame.tobytes(), frame.shape[1::-1], "BGR")
            
            screen.blit(pygame_frame, (0, 0))
            
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                landmarks = face_landmarks.landmark
                
                left_eye_x = int(landmarks[LEFT_EYE_INDICES[0]].x * 800)
                left_eye_y = int(landmarks[LEFT_EYE_INDICES[0]].y * 600)
                
                right_eye_x = int(landmarks[RIGHT_EYE_INDICES[0]].x * 800)
                right_eye_y = int(landmarks[RIGHT_EYE_INDICES[0]].y * 600)
                
                if last_left_eye is not None and last_right_eye is not None:
                    left_eye_move = math.sqrt((left_eye_x - last_left_eye[0])**2 + (left_eye_y - last_left_eye[1])**2)
                    right_eye_move = math.sqrt((right_eye_x - last_right_eye[0])**2 + (right_eye_y - last_right_eye[1])**2)
                    
                    if left_eye_move > eye_move_threshold:
                        create_explosion(left_eye_x, left_eye_y, count=12)
                    
                    if right_eye_move > eye_move_threshold:
                        create_explosion(right_eye_x, right_eye_y, count=12)
                
                last_left_eye = (left_eye_x, left_eye_y)
                last_right_eye = (right_eye_x, right_eye_y)
                
                nose_tip = (landmarks[NOSE_TIP].x, landmarks[NOSE_TIP].y)
                forehead = (landmarks[FOREHEAD].x, landmarks[FOREHEAD].y)
                left_temple = (landmarks[LEFT_TEMPLE].x, landmarks[LEFT_TEMPLE].y)
                right_temple = (landmarks[RIGHT_TEMPLE].x, landmarks[RIGHT_TEMPLE].y)
                
                head_position_history.append(nose_tip)
                if len(head_position_history) > HEAD_HISTORY_MAX:
                    head_position_history.pop(0)
                
                if len(head_position_history) >= 5:
                    vertical_movement = max([abs(p[1] - head_position_history[0][1]) for p in head_position_history[1:]])
                    horizontal_movement = max([abs(p[0] - head_position_history[0][0]) for p in head_position_history[1:]])
                    
                    current_time = pygame.time.get_ticks()
                    time_since_last_drum = current_time - last_drum_time
                    
                    if vertical_movement > NOD_THRESHOLD and horizontal_movement < NOD_THRESHOLD and time_since_last_drum > MIN_DRUM_INTERVAL:
                        kick_drum.play()
                        create_explosion(int(nose_tip[0] * 800), int(nose_tip[1] * 600), count=15)
                        last_drum_time = current_time
                        
                        head_position_history = []
                    
                    elif horizontal_movement > SHAKE_THRESHOLD and vertical_movement < SHAKE_THRESHOLD and time_since_last_drum > MIN_DRUM_INTERVAL:
                        hihat.play()
                        create_explosion(int(left_temple[0] * 800), int(nose_tip[1] * 600), count=8)
                        create_explosion(int(right_temple[0] * 800), int(nose_tip[1] * 600), count=8)
                        last_drum_time = current_time
                        
                        head_position_history = []
    else:
        screen.fill((255, 255, 255))

        if first_burst:
            create_explosion(400, 300, count=30)
            first_burst = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
            mx, my = event.pos
            create_explosion(mx, my, count=6)
        elif not USE_CAMERA and event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            create_explosion(mx, my, count=6)
    
    for p in particles[:]:
        p.update()
        p.draw(screen)
        if p.life <= 0 or p.alpha <= 0:
            particles.remove(p)
    
    pygame.display.flip()
    clock.tick(60)

if USE_CAMERA:
    cap.release()
    face_mesh.close()
pygame.quit()
sys.exit()