from adafruit_display_text import bitmap_label as label
from adafruit_macropad import MacroPad
import displayio
import terminalio
import time
import random

macropad = MacroPad()

main_group = displayio.Group()
main_group.scale = 2
macropad.display.root_group = main_group
score_label = label.Label(
    y=4,
    font=terminalio.FONT,
    color=0xFFFFFF
)
lives_label = label.Label(
    y=14,
    font=terminalio.FONT,
    color=0xFFFFFF
)
speed_label = label.Label(
    y=24,
    font=terminalio.FONT,
    color=0xFFFFFF
)
main_group.append(score_label)
main_group.append(lives_label)
main_group.append(speed_label)

game_over = displayio.Group()
game_over.scale = 2
game_over_label = label.Label(
    anchor_point=(.5, .5),
    anchored_position=(32, 16),
    font=terminalio.FONT,
    color=0xFFFFFF,
    text="GAME OVER"
)
game_over.append(game_over_label)

press_to_start = displayio.Group()
press_to_start.scale = 2
press_to_start_label = label.Label(
    anchor_point=(1, .5),
    anchored_position=(64, 16),
    font=terminalio.FONT,
    color=0xFFFFFF,
    text="   Press\n     -->\nto start",
    line_spacing = .7
)
press_to_start.append(press_to_start_label)

last_pixel_time = 0
tone_start = -1
score = 0
lives = 3
speed = 1

def update_score():
    global score_label
    global score
    score_label.text = "Score: " + str(score)

def update_lives():
    global lives_label
    global lives
    lives_label.text = "Lives: " + ("X" * lives)

def update_speed():
    global speed_label
    global speed
    speed_label.text = "Speed: " + str(speed)

update_score()
update_lives()
update_speed()
while True:
    new_speed = max(macropad.encoder + 1, 1)
    if not new_speed == speed:
        speed = new_speed
        update_speed()

    if lives <= 0:
        macropad.display.root_group = game_over
        macropad.stop_tone()
        time.sleep(.5)
        macropad.play_tone(466, .5)
        macropad.play_tone(440, .5)
        macropad.play_tone(415, .5)
        macropad.play_tone(392, .5)
        
        score = 0
        lives = 3
        update_score()
        update_lives()
        macropad.pixels.fill((0, 0, 0))
        macropad.display.root_group = press_to_start

        while not macropad.encoder_switch:
            time.sleep(.1)
        
        macropad.display.root_group = main_group

    while True:
        event = macropad.keys.events.get()
        if event:
            if event.pressed:
                key_value = macropad.pixels[event.key_number][0]
                if key_value > 0:
                    score = score + 1
                    update_score()
                    macropad.pixels[event.key_number] = (0, 255, 0)
                    macropad.start_tone(1000)
                    tone_start = time.monotonic()
                else:
                    lives = lives - 1
                    update_lives()
                    macropad.start_tone(200)
                    tone_start = time.monotonic()
        else:
            break

    if  time.monotonic() - tone_start > .2:
        macropad.stop_tone()
    
    for i, pixel in enumerate(macropad.pixels):
        if pixel[0] > 0:
            macropad.pixels[i] = (max(0, pixel[0]-speed), 0, 0)
        if pixel[1] > 0:
            macropad.pixels[i] = (0, max(0, pixel[1]-speed), 0)
    
    now = time.monotonic()
    if (now - last_pixel_time > .5):
        pixel = random.randint(0, 11)
        macropad.pixels[pixel] = (255, 0, 0)
        last_pixel_time = now
