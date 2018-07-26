# Dependencies
import board
import neopixel
import adafruit_irremote
import pulseio
import adafruit_fancyled.adafruit_fancyled as fancy

BRIGHTNESS_INCREMENT = 0.025
current_color = (255, 255, 255) # default color white
brightness = 0.025 # led default brightness
number_led_illuminated = 0
last_color = current_color

num_pixels = 10

pixels = neopixel.NeoPixel(board.NEOPIXEL, num_pixels, auto_write=False, brightness=1.0)
pulsein = pulseio.PulseIn(board.REMOTEIN, maxlen=120, idle_state=True)
decoder = adafruit_irremote.GenericDecode()

def brightness_up():
    global brightness
    brightness = brightness + BRIGHTNESS_INCREMENT
    if brightness > 1:
        brightness = 1.0
    print("Brightness increase", brightness)

def brightness_down():
    global brightness
    brightness = brightness - BRIGHTNESS_INCREMENT
    if brightness < BRIGHTNESS_INCREMENT:
        brightness = BRIGHTNESS_INCREMENT
    print("Brightness decrease")

def select_color(color):
    global current_color
    current_color = color
    print("Selected color:", color)

def more_leds():
    global number_led_illuminated
    number_led_illuminated += 1
    if number_led_illuminated > num_pixels:
        number_led_illuminated = num_pixels + 1
        
def less_leds():
    global number_led_illuminated
    number_led_illuminated -= 1
    if number_led_illuminated < 1:
        number_led_illuminated = 1

def on_off():
    global current_color, last_color
    if current_color == (0, 0, 0):
        current_color = last_color
        last_color = (0, 0, 0)
    else:
        last_color = current_color
        current_color = (0, 0, 0)
    
code_map = {  # button = color
    247: (255, 0, 0),  # 1 = red
    119: (255, 40, 0),  # 2 = orange
    183: (255, 150, 0),  # 3 = yellow
    215: (0, 255, 0),  # 4 = green
    87: (0, 255, 120),  # 5 = teal
    151: (0, 255, 255),  # 6 = cyan
    231: (0, 0, 255),  # 7 = blue
    103: (180, 0, 255),  # 8 = purple
    167: (255, 0, 20),  # 9 = magenta
    207: (255, 255, 255),  # 0 = white needs to be an RGBW value
    127: on_off,  # Play/Pause = off
    95: brightness_up,
    79: brightness_down,
    175: more_leds,
    239: less_leds
}

def remote_decoder():
  pulses = decoder.read_pulses(pulsein, max_pulse=2000)
  command = None
  try:
      code = decoder.decode_bits(pulses)
      if len(code) > 3:
          command = code[2]
  except adafruit_irremote.IRNECRepeatException:  # Catches the repeat signal
      pass
  except adafruit_irremote.IRDecodeException:  # Failed to decode
      pass
  if command is not None:
      action = code_map.get(command)
      if action is None:
          return
      if type(action) is tuple:
          select_color(action)
      else:
          action()

def update_pixels():
    for i in range(num_pixels):
        if i < number_led_illuminated - 1:
            pixels[i] = fancy.gamma_adjust(fancy.CRGB(*current_color), brightness=brightness).pack()
        else:
            pixels[i] = (0, 0, 0)
    pixels.write()
    
while True:
  remote_decoder()
  update_pixels()