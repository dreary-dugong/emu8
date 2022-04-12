# emu8.py

A somewhat naive chip-8 interpreter/emulator written in Python with curses. 

This project was based on the spec outlined here:

https://web.archive.org/web/20220104155337/devernay.free.fr/hacks/chip8/C8TECH10.HTM


https://user-images.githubusercontent.com/85261881/163059170-61eb0703-d5b0-4725-a82b-f3a6362318f4.mp4


## Usage

The main method for the emulator is implemented in `emu8.py` which by default runs a program that counts up from 0, but can be made to run another program with one of the following three arguments:

- `-3` or `--three` : run the included "three" demo which just writes the digit 3 to the screen

- `-r <file>` or `--run <file>` : run a supplied chip-8 binary rom

There are also several optional arguments to set parameters for the emulator:

- `-cm` or `--comprehensive` : run in comprehensive windowed mode, displaying the register, memory, and description windows

- `-cl` or `--clockspeed` : set the clock speed in Hz (default is 500 as outlined in the spec). Note that the upper limit here depends on the host machine,
  but it's unlikely to reach beyond 2000 before throwing an exception for an instruction taking too long. 

- `-rf` or `--refreshrate` : set the number of cycles between screen refreshes (default is 10). Because writing to the screen takes time, setting this to a
lower value will noticably slow down the program. Higher values seem to have diminishing returns on speed after this point.

- `-db` or `--debug` : run the emulator in debug mode. See debug section.

## Display



https://user-images.githubusercontent.com/85261881/163062122-eeb86640-b43c-414b-a241-45fa697322d6.mp4



![emu8-demo-cm](https://user-images.githubusercontent.com/85261881/163059854-56e2f968-0ea7-469b-9ef2-eccffbfa1d47.png)


The terminal display includes 5 parts:

- The chip8 screen. This is 64x32 characters wherein each 'pixel' is represented by two spaces. 

- The keypad display. This displays which keys are pressed for the emulator as well as providing an outline for their expected positioning. 
(Note that the emulator maps the chip-8 keys directly to their character counterparts on the keyboard, despite being in a different position. 
 i.e., a maps to a and 0 maps to 0 even though they are not beside each other in qwerty.)

- The register display. Only present in comprehensive mode, this displays the contents of all general- and special-purpose registers. This is only displayed when running in comprehensive mode.

- The memory display. Only present in comprehensive mode, this displays 41 memory values, their addresses, and their corresponding assembly interpretation in order starting from 20 below the program counter and ending at 20 above the program counter. The "current" instruction (currently pointed to by the program counter, about to execute) is highlighted.

- The description display. Only present in comprehensive mode, this displays a highlighted English interpretation of the "current" instruction and the ones immediately before and after it. 

## Debug Mode

https://user-images.githubusercontent.com/85261881/163061951-b8eb659c-e26d-4838-8bad-a3869eaa034b.mp4

When supplied with the debug flag, the emulator will run in debug mode. In this mode, execution is halted until the user presses the spacebar, whereupon execution will continue for as long as the space bar is held. Additionally, key presses for the emulator are registered between space bar taps and are toggled rather than held. This allows multiple inputs to be toggled on at a time. Finally, execution can be reversed at any time by the use of the z button which returns the emulator to the state it was in before the most recently executed instruction. 

## Keyboard

In order to avoid requiring root access, the emulator uses the curses module for keyboard input. As a result, real-time input can be a bit quirky. A low keyboard 
repeat delay should be used if possible (350 ms was used in testing). There is also a short but unpredictable delay between when a user stops pressing a key and
that key being marked as not-pressed in the emulator. This can be tracked by observing the key value on screen. Finally, the emulator can only register a single
key press at a time unless running in debug mode. 


## Operating System

This project makes heavy use of the curses module and therefore is only verified to work properly on linux. Ostensibly, the ncurses module provides a drop-in 
replacement for Windows, but this has yet to be tested. 

