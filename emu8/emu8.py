import chip8
import tui8
import argparse
import curses
import copy
from collections import deque


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
        0x14,
        # subroutine to print the value in register 1 and increment it
        0x00,  # clear display
        0xE0,
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
        0x18,
        0x22,  # loop is broken, call the subroutine
        0x06,
        0x12,  # reset delay timer and reloop
        0x14,
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


def update_keys(chip, tui, currPress):
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

    press = tui.inputWin.getch()

    # we account for a timeout becuase getch fails if it's called too quickly
    if press == -1:
        currPress[1] = currPress[1] - 1
    elif currPress[0] == chr(press):
        currPress[1] = 150
    else:
        currPress[0] = chr(press)
        currPress[1] = 150

    if currPress[1] == 0:
        currPress[0] = ""

    # update chip keys based on what's pressed
    for i, key in enumerate(keys):
        if key == currPress[0]:
            chip.keys[i] = True
        else:
            chip.keys[i] = False

def update_keys_debug(chip, tui, press):
    """toggle the chip's keys according to what's pressed on the keyboard"""
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

    # update chip keys based on what's pressed
    for i, key in enumerate(keys):
        if key == chr(press):
            chip.keys[i] = not chip.keys[i]


def run_chip(chip, tui, refreshrate, stdscr):
    """cycle the chip and update the display according to the refresh rate"""

    currPress = ["", 0] # initialize key press history to nothing

    while chip.get_curr_inst() != chip8.Chip.EXIT:

        screenUpdated = False
        for _ in range(refreshrate):

            # if we're going to write to the chip sceen, note it
            inst = chip.get_curr_inst()
            if inst >> 12 == 0xD:
                screenUpdated = True

            # run the chip and check for input
            update_keys(chip, tui, currPress) 
            chip.cycle()


        # if we're running the tui in fast mode,
        # don't update it unless draw has been called
        if not tui.compmode:
            if screenUpdated:
                tui.update()
        else:
            tui.update()

def run_debug(chip, tui, stdscr):
    """cycle the chip and update the display only when space is pressed"""

    states = deque() # copies of the chip at previous states, this eats a ton of memory
    while chip.get_curr_inst() != chip8.Chip.EXIT:

        press = tui.inputWin.getch()
        if press != -1:

            # step
            if press == ord(" "):
                states.append(copy.deepcopy(chip))
                chip.cycle()

            # go back 
            elif press == ord("z"):
                try:
                    chip = states.pop()
                    tui.chip = chip
                except: # if the states deque is empty, do nothing
                    pass

            # toggle chip keys 
            else:
                update_keys_debug(chip, tui, press)

            tui.update()


def init_argparse():
    """create an argument parser"""
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] (FILE)",
        description="Run a specified chip8 program or an included demo.",
    )
    parser.add_argument("-c", "--count", action="store_true", help="run the count demo")
    parser.add_argument("-3", "--three", action="store_true", help="run the 3 demo")
    parser.add_argument("-r", "--run", metavar="file", help="run the provided program")
    parser.add_argument(
        "-cs",
        "--clockspeed",
        metavar="Hz",
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
    parser.add_argument("-cm", "--comprehensive", action="store_true", help="run in comprehensive windowed mode")
    parser.add_argument("-db", "--debug", action="store_true", help="run in debug mode")

    return parser


def main(stdscr):
    """run a program on the chip8 depending on specified arguments"""

    # parse args
    parser = init_argparse()
    args = parser.parse_args()

    chip = chip8.Chip()

    if args.run:
        load_file(args.run, chip)
        chip.clockSpeed = args.clockspeed
    elif args.three:
        load_demo_3(chip)
        chip.clockSpeed = args.clockspeed
    # count is the default
    else:
        load_demo_count(chip)
        chip.clockSpeed = args.clockspeed

    curses.noecho()
    curses.cbreak()

    tui = tui8.Tui(stdscr, chip, compmode=args.comprehensive)
    tui.inputWin.nodelay(1)

    if args.debug:
        run_debug(chip, tui, stdscr)
    else:
        run_chip(chip, tui, args.refreshrate, stdscr)


if __name__ == "__main__":
    curses.wrapper(main)
