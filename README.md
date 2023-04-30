This project is now changed from Teensy 2.0++ to Raspberry Pi 3B.
Why?
The Teensy works great, and has much more I/O then a Raspberry Pi but
the DFRobot parts: the DFPlayer Pro is particularly a garbage product
that does not reliably play low-bitrate files without random stuttering.

So, the solution is to use an RPi. It has barely enough I/O to handle the 
buttons (24 pins total). This leaves no room for expansion.

See pin diagram in the comments. There are:
18 momentary buttons
4 latched buttons 
2 LEDs




