#!/usr/bin/python3
import time
import RPi.GPIO as GPIO
from gpiozero import LED,Button
import signal
import sys
import os
import re
from stat import *
import subprocess
from collections import deque
import random

random.seed()

ORANGE=23
RED=18

bootdir1="1"
bootdir2="2"

#===============================================
# wiring diagram
#
#         3.3V    1 || 2     5V   Power red
#     run   P2    3 || 4     5V
#    clear  P3    5 || 6     GND  Power black
#    b16    P4    7 || 8     P14
#          GND    9 || 10    P15
#    b32   P17   11 || 12    P18  LED Orange
#    b64   P27   13 || 14    GND
#    rand  P22   15 || 16    P23  LED Red
#         3.3V   17 || 18    P24  b5
#     b10  P10   19 || 20    GND
#     b11  P9    21 || 22    P25  b6
#     b9   P11   23 || 24    P8   b7
#          GND   25 || 26    P7   b4
#     RESERVED   27 || 28    RESERVED
#     b8   P5    29 || 30    GND
#     b12  P6    31 || 32    P12  b2
#     b15 P13    33 || 34    GND
#     b14 P19    35 || 36    P16  b1
#     b13 P26    37 || 38    P20  b3
#         GND    39 || 40    P21  b0
#
# All buttons are configured with pull-up resistors except
# P2 and P3 which are hardwired with pull-ups.
#
# Buttons are grounded when closed.
#
#----------------------
# Default locations for stuff...

#player="/usr/bin/omxplayer"       # note - omxplayer not suitable for use
player="mpg321"                    # must install
script="/bin/bash"
volume_control="/usr/bin/amixer"

# to shutdown from main menu
# as regular user, need 'sudo chmod u+s /sbin/shutdown'

devnull=open(os.devnull,'w') 
running=False   

#--------------------
# stop functionality

def stopAll():
    # stop all sound sources
    global running
    global soundproc
    
    running=False
    runLEDoff()
    if (soundproc.poll() is None):
        soundproc.kill()
        soundprocstat=False

#---------------------------------------------------

def playfile (filenum):
    global devnull
    global soundproc
    global soundprocStat

    filename= audiodir+"/"+str(filenum)+".mp3"
    print ("play filename: %s\n" % (filename))
    soundproc=subprocess.Popen([player,filename],shell=False,stdout=devnull,stderr=devnull)
    soundprocStat=True


class Play:
    def __init__(self):
       self.queue=deque([])

    def number(self):
       return len(self.queue)

    def add(self,num):
        print ("Button: %d\n" % (num))
        return self.queue.append(num)

    def clearall(self):
        self.queue.clear()
        statusLEDoff()
        
    def playnext(self):
        try:
            nextfile=self.queue.popleft()
            playfile(nextfile)
            if (len(self.queue)==1):
                for x in range(2):   # alternate lights twice when one track left
                    statusLEDon()
                    runLEDoff()
                    time.sleep(.15)
                    statusLEDoff()
                    runLEDon()
                    time.sleep(.15)
            statusLEDon()
            runLEDon()
            
        except IndexError:
            running=False
            for x in range(3):   # flash both lights 3 times
                statusLEDoff()
                runLEDoff()
                time.sleep(.15)
                statusLEDon()
                runLEDon()
                time.sleep(.15)
            statusLEDoff()
            runLEDoff()

playqueue=Play()

soundproc=subprocess.Popen([volume_control,"cset","numid=1","94%"],stdout=devnull,shell=False)   # set up volume, 80% by default
soundprocStat=False
boost=False

#--------------------
# stop/run button callback

def stopRunCB(button):
    value=button.value

    global running

    if (value==0):
       # print ("Stop!\n")
       stopAll()
       running=False
       runLEDoff()
    else:
       # print ("Run!\n")
        if(playqueue.number()==0):
            running=False
        else:
            running=True
            playqueue.playnext()
        
def doQueueLight():
    if (playqueue.number()>0):
        GPIO.output(ORANGE,1);
    else:
        GPIO.output(ORANGE,0);


# add queue callback----------------------------------------
#
# unfortunately, gpiozero doesn't allow data to
# be passed into the callback, so we have to map
# the button to the action here.

