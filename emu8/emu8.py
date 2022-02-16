import chip8
from colorama import Back
import os

def program_test(chip):
    """load a simple 'hello, world' style program for testing"""
    #the following should write a "3" to the display
    program = ( 
            0x65, #load the value 16 into register 5, just to test
            0xFF,

            0x62, #load the value 0 into register 2
            0x00,
            0x63, #load the value 0 into register 3
            0x00,
            0x61, #load the value 3 into register 1
            0x03,
            0xF1, #load sprite for value of register 1 into I
            0x29,
            0xD2, #write sprite to screen at coordinstes stored in 2 and 3
            0x35
            )
    chip.load_program(program)

def load_animation(chip):
    """load an animation program into the system for testing the display"""
    
    #the system should count up from 0 to F, then reset
    program = (
            #program constants
            0x62, #load the value 0 into register 2
            0x00, 
            0x63, #load the value 0 into register 3
            0x00, 

            #jump to execution
            0x12, #jump to 530 in memory (18 bytes ahead of the start)
            0x12,
            
            #subroutine to print the value in register 1 and increment it
            0xF1, #load sprite for value into I pointer
            0x29,
            0xD2, #write sprite in I pointer to screen at constant coord
            0x35,
            0x71, #add 1 to r1
            0x01,
            0x41, #if our value isn't 16, skip to exit
            0x10,
            0x61, #otherwise, reset to 0
            0x00,
            0x00, #exit subroutine
            0xEE,

            #loop delay and redrawing
            0x64, #load 64 into register 4
            0x40,
            0xF4, #load register 4 into DT (delay timer)
            0x15,

            #loop checking the value in the delay timer until it's 0
            0xF5, #load delay timer value into regiser 5
            0x07,
            0x35, #if register 5 is 0, break the loop 
            0x00,
            0x12, #jump back to check delay timer again
            0x16,
            0x22, #loop is broken, call the subroutine
            0x06,
            0x12, #reset delay timer and reloop
            0x12
            )
    chip.load_program(program)

def get_screen(chip):
    """get a stylized text representation of the chip-8's display"""

    #transpose the display so it's right-side up
    display = []
    for y in range(32):
        display.append([0]*64)
    for x, column in enumerate(chip.disp):
        for y, val in enumerate(column):
            display[y][x] = val

    #add colored characters to output string
    output = ""
    for row in display:
        for val in row:
            if val:
                output += (Back.GREEN + "  ")
            else:
                output += (Back.RESET + "  ")
        output += (Back.RESET + "\n")

    return output

def get_stylized_registers(chip):
    """return a stylized string representation of the registers"""
    output = ""

    for i in range(4):
        for j in range(4):
            n = j + 4*i
            output += f"r{hex(n)[2]}:\t{hex(chip.regs[n])}  \t"
        output += "\n"

    return output


def text_display(chip):
    """display an interface to the chip in the terminal"""
    os.system('clear')
    display = get_screen(chip) + get_stylized_registers(chip)
    print(display)


def main():
    """run our countdown program and display in the terminal"""
    chip = chip8.Chip()
    load_animation(chip)
    while True:
        for i in range(10): #update the screen every 10 cycles
            chip.cycle()
        text_display(chip)


if __name__ == "__main__":
    main()
