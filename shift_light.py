#! /usr/bin/python
# Simple client program to read RPM data from the Realdash multicast stream and control a wd281x led strip as shift light  
import socket,os
import struct
import board
import neopixel_spi as neopixel
import signal

# Configuration
SHIFTRPM = 7000				# At what RPM doe you need to shift
GREEN    = 9				# Nr of green leds
ORANGE   = 4				# Nr of orange leds
RED      = 3 				# Nr of red leds
RANGE    = 0.3				# What part of the rev range does the shift light work on
SERVER   = ('localhost', 12345)       # Realdash instance to connect to
RPMID    = 37				# RPM id send from Realdash


# Global variables
nrLeds = GREEN + ORANGE + RED
ledsOn = 0

startRpm = SHIFTRPM - (SHIFTRPM * RANGE)
stepSize = SHIFTRPM * RANGE / nrLeds 

# Classes and functions
class SignalHandler:
  shutdown_requested = False

  def __init__(self):
    signal.signal(signal.SIGINT, self.request_shutdown)
    signal.signal(signal.SIGTERM, self.request_shutdown)

  def request_shutdown(self, *args):
    print('Request to shutdown received, stopping')
    self.shutdown_requested = True

  def can_run(self):
    return not self.shutdown_requested

def setLight(rpm):
  global ledsOn
  i = 0
  while i < nrLeds:
    if rpm > SHIFTRPM:
      if ledsOn == 0:
        pixels.fill((255, 255, 255))
        ledsOn = 1
      else:
        pixels.fill((0, 0, 0))
        ledsOn = 0
      break
    if rpm > (startRpm + (i * stepSize)):
      pixels[i] = (0, 255, 0)
      if i >= GREEN:
        pixels[i] = (255, 64, 5)
      if i >= GREEN + ORANGE:
        pixels[i] = (255, 0, 0)
    else:
      pixels[i] = (0, 0, 0)
    i += 1

# Set everything up
signalHandler = SignalHandler()
pixels = neopixel.NeoPixel_SPI(board.SPI(), nrLeds)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
sock.connect(SERVER)

# Main loop
while signalHandler.can_run():  
  buf = sock.recv(1024)  
  pair = [buf[i:i+8] for i in range(0, len(buf), 8)]
  i = 0
  while i < len(pair):
    id = int.from_bytes(pair[i][:4], "little")
    value = int(struct.unpack('<f', pair[i][4:8])[0])
    if(id == RPMID):
      setLight(value)
    i += 1
