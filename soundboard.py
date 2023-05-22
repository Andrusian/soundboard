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

bootdir1="/home/dave/1"
bootdir2="/home/dave/2"
bootdir3="/home/dave/3"
bootdir4="/home/dave/4"

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
# Note: both run and clear buttons are now momentary with
# long debounce times.
#
#----------------------
# Default locations for stuff...

#player="/usr/bin/omxplayer"       # note - omxplayer not suitable for use
player="mpg321"                    # must install
script="/bin/bash"

# to shutdown from main menu
# as regular user, need 'sudo chmod u+s /sbin/shutdown'

devnull=open(os.devnull,'w') 
running=False   

#-----------------------------------------------------
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


#---class for the play queue ---------------------

class Play:
    def __init__(self):
       self.queue=deque([])

    def number(self):
       return len(self.queue)

    def add(self,num):
        print ("Add: %d\n" % (num))
        return self.queue.append(num)

    def clearall(self):
        self.queue.clear()
        statusLEDoff()
        
    def playnext(self):
        try:
            nextfile=self.queue.popleft()
            print ("Play next: %s\n" % (nextfile))
        except IndexError:
            for x in range(3):   # flash both lights 3 times
                statusLEDoff()
                runLEDoff()
                time.sleep(.15)
                statusLEDon()
                runLEDon()
                time.sleep(.15)
            statusLEDoff()
            runLEDoff()
            print ("queue empty\n");
            running=False
            return False

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
        return True

playqueue=Play()

# set up volume
# RPi has terrible audio output so we are using a separate 3W amp to boost
# if set too high, you'll get noise on the output
#
# Note also that RPi volume control is non-linear.
# 95% in amixer should yield max volume in in alsamixer
#
# The RPi output is also noisy due to being cheap. There is some discussion about this online
# but the solution of doing raspi-update to install corrected firmware
# makes no difference.
 
soundproc=subprocess.Popen(["amixer","cset","numid=1","95%"],stdout=devnull,shell=False)  
soundprocStat=False
boost=False

#---------------------------------------------------------------
# stop/run button callbacks

def RunCB(button):
    global running

    # print ("Run!\n")
    running=True
    running=playqueue.playnext()

def StopCB(button):
    stopAll()
    running=False
    runLEDoff()
       
#---------------------------------------------------------------

def doQueueLight():
    if (playqueue.number()>0):
        GPIO.output(ORANGE,1);
    else:
        GPIO.output(ORANGE,0);


# track button callback----------------------------------------
#
# unfortunately, gpiozero doesn't allow data to
# be passed into the callback, so we have to map
# the button to the action here.

def addqueue(button):
    pin=button.pin.number
    additional=0
    global running

    # switch mode if clear plus a bottom row pushed

    if ((bclear.is_pressed) and (b0.is_pressed)):
      audiodir==bootdir1
      playqueue.clearall
      print ("mode change 1\n")
      return

    if ((bclear.is_pressed) and (b1.is_pressed)):
      audiodir==bootdir2   
      playqueue.clearall
      print ("mode change 2\n")
      return

    if ((bclear.is_pressed) and (b2.is_pressed)):
      audiodir==bootdir3   
      playqueue.clearall
      print ("mode change 3\n")
      return

    if ((bclear.is_pressed) and (b3.is_pressed)):
      audiodir==bootdir4   
      playqueue.clearall
      print ("mode change 4\n")
      return
    
    # flash orange LED 4 times fast
    
    for x in range(2):
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
        # random track chooser
        # which mode are we in?
        if (audiodir==bootdir1):
            n=random.randint(0,5)
            r=random.randint(0,64)
            if (n==4):    # 20% chance
                track=64+r
            else:
                track=r
        else:
            track=random.randint(0,128)
        playqueue.add(track)
        
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

    # we know there should be something in the playqueue
    # but if the run button is pressed and something is
    # queued, we should automatically start playing it
    #
    # If we are already running, we don't need to do anything
        
    if (brun.is_pressed==True):
        if (running==False):
            running=True
            running=playqueue.playnext()


#---------------------------------------------------------------
        
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

brun=Button(3, bounce_time=.5)
bclear=Button(2)

brun.when_pressed=RunCB
brun.when_released=StopCB
bclear.when_pressed=playqueue.clearall

redPWM=GPIO.PWM(RED,100)
redPWM.start(0)
redPWM.ChangeDutyCycle(100)  # reset this whenever off
# not that DutyCycle overrides on/off

audiodir=bootdir1  # default
    
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

#-----------------------------------------------------------------
# main program

blink=0

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

# main loop...

while True:
    time.sleep(.2)

    # orange light (play queue status)

    doQueueLight()
    # red light (running status)

    if (running==True):
        if (soundproc.poll() is None):
            runLEDon()
            soundprocStat=True
            if (running):
              blink=blink+1
              if (blink==0):
                  redPWM.ChangeDutyCycle(100)
              elif (blink==4):
                  redPWM.ChangeDutyCycle(50)
              if (blink>8):
                  blink=0
              else:
                  blink=0
            else:
                runLEDoff()
                soundprocStat=False
        else:
            print ("Next track\n")
            for x in range(2):
               runLEDoff()
               time.sleep(.05)
               runLEDon()
               statusLEDon()
               time.sleep(.05)
            success=playqueue.playnext()
            if (success==False):
                running=False

    
