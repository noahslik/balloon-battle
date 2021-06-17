import RPi.GPIO as GPIO
import pygame
import time
import sys

GPIO.setwarnings(False)

button_balloon = 20
button_left = 16
button_right = 12
led = 26

# MOTOR GPIO PINS
left_motor = [2,3,4,17]
right_motor = [9,10,22,27]

# BUTTON GPIO PINS
buttons = [button_right,button_left,button_balloon]

# PYGAME INIT
pygame.init()
pygame.mixer.init()

# CONTROLLER INIT
j = pygame.joystick.Joystick(0)
j.init()

# AUDIO INIT
mission_failed = pygame.mixer.Sound("/home/pi/gpio-music-box/samples/mission_failed.wav")
oof_sound = pygame.mixer.Sound("/home/pi/gpio-music-box/samples/oof_sound.wav")

######################
##   MOTOR CONFIG   ##
######################

half_seq = [
        [1,0,0,1],
        [1,0,0,0],
        [1,1,0,0],
        [0,1,0,0],
        [0,1,1,0],
        [0,0,1,0],
        [0,0,1,1],
        [0,0,0,1]]

half_reverse = half_seq[::-1]

#####################
##      SETUP      ##
#####################

def do_setup():
  GPIO.setmode(GPIO.BCM)

  GPIO.setup(left_motor, GPIO.OUT)
  GPIO.output(left_motor, 0)

  GPIO.setup(right_motor, GPIO.OUT)
  GPIO.output(right_motor, 0)

  GPIO.setup(buttons, GPIO.IN)

  GPIO.setup(led, GPIO.OUT)

######################
##     MOVEMENT     ##
######################

def forward():
  do_setup()
  for _ in range(12):
    for half_step in range(8):
      for pin in range(4):
        GPIO.output(left_motor[pin], half_reverse[half_step][pin])
        GPIO.output(right_motor[pin], half_reverse[half_step][pin])
      time.sleep(0.001)
  GPIO.cleanup()

def backwards():
  do_setup()
  for _ in range(12):
    for half_step in range(8):
      for pin in range(4):
        GPIO.output(left_motor[pin], half_seq[half_step][pin])
        GPIO.output(right_motor[pin], half_seq[half_step][pin])
      time.sleep(0.001)
  GPIO.cleanup()

def left():
  do_setup()
  for _ in range(12):
    for half_step in range(8):
      for pin in range(4):
        GPIO.output(left_motor[pin], half_seq[half_step][pin])
        GPIO.output(right_motor[pin], half_reverse[half_step][pin])
      time.sleep(0.001)
  GPIO.cleanup()

def right():
  do_setup()
  for _ in range(12):
    for half_step in range(8):
      for pin in range(4):
        GPIO.output(left_motor[pin], half_reverse[half_step][pin])
        GPIO.output(right_motor[pin], half_seq[half_step][pin])
      time.sleep(0.001)
  GPIO.cleanup()

def hit_left():
  for _ in range(15):
    backwards()
  for _ in range(30):
    right()

def hit_right():
  for _ in range(15):
    backwards()
  for _ in range(30):
    left()

######################
##      CHECK       ##
######################

def has_balloon():
  do_setup()
  if GPIO.input(button_balloon) == 0:
    return True
  else:
    return False
  GPIO.cleanup()

def check_hit_left():
  do_setup()
  if GPIO.input(button_left) == 0:
    GPIO.cleanup()
    return True
  else:
    GPIO.cleanup()
    return False
  
def check_hit_right():
  do_setup()
  if GPIO.input(button_right) == 0:
    GPIO.cleanup()
    return True
  else:
    GPIO.cleanup()
    return False

######################
##        LED       ##
######################

def light_on():
  do_setup()
  GPIO.output(led,GPIO.HIGH)
  GPIO.cleanup()

def light_off():
  do_setup()
  GPIO.output(led,GPIO.LOW)
  GPIO.cleanup()

######################
##       MAIN       ##
######################

def main():
  light_off()
  try:
    while True:
      events = pygame.event.get()
      if (j.get_button(0)):
        break
    while has_balloon():
      events = pygame.event.get()
      forward()
      if j.get_button(4):
        left()
      if j.get_button(5):
        right()
      if check_hit_left():
        oof_sound.play()
        light_on()
        hit_left()
        light_off()
        continue
      elif check_hit_right():
        oof_sound.play()
        light_on()
        hit_right()
        light_off()
        continue
    mission_failed.play()
    while check_hit_left() == False and check_hit_right() == False:
      events = pygame.event.get()
      forward()
      if j.get_button(4):
        left()
      if j.get_button(5):
        right()
    GPIO.cleanup()
    time.sleep(12)
  except KeyboardInterrupt:
    j.quit()
    pygame.quit()
    GPIO.cleanup()
    
if __name__ == "__main__":
  main()
