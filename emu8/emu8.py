#!/bin/python3

import chip8
from colorama import Back, Fore
import os
import argparse
import keyboard


def load_demo_3(chip):
    """load a simple 'hello, world' style program for testing"""
    # the following should write a "3" to the display
    program = (
        0x62,  # load the value 0 into register 2
        0x00,
        0x63,  # load the value 0 into register 3
        0x00,
        0x61,  # load the value 3 into register 1
        0x03,
        0xF1,  # load sprite for value of register 1 into I
        0x29,
        0xD2,  # write sprite to screen at coordinstes stored in 2 and 3
        0x35,
    )
    chip.load_program(program)


def load_demo_count(chip):
    """load an counting program into the chip for testing the display"""
    # the chip should count up from 0 to F, then reset
    program = (
        # program constants
        0x62,  # load the value 0 into register 2
        0x00,
        0x63,  # load the value 0 into register 3
        0x00,
        # jump to execution
        0x12,  # jump to 530 in memory (18 bytes ahead of the start)
        0x12,
        # subroutine to print the value in register 1 and increment it
        0xF1,  # load sprite for value into I pointer
        0x29,
        0xD2,  # write sprite in I pointer to screen at constant coord
        0x35,
        0x71,  # add 1 to r1
        0x01,
        0x41,  # if our value isn't 16, skip to exit
        0x10,
        0x61,  # otherwise, reset to 0
        0x00,
        0x00,  # exit subroutine
        0xEE,
        # loop delay and redrawing
        0x64,  # load 64 into register 4
        0x40,
        0xF4,  # load register 4 into DT (delay timer)
        0x15,
        # loop checking the value in the delay timer until it's 0
        0xF5,  # load delay timer value into regiser 5
        0x07,
        0x35,  # if register 5 is 0, break the loop
        0x00,
        0x12,  # jump back to check delay timer again
        0x16,
        0x22,  # loop is broken, call the subroutine
        0x06,
        0x12,  # reset delay timer and reloop
        0x12,
    )
    chip.load_program(program)


def load_file(f, chip):
    """read a raw program in from a file and load it into the chip"""

    program = []
    with open(f, "rb") as file:
        for byteArray in file:
            for byte in byteArray:
                program.append(byte)

    chip.load_program(program)


def update_keys(chip):
    """set the chip's keys according to what's pressed on the keyboard"""
    keys = (
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
    )
    for i, key in enumerate(keys):
        chip.keys[i] = keyboard.is_pressed(key)


def get_screen(chip):
    """get a stylized text representation of the chip-8's display"""

    # transpose the display so it's right-side up
    display = []
    for y in range(32):
        display.append([0] * 64)
    for x, column in enumerate(chip.disp):
        for y, val in enumerate(column):
            display[y][x] = val

    # add colored characters to output string
    output = ""
    for row in display:
        for val in row:
            if val:
                output += Back.GREEN + "  "
            else:
                output += Back.RESET + "  "
        output += Back.RESET + "\n"

    return output


def get_stylized_registers(chip):
    """return a stylized string representation of the registers"""
    output = ""

    for i in range(4):
        for j in range(4):
            n = j + 4 * i
            output += f"r{hex(n)[2]}:  {double_hex(chip.regs[n])} \t"
        output += "\n"

    output += "\n"
    output += f"I:{hex(chip.regI)}\t\t\t"
    output += f"dt:{hex(chip.dt)}\t\t\t"
    output += f"st:{hex(chip.st)}\n"

    return output


def get_stylized_mem(chip):
    """return a stylized string representation of the chip's  memory"""
    distance = 12  # distance away from the program counter to display

    valueRow = []  # row of values in memory
    addrRow = []  # row of memory addresses
    arrowRow = []  # row with an arrow to the current instruction

    for i in range(chip.pc - distance, chip.pc + distance):
        if i >= 0 and i < len(chip.mem):
            valueRow.append(double_hex(chip.mem[i]) + "  ")
        else:
            valueRow.append(double_hex(0) + "  ")
        addrRow.append(triple_hex(i) + " ")

        if i == chip.pc:
            arrowRow.append(Fore.BLUE + "^" + Fore.RESET)
        else:
            arrowRow.append("     ")

    return "\n" + "".join(valueRow) + "\n" + "".join(addrRow) + "\n" + "".join(arrowRow)


def get_stylized_keys(chip):
    """return a stylized string representation of which keys are pressed on the chip"""
    keys = (
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
    )
    output = "\n"
    for key, value in zip(keys, chip.keys):
        if value:
            output += Back.WHITE + Fore.BLACK + key + Back.RESET + Fore.RESET + "\t"
        else:
            output += key + "\t"

    return output


def double_hex(n):
    """return a two digit hex representation of an integer"""
    h = hex(n)
    if len(h) == 3:
        h = h[:2] + "0" + h[2]
    return h


def triple_hex(n):
    """return a three digit hex representation of an integer"""
    h = double_hex(n)
    if len(h) == 4:
        h = h[:2] + "0" + h[2:]
    return h


def text_display(chip):
    """display an interface to the chip in the terminal"""
    os.system("clear")
    display = (
        get_screen(chip)
        + get_stylized_registers(chip)
        + get_stylized_mem(chip)
        + get_stylized_keys(chip)
    )
    print(display)


def run_display(chip, rf):
    """run the program on the chip and display contents in the terminal"""
    currInst = (chip.mem[chip.pc] << 8) + chip.mem[chip.pc + 1]
    while currInst != chip8.Chip.EXIT:
        currInst = (chip.mem[chip.pc] << 8) + chip.mem[chip.pc + 1]
        for _ in range(rf):
            update_keys(chip)
            chip.cycle()
        text_display(chip)


def init_argparse():
    """create an argument parser"""
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] (FILE)",
        description="Run a specified chip8 program or an included demo.",
    )
    parser.add_argument("-c", "--count", action="store_true", help="run the count demo")
    parser.add_argument("-3", "--three", action="store_true", help="run the 3 demo")
    parser.add_argument("-r", "--run", metavar="file", help="run the prvoided program")
    parser.add_argument(
        "-cs",
        "--clockspeed",
        metavar="speed",
        type=int,
        help="set the clock speed in Hz (default 500)",
        default=500,
    )
    parser.add_argument(
        "-rf",
        "--refreshrate",
        metavar="cycles",
        type=int,
        default=10,
        help="""set the number of cycles between
            screen refreshes (default 10)""",
    )

    return parser


def main():
    """run a program on the chip8 depending on specified arguments"""
    parser = init_argparse()
    args = parser.parse_args()

    chip = chip8.Chip()

    if args.three:
        load_demo_3(chip)
        chip.clockSpeed = args.clockspeed
        run_display(chip, args.refreshrate)
    elif args.count:
        load_demo_count(chip)
        chip.clockSpeed = args.clockspeed
        run_display(chip, args.refreshrate)
    elif args.run:
        load_file(args.run, chip)
        chip.clockSpeed = args.clockspeed
        run_display(chip, args.refreshrate)
    else:
        print("incorrect arguments, use --help for help")


if __name__ == "__main__":
    main()
