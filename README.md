# emu8.py

A naive chip-8 interpreter/emulator written in Python with curses. 

This project was based on the spec outlined here:

https://web.archive.org/web/20220104155337/devernay.free.fr/hacks/chip8/C8TECH10.HTM

## Usage

The main method for the emulator is implemented in `emu8.py` which requires one of the following three arguments:

- `-3` or `--three` : run the included "three" demo which just writes the digit 3 to the screen

- `-c` or `--count` : run the included "count" demo which writes the hexidecimal digits 0-15 on the screen in order with ~1 second between each.

- `-r <file>` or `--run <file>` : run a supplied chip-8 binary rom

There are also a number of optional arguments to set parameters for the emulator:

- `-cl` or `--clockspeed` : set the clock speed in Hz (default is 500 as outlined in the spec). Note that the upper limit here depends on the host machine,
  but it's unlikely to reach beyond 2000 before throwing an exception for an instruction taking too long. 

- `-rf` or `--refreshrate` : set the number of cycles between screen refreshes (default is 10). Because writing to the screen takes time, setting this to a
lower value will noticably slow down the program. Higher values seem to have diminishing returns on speed after this point.

- `-db` or `--debug` : run the emulator in debug mode. The program counter will only progress to the next instruction when the user presses the space bar.

## Display

The terminal display includes 4 parts:

- The chip8 screen. This is 64x32 characters wherein each 'pixel' is represented by two spaces. 

- The register display. This displays the contents of all general- and special-purpose registers at all times.

- The keypad display. This displays which keys are pressed for the emulator at all times as well as providing an outline for their expected positioning. 
(Note that the emulator maps the chip-8 keys directly to their character counterparts on the keyboard, despite being in a different position. 
 i.e., a maps to a and 0 maps to 0 even though they are not beside each other in qwerty.)

- The memory display. This displays 23 memory values and their addresses in order, starting from 11 below the program counter and ending at 11 above the program 
counter. There is a blue carrot ('^') beneath the address of the current program counter. 

## Keyboard

In order to avoid requiring root access, the emulator uses the curses module for keyboard input. As a result, real-time input can be a bit quirky. A low keyboard 
repeat delay should be used if possible (350 ms was used in testing). There is also a short but unpredictable delay between when a user stops pressing a key and
that key being marked as not-pressed in the emulator. This can be tracked by observing the key value on screen. Finally, the emulator can only register a single
key press at a time. 

## Operating System

This project makes heavy use of the curses module and therefore is only verified to work properly on linux. Ostensibly, the ncurses module provides a drop-in 
replacement for Windows, but this has yet to be tested. 

