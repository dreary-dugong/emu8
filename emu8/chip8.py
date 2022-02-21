import random
import time


class Chip:
    # class constants
    CLOCK_SPEED = 500
    # default clock speed in Hz
    DIGIT_MEM_INDEX = 0
    # where in memory are the sprite reprs of digits
    PROGRAM_MEM_INDEX = 512
    # where is program space in memory
    RAM_SIZE = 4096
    # total bytes of ram
    DISPLAY_X_MAX = 63
    # one less than the width of the display
    DISPLAY_Y_MAX = 31
    # one less than the height of the display
    EXIT = 0
    # instruction that ends program execution

    def __init__(self):

        # memory
        self.mem = [0] * Chip.RAM_SIZE
        # main memory, each entry is one byte
        self.pc = Chip.PROGRAM_MEM_INDEX
        # program counter

        # registers
        self.regs = [0] * 16
        # general purpose registers
        self.regI = 0
        # "I" register

        # stack
        self.stack = [0] * 16
        # stack of return addresses for subroutines
        self.sp = 0
        # stack pointer

        # timers
        self.dt = 0
        # delay timer register, decreases to 0 at 60Hz
        self.st = 0
        # sound timer registser, decreases to 0 at 60Hz
        # plays a sound as it decrmeents

        # display
        # this would be read by a driver class to display on screen
        self.load_display()

        # keys
        # these have to be set by a driver class
        self.keys = [False] * 16

        # initial memory values
        self.load_digit_sprites()

        # number of cycles run so far, used for timing
        self.cycleCount = 0

        # set clock speed to default
        self.clockSpeed = Chip.CLOCK_SPEED

    def load_display(self):
        """load the display as an empty matrix"""
        # TODO: bigger display sizes? check roms for what they expect
        self.disp = []  # 2D boolean matrix representing the 63 x 32 display
        for _ in range(Chip.DISPLAY_X_MAX + 1):
            self.disp.append([False] * (Chip.DISPLAY_Y_MAX + 1))

    def load_digit_sprites(self):
        """load the sprite reprentations of digits into memory for use
        in drawing instructions"""

        digit0 = (0xF0, 0x90, 0x90, 0x90, 0xF0)
        digit1 = (0x20, 0x60, 0x20, 0x20, 0x70)
        digit2 = (0xF0, 0x10, 0xF0, 0x80, 0xF0)
        digit3 = (0xF0, 0x10, 0xF0, 0x10, 0xF0)
        digit4 = (0x90, 0x90, 0xF0, 0x10, 0x10)
        digit5 = (0xF0, 0x80, 0xF0, 0x10, 0xF0)
        digit6 = (0xF0, 0x80, 0xF0, 0x90, 0xF0)
        digit7 = (0xF0, 0x10, 0x20, 0x40, 0x40)
        digit8 = (0xF0, 0x90, 0xF0, 0x90, 0xF0)
        digit9 = (0xF0, 0x90, 0xF0, 0x10, 0xF0)
        digitA = (0xF0, 0x90, 0xF0, 0x90, 0x90)
        digitB = (0xE0, 0x90, 0xE0, 0x90, 0xE0)
        digitC = (0xF0, 0x80, 0x80, 0x80, 0xF0)
        digitD = (0xE0, 0x90, 0x90, 0x90, 0xE0)
        digitE = (0xF0, 0x80, 0xF0, 0x80, 0xF0)
        digitF = (0xF0, 0x80, 0xF0, 0x80, 0x80)

        digits = (
            digit0
            + digit1
            + digit2
            + digit3
            + digit4
            + digit5
            + digit6
            + digit7
            + digit8
            + digit9
            + digitA
            + digitB
            + digitC
            + digitD
            + digitE
            + digitF
        )

        self.load_mem(Chip.DIGIT_MEM_INDEX, digits)

    def load_mem(self, offset, vals):
        """load the values from an iterable into subsequent memory
        locations. This is just memcpy."""
        index = offset
        for val in vals:
            self.mem[index] = val
            index += 1

    def display_byte(self, x, y, b):
        """set 'pixels' in the display according to a byte"""
        ow = False
        y = y % Chip.DISPLAY_Y_MAX

        for i in range(8):
            p = b & (1 << (7 - i))  # isolate our bit
            p = p >> (7 - i)  # shift our bit all the way right for 1 or 0
            currx = (x + i) % Chip.DISPLAY_X_MAX  # wrap around

            # are we overwritiing a previous sprite?
            if not p and self.disp[currx][y]:
                ow = True

            self.disp[currx][y] = True if p != self.disp[currx][y] else False

        return ow

    def load_program(self, vals):
        """exposed method for loading a program into memory"""
        self.__init__()
        # reset everything
        # TODO: this resets clock speed, maybe it shouldn't
        index = Chip.PROGRAM_MEM_INDEX
        for val in vals:
            self.mem[index] = val
            index += 1

    def run(self):
        """run all instructions in program memory"""
        # TODO: for now, we treat 0 as exit. Is that correct?
        while self.mem[self.pc] != Chip.EXIT:
            self.cycle()

    def cycle(self):
        """run a single instruction with proper timing"""
        inst = self.mem[self.pc]  # first byte
        inst = inst << 8  # shift over to make room for second byte
        inst = inst + self.mem[self.pc + 1]  # add second byte

        start = time.time()
        self.execute(inst)
        end = time.time()

        elapsed = end - start
        time.sleep((1 / self.clockSpeed) - elapsed)
        self.cycleCount += 1

        # decrement timers every 8 cycles. This is ~60Hz when
        # clock speed is 500 Hz
        if self.cycleCount % 8 == 0:
            self.dt = max(0, self.dt - 1)
            self.st = max(0, self.st - 1)

    def execute(self, inst):
        """execute a single 16-bit integer instruction on the chip"""
        # TODO: is it worthwhile to save the decoder dictionaries as instance
        # data so we don't reload them every cycle?

        # if we're at an exit code, don't do anything
        if inst == Chip.EXIT:
            return

        # instructions with no params
        no_params = {0x00E0: self.CLS, 0x00EE: self.RET}
        if inst in no_params:
            no_params[inst]()
            return

        # instructions with a single 12 bit param (address)
        prefix = inst >> 12  # first 4 bits encode instruction type
        addr = inst & 0x0FFF  # last 12 bits encode param

        addr_param = {0x1: self.JP, 0x2: self.CALL, 0xA: self.LDI, 0xB: self.JP0}
        if prefix in addr_param:
            addr_param[prefix](addr)
            return

        # instructions with a 4-bit param (register) and 8-bit param (literal)
        reg = addr >> 8
        # middle 4 bits encode register
        val = addr & 0x0FF
        # last 8 bits encode literal byte

        reg_val_params = {
            0x3: self.SEval,
            0x4: self.SNEval,
            0x6: self.LDval,
            0x7: self.ADDval,
            0xC: self.RND,
        }
        if prefix in reg_val_params:
            reg_val_params[prefix](reg, val)
            return

        # instructions with a single 4-bit param (register)
        postfix = val
        # what was a literal value before is now a postfix
        reg_params = {
            (0xE, 0x9E): self.SKP,
            (0xE, 0xA1): self.SKNP,
            (0xF, 0x07): self.LDregdt,
            (0xF, 0x0A): self.LDkey,
            (0xF, 0x15): self.LDdt,
            (0xF, 0x18): self.LDst,
            (0xF, 0x1E): self.ADDi,
            (0xF, 0x29): self.LDdigit,
            (0xF, 0x33): self.LDbcd,
            (0xF, 0x55): self.LDmemreg,
            (0xF, 0x65): self.LDregmem,
        }

        if (prefix, postfix) in reg_params:
            reg_params[(prefix, postfix)](reg)
            return

        # instructions with two 4-bit parameters (registers)
        reg1 = reg  # rename since there's now 2 registers
        reg2 = postfix >> 4  # second param is third set of 4 bits
        postfix = postfix & 0x0F
        # now the postfix is only 4 bits

        reg_reg_params = {
            (0x5, 0x0): self.SEreg,
            (0x8, 0x0): self.LDreg,
            (0x8, 0x2): self.AND,
            (0x8, 0x3): self.XOR,
            (0x8, 0x4): self.ADDreg,
            (0x8, 0x5): self.SUB,
            (0x8, 0x6): self.SHR,
            (0x8, 0x7): self.SUBN,
            (0x8, 0xE): self.SHL,
            (0x8, 0x1): self.OR,
            (0x9, 0x0): self.SNEreg,
        }

        if (prefix, postfix) in reg_reg_params:
            reg_reg_params[(prefix, postfix)](reg1, reg2)
            return

        # instructions with 3 4-bit parameters (two registers, one 'nibble')
        nibble = postfix
        if prefix == 0xD:
            self.DRW(reg1, reg2, nibble)
            return

        # if it hasn't been decoded yet, it doesn't exist
        raise (Exception(f"Bad instruction: {inst}"))

    def CLS(self):
        """instruction to clear the display"""
        self.load_display()
        self.pc += 2

    def RET(self):
        """instruction to return from a subroutine"""
        self.pc = self.stack[self.sp]
        self.sp -= 1
        self.pc += 2

    def JP(self, addr):
        """instruction to jump to addresss addr"""
        self.pc = addr

    def CALL(self, addr):
        """instruction to call a subroutine at address addr"""
        self.sp += 1
        self.stack[self.sp] = self.pc
        self.pc = addr

    def SEval(self, reg, val):
        """instruction to skip the next instruction if a register is val"""
        if self.regs[reg] == val:
            self.pc += 4
        else:
            self.pc += 2

    def SNEval(self, reg, val):
        """instruction to skip the next instruction if reg is not val"""
        if self.regs[reg] != val:
            self.pc += 4
        else:
            self.pc += 2

    def SEreg(self, reg1, reg2):
        """instruction to skip to the next instruction if the value in
        reg 1 is the same as the value in reg 2"""
        if self.regs[reg1] == self.regs[reg2]:
            self.pc += 4
        else:
            self.pc += 2

    def LDval(self, reg, val):
        """instruction to load a value into a register"""
        self.regs[reg] = val
        self.pc += 2

    # TODO: should this account for a carry?
    def ADDval(self, reg, val):
        """instruction to add a value to a register"""
        self.regs[reg] = (self.regs[reg] + val) & 255
        self.pc += 2

    def LDreg(self, reg1, reg2):
        """instruction to load the value from one register into another"""
        self.regs[reg1] = self.regs[reg2]
        self.pc += 2

    def OR(self, reg1, reg2):
        """instruction to bitwise or two registers and store the result"""
        self.regs[reg1] = self.regs[reg1] | self.regs[reg2]
        self.pc += 2

    def AND(self, reg1, reg2):
        """instruction to bitwise and two registers and store the result"""
        self.regs[reg1] = self.regs[reg1] & self.regs[reg2]
        self.pc += 2

    def XOR(self, reg1, reg2):
        """instruction to bitwise xor two registers and store the result"""
        self.regs[reg1] = self.regs[reg1] ^ self.regs[reg2]
        self.pc += 2

    def ADDreg(self, reg1, reg2):
        """instruction to add the values in two registers and store the
        result"""
        self.regs[reg1] = self.regs[reg1] + self.regs[reg2]

        if self.regs[reg1] > 255:
            self.regs[15] = 1
            # set carry flag
            self.regs[reg1] = self.regs[reg1] & 255  # keep 8-bit limit
        else:
            self.regs[15] = 0

        self.pc += 2

    def SUB(self, reg1, reg2):
        """instruction to subtract the value of one register from another"""
        if self.regs[reg1] > self.regs[reg2]:
            self.regs[15] = 1
        else:
            self.regs[15] = 0

        self.regs[reg1] = self.regs[reg1] - self.regs[reg2]
        self.regs[reg1] = self.regs[reg1] & 255
        #  this fixes unsigned 8-bit subtraction

        self.pc += 2

    def SHR(self, reg, empty):
        """instruction to divide the value of a register by 2"""
        # this is listed as taking two registers but it only operates on one
        self.regs[15] = self.regs[reg] % 2
        # if it was odd, set the flag
        self.regs[reg] = self.regs[reg] // 2
        self.pc += 2

    def SUBN(self, reg1, reg2):
        """instruction to subtract the value of one register from another
        but in reverse"""
        self.regs[15] = self.regs[reg2] > self.regs[reg1]
        # set flag?
        self.regs[reg1] = self.regs[reg2] - self.regs[reg1]
        # subtract
        self.regs[reg1] = self.regs[reg1] & 255
        # limit to 8 bits
        self.pc += 2

    def SHL(self, reg, empty):
        """instruction to multiply the value in a register by 2"""
        # this is classified as taking two registers but only operates on
        # one
        self.regs[15] = self.regs[reg] > 127
        # set flag
        self.regs[reg] = self.regs[reg] * 2
        # multiply
        self.regs[reg] = self.regs[reg] & 255
        # limit to 8 bits
        self.pc += 2

    def SNEreg(self, reg1, reg2):
        """instruction to skip the next instruction if two registers
        are not equal"""
        if self.regs[reg1] != self.regs[reg2]:
            self.pc += 4
        else:
            self.pc += 2

    def LDI(self, addr):
        """insruction to set the I register to a given address"""
        self.regI = addr
        self.pc += 2

    def JP0(self, addr):
        """instruction to jump to the instruction at addr + the value
        in register 0"""
        self.pc = addr + self.regs[0]

    def RND(self, reg, b):
        """instruction to generate a random byte, bitwise and it with a given
        byte and store the result"""
        r = random.randint(0, 255)
        self.regs[reg] = r & b
        self.pc += 2

    def DRW(self, reg1, reg2, n):
        """instruction to draw a sprite on the display"""
        x, y = self.regs[reg1], self.regs[reg2]
        index = self.regI
        ow = False

        for i in range(n):
            b = self.mem[index]
            if self.display_byte(x, y + i, b):
                ow = True
            index += 1

        if ow:
            self.regs[15] = 1

        self.pc += 2

    def SKP(self, reg):
        """instruction to skip the next instruction if the key corresponding
        to the value in a given register is pressed"""
        key = self.regs[reg]
        if self.keys[key]:
            self.pc += 4
        else:
            self.pc += 2

    def SKNP(self, reg):
        """instruction to skip the next instruction if the key corresponding
        to the value in a given register is not pressed"""
        key = self.regs[reg]
        if not self.keys[key]:
            self.pc += 4
        else:
            self.pc += 2

    def LDregdt(self, reg):
        """instruction to load the value in the delay timer into a
        register"""
        self.regs[reg] = self.dt
        self.pc += 2

    def LDkey(self, reg):
        """instruction to load the value of the next key press into a
        register"""
        # TODO: should we check for a press or a change in state?
        if not any(self.keys):  # do nothing, let it be reexeucted
            return
        else:
            self.regs[reg] = self.keys.index(True)
            self.pc += 2

    def LDdt(self, reg):
        """instruction to load the value from a register into the delay
        timer"""
        self.dt = self.regs[reg]
        self.pc += 2

    def LDst(self, reg):
        """instruction to load the value from a register into the sound
        timer"""
        self.st = self.regs[reg]
        self.pc += 2

    def ADDi(self, reg):
        """instruction to add the value in a register to the I register"""
        self.regI += self.regs[reg]
        self.regI = self.regI & (2 ** 12 - 1)  # maintain 12 bits
        self.pc += 2

    def LDdigit(self, reg):
        """instruction to set the I register to the memory address of the
        sprite for the value in a given register"""
        val = self.regs[reg]
        self.regI = Chip.DIGIT_MEM_INDEX + 5 * val
        self.pc += 2

    def LDbcd(self, reg):
        """instruction to store the decimal representation of the value in
        a register in the memory addresses directly after the i register"""
        val = self.regs[reg]

        hundreds = val // 100
        val -= 100 * hundreds
        tens = val // 10
        val -= 10 * tens
        ones = val

        self.mem[self.regI] = hundreds
        self.mem[self.regI + 1] = tens
        self.mem[self.regI + 2] = ones

        self.pc += 2

    def LDmemreg(self, reg):
        """instruction to store the values in registers 0 - x in memory
        starting at the value in the I register"""
        loc = self.regI
        for r in range(0, reg + 1):  # TODO: should be inclusive?
            self.mem[loc] = self.regs[r]
            loc += 1
        self.pc += 2

    def LDregmem(self, reg):
        """instruction to load values from memory starting at the address
        pointed to by the I register into registers 0 to x"""
        loc = self.regI
        for r in range(0, reg + 1):  # TODO: should be inclusive?
            self.regs[r] = self.mem[loc]
            loc += 1
        self.pc += 2


def main():
    chip = Chip()
    chip.LDkey(0)
    print(chip.regs[0])


if __name__ == "__main__":
    main()
