def setup():
    size(1900,1000) # sizing your canvas
    background(255,255,255)
    no_loop()

def draw():

    for row in range(13):
        y_pos_strip = row * (1000/13)
        drawStrips(y_pos_strip, row)
        
    fill(0,38,100)
    rect(0,0,760,(7000/13))
    
    for column in range(6):
        for row in range(5):
            x_pos = column * 126
            y_pos = row * 110
            drawStars(x_pos, y_pos);
            
    for column in range (5):
        for row in range (4):
            x_pos_1 = column * 127
            y_pos_1 = row * 108
            drawStars_1(x_pos_1, y_pos_1)

def drawStars(x_pos, y_pos):
    space = 20
    margin = 55
    r = random(255)
    g = random(255)
    b = random (255)
    fill(r, g, b)
    triangle(x_pos - space + margin,
             y_pos + space + margin,
             x_pos + margin,
             y_pos - space + margin,
             x_pos + space + margin,
             y_pos + space + margin)

def drawStars_1(x_pos_1,y_pos_1):
    space = 20
    margin = 108
    r = random(255)
    g = random(255)
    b = random (255)
    fill(r, g, b)
    triangle(x_pos_1 - space + margin,
             y_pos_1 + space + margin,
             x_pos_1 + margin,
             y_pos_1 - space + margin,
             x_pos_1 + space + margin,
             y_pos_1 + space + margin)

def drawStrips(y_pos_strip, row):
    if row % 2 > 0:
        fill(255,255,255)
    else:
        r = random(255)
        g = random(255)
        b = random (255)
        fill(r, g, b)
        
    rect(0, y_pos_strip, 1900, 1000/13)
    
run_sketch()
