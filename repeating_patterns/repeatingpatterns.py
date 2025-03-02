from turtle import *
import turtle
# from theme import set_theme
import random

speed(0)
tracer(False)
turtle.ht()

pen_colors = ["#1c732c", "#8B4513", "#228B22", "#FF4500", "#2E8B57", "#6B8E23"]
bg_colors = ["#f0adef", "#FFE4B5", "#ADD8E6", "#FFFACD", "#E6E6FA", "#F5DEB3"]

emoji = ["🍎", "🍏", "🍊", "🍋", "🍇", "🍉", "🍌", "🍍", "🍎", "🍏", "🍊", "🍋", "🍇", "🍉", "🍌", "🍍"]

def grow(length, decrease, angle, noise = 0):
    if length > 10:
        width(length / 10)
        forward(length)
        if random.random() < 0.05:
            current_pos = position()
            current_heading = heading()
            penup()
            backward(random.uniform(0, length/2))
            left(10)
            random_emoji = random.choice(emoji)
            write(random_emoji, font = ("Arial", random.randint(10,25), "bold") )
            goto(current_pos)
            setheading(current_heading)    
            pendown()

        new_length = length * decrease
        if noise > 0:
            new_length += random.uniform(0.9,1.3)

        angle_l = angle + random.gauss(0, noise)
        angle_r = angle + random.gauss(0, noise)

        left(angle_l)
        grow(new_length, decrease, angle, noise)
        right(angle_l)

        right(angle_r)
        grow(new_length, decrease, angle, noise)
        left(angle_r)
        backward(length)
        
def draw_tree():
    penup()
    goto(0, -400)
    pendown()
    setheading(90)
    grow(170, 0.73, 19,10)

def refresh(x,y):
    clearscreen()
    speed(0)
    tracer(False)
    turtle.ht()
    pencolor(random.choice(pen_colors))
    bgcolor(random.choice(bg_colors))
    draw_tree()
    turtle.onscreenclick(refresh)
    tracer(True)
draw_tree()

turtle.onscreenclick(refresh)
tracer(True)
done()