def addqueue(button):
    pin=button.pin.number
    additional=0

    # flash orange LED 4 times fast
    
    for x in range(4):
        statusLEDoff()
        time.sleep(.05)
        statusLEDon()
        time.sleep(.05)
    
    if (b16.value==1):
        additional+=16
    if (b32.value==1):
        additional+=32
    if (b64.value==1):
        additional+=64

    # print ("pin %d additional %d \n" % (pin,additional))
        
    if (pin==22):
        r=random.randint(0,127)
        playqueue.add(r);
    if (pin==21):
        playqueue.add(0+additional)
    if (pin==16):
        playqueue.add(1+additional)
    if (pin==12):
        playqueue.add(2+additional)
    if (pin==20):
        playqueue.add(3+additional)
        
    if (pin==7):
        playqueue.add(4+additional)
    if (pin==24):
        playqueue.add(5+additional)
    if (pin==25):
        playqueue.add(6+additional)
    if (pin==8):
        playqueue.add(7+additional)
        
    if (pin==5):
        playqueue.add(8+additional)
    if (pin==11):
        playqueue.add(9+additional)
    if (pin==10):
        playqueue.add(10+additional)
    if (pin==9):
        playqueue.add(11+additional)
        
    if (pin==6):
        playqueue.add(12+additional)
    if (pin==26):
        playqueue.add(13+additional)
    if (pin==19):
        playqueue.add(14+additional)
    if (pin==13):
        playqueue.add(15+additional)
  
# Configure all buttons


GPIO.setmode(GPIO.BCM)
inputpins={21,20,16,12,7,8,25,24,22,10,5,11,9,26,19,13,6,4,17,27,22}
outputpins={ORANGE,RED}

for pin in inputpins:
  GPIO.setup(pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)

# do not need to do pins 2 and 3: they are hard wired
  
for pin in outputpins:
  GPIO.setup(pin,GPIO.OUT)

# bottom bank buttons
  
b0=Button(21)
b0.when_pressed=addqueue
b1=Button(16)
b1.when_pressed=addqueue
b2=Button(12)
b2.when_pressed=addqueue
b3=Button(20)
b3.when_pressed=addqueue

# second bank

b4=Button(7)
b4.when_pressed=addqueue
b5=Button(24)
b5.when_pressed=addqueue
b6=Button(25)
b6.when_pressed=addqueue
b7=Button(8)
b7.when_pressed=addqueue

# third bank

b8=Button(5)
b8.when_pressed=addqueue
b9=Button(11)
b9.when_pressed=addqueue
b10=Button(10)
b10.when_pressed=addqueue
b11=Button(9)
b11.when_pressed=addqueue

# fourth bank

b12=Button(6)
b12.when_pressed=addqueue
b13=Button(26)
b13.when_pressed=addqueue
b14=Button(19)
b14.when_pressed=addqueue
b15=Button(13)
b15.when_pressed=addqueue

# handle the special latched buttons

b16=Button(4)
b32=Button(17)
b64=Button(27)

# do the random button

brandom=Button(22,hold_time=1.5,hold_repeat=True)
brandom.when_pressed=addqueue
brandom.when_held=addqueue

# and the run and clear buttons

brun=Button(3)
bclear=Button(2)

brun.when_pressed=stopRunCB
brun.when_released=stopRunCB
bclear.when_pressed=playqueue.clearall

redPWM=GPIO.PWM(RED,100)
redPWM.start(0)
redPWM.ChangeDutyCycle(100)  # reset this whenever off
# not that DutyCycle overrides on/off

if (GPIO.input(4)):
    audiodir=bootdir2
else:
    audiodir=bootdir1
    
    
def runLEDon ():
    GPIO.output(RED,1)

def runLEDoff ():
    GPIO.output(RED,0)
    redPWM.ChangeDutyCycle(0)  # reset this whenever off

def statusLEDon ():
    GPIO.output(ORANGE,1)

def statusLEDoff ():
    GPIO.output(ORANGE,0)
    
# with (HALT and CONT) signals

def suspendSoundProc():
        os.kill(soundproc.pid,signal.SIGSTOP)

def resumeSoundProc():
        os.kill(soundproc.pid,signal.SIGCONT)

# flash LEDs indicating boot up

for x in range(10):
    runLEDon()
    statusLEDon()
    time.sleep(.05)
    runLEDoff()
    statusLEDoff()
    time.sleep(.05)
statusLEDoff()
runLEDoff()

#--------------------
# main loop

while True:
    blink=False
    time.sleep(.25)

    # orange light (play queue status)

    doQueueLight()
    # red light (running status)
         
    if (soundproc.poll() is None):
        runLEDon()
        soundprocStat=True
        if (running):
          if (blink):
              blink=False
              redPWM.ChangeDutyCycle(100)
          else:
              redPWM.ChangeDutyCycle(50)
              blink=True
        else:
            runLEDoff()
            soundprocStat=False

    
