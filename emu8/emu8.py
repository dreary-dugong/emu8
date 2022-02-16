import chip8

def program_test(chip):
    #the following should write a "3" to the display
    program = ( 
            0x65FF, #load the value 16 into register 5, just to test

            0x6200, #load the value 0 into register 2
            0x6300, #load the value 0 into register 3
            0x6103, #load the value 3 into register 1
            0xF129, #load sprite for value of register 1 into I
            0xD235 #write sprite to screen at coordinstes stored in 2 and 3
            )
    chip.load_program(program)
    chip.run()

def text_display(chip):

    display = []
    for y in range(32):
        display.append([0]*64)

    for x, column in enumerate(chip.disp):
        for y, val in enumerate(column):
            display[y][x] = val

    print(chip.regs)
    print(chip.mem[512:600])

    output = ""
    for row in display:
        for val in row:
            output += "#" if val else "."
        output += "\n"
    print(output)

def main():
    chip = chip8.Chip();
    program_test(chip)
    text_display(chip)


if __name__ == "__main__":
    main()
