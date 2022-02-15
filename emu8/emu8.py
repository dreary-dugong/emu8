import random;

class Chip:
    #class constants
    DIGIT_MEM_INDEX = 0; #where in memory are the sprite reprs of digits


    def __init__(self):

        #memory
        self.mem = [0] * 4096; #main memory, each entry is one byte
        self.pc = 512; #program counter
                #program space is expected to start 512 bytes in

        #registers
        self.regs = [0]*16; #general purpose registers
        self.regI = 0; #"I" register
        self.regVF = 0; #"VF" register, usually used a flag

        #stack
        self.stack = [0]*16; #stack of return addresses for subroutines
        self.sp = 0; #stack pointer

        #timers
        self.dt = 0; #delay timer register, decreases to 0 at 60Hz
        self.st = 0; #sound timer registser, decreases to 0 at 60Hz
                #plays a sound as it decrmeents

        #display
        #this would be read by a driver class to display on screen
        self.load_display();

        #keys 
        #these have to be set by a driver class
        self.key0 = False
        self.key1 = False
        self.key2 = False
        self.key3 = False
        self.key4 = False
        self.key5 = False
        self.key6 = False
        self.key7 = False
        self.key8 = False
        self.key9 = False
        self.keyA = False
        self.keyB = False
        self.keyC = False
        self.keyD = False
        self.keyE = False
        self.keyF = False

        #initial memory values
        self.load_digit_sprites();
        
    def load_display(self):
        """load the display as an empty matrix"""
        #TODO: bigger display sizes? check roms for what they expect
        self.disp = [] #2D boolean matrix representing the 63 x 32 display
        for _ in range(64):
            disp.append([0]*32)

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

        digits = (digit0 + digit1 + digit2 + digit3 + digit4 + digit5 
                + digit6 + digit7 + digit8 + digit9 + digitA + 
                digits + digitB + digitC + digitD + digitE + digitF)

        self.load_mem(Chip8.DIGIT_MEM_INDEX, digits)

    def load_mem(self, offset, vals):
        """load the values from an iterable into subsequent memory
        locations. This is just memcpy."""
        index = offset
        for val in vals:
            self.mem[index] = val
            index += 1

    def execute(inst):
        """execute a single 16-bit integer instruction on the chip"""
        #TODO: refactor to use dictionaries and first class functions

        #instructions with no params
        if inst == 0x00E0:
            self.CLS();
            return;
        elif inst == 0x00EE:
            self.RET();
            return;

        #instructions with a single 12 bit param (address)
        prefix = inst >> 12; #first 4 bits encode instruction type
        addr = inst & 0x0FFF; #last 12 bits encode param
        if prefix == 0x1:
            self.JP(addr);
            return;
        elif prefix == 0x2:
            self.CALL(addr);
            return;
        elif prefix == 0xA:
            self.LDI(addr);
            return;
        elif prefix == 0xB:
            self.JP0(addr);
            return;

        #instructions with a 4-bit param (register) and 8-bit param (literal)
        reg = addr >> 8; #middle 4 bits encode register
        val = addr & 0x0FF; #last 8 bits encode literal byte
        if prefix == 0x3:
            self.SEval(reg, val);
            return;
        elif prefix == 0x4:
            self.SNEval(reg, val);
            return;
        elif prefix == 0x6:
            self.LDval(reg, val);
            return;
        elif prefix == 0x7:
            self.ADDval(reg, val);
            return;
        elif prefix == 0xC:
            self.RND(reg, val);
            return;

        #instructions with a single 4-bit param (register)
        postfix = val;
        if prefix == 0xE:
            if postfix == 0x9E:
                self.SKP(reg);
                return;
            elif postfix == 0xA1:
                self.SKNP(reg);
                return;
        elif prefix == 0xF:
            if postfix == 0x07:
                self.LDregdt(reg);
                return;
            elif postfix == 0x0A:
                self.LDkey(reg);
                return;
            elif postfix == 0x15:
                self.LDdt(reg);
                return;
            elif postfix == 0x18:
                self.LDst(reg);
                return;
            elif postfix == 0x1E:
                self.ADDi(reg);
                return;
            elif postfix == 0x29:
                self.LDdigit(reg);
                return;
            elif postfix == 0x33:
                self.LDbcd(reg);
                return;
            elif postfix == 0x55:
                self.LDmemreg(reg);
                return;
            elif postfix == 0x65:
                self.LDregmem(reg);
                return;

        #instructions with two 4-bit parameters (registers)
        reg1 = reg #rename since there's now 2 registers
        reg2 = postfix >> 4 #second param is third set of 4 bits
        postfix = postfix & 0x0F; #now there's an extra 4 bits on the end
        
        if prefix == 0x5:
            if postfix == 0x0:
                self.SEreg(reg1, reg2);
                return;
        elif prefix == 0x8:
            if postfix == 0x0:
                self.LDreg(reg1, reg2);
                return;
            elif postfix == 0x1:
                self.OR(reg1, reg2);
                return;
            elif postfix == 0x2:
                self.AND(reg1, reg2);
                return;
            elif postfix == 0x3:
                self.XOR(reg1, reg2);
                return;
            elif postfix == 0x4:
                self.ADDreg(reg1, reg2);
                return;
            elif posfix == 0x5:
                self.SUB(reg1, reg2);
                return;
            elif postfix == 0x6:
                self.SHR(reg1); #this is weird but it's in the spec
                return;
            elif postfix == 0x7:
                self.SUBN(reg1, reg2);
                return;
            elif postfix == 0xE:
                self.SHL(reg1); #another weird one
                return;

        elif prefix == 9:
            if postfix == 0:
                self.SNEreg(reg1, reg2);
                return;

        #instructions with 3 4-bit parameters (two registers, one 'nibble')
        nibble = postfix;
        if prefix == 0xD:
            self.DRW(reg1, reg2, nibble);
            return;
        
        #if it hasn't been decoded yet, it doesn't exist
        raise(f"Bad instruction: {inst}")


    def CLS(self):
        """instruction to clear the display"""
        self.load_display();
        self.pc += 1;

    def RET(self):
        """instruction to return from a subroutine"""
        self.pc = stack[sp];
        self.sp -= 1;

    def JP(self, addr):
        """instruction to jump to addresss addr"""
        self.pc = addr;

    def CALL(self, addr):
        """instruction to call a subroutine at address addr"""
        self.sp += 1;
        self.stack[sp] = pc;
        self.pc = addr;

    def SEval(self, reg, val):
        """instruction to skip the next instruction if a register is val"""
        if regs[reg] == val:
            self.pc += 2;
        else:
            self.pc += 1;

    def SNEval(self, reg, val):
        """instruction to skip the next instruction if reg is not val"""
        if self.regs[reg] != val:
            self.pc += 2;
        else:
            self.pc += 1;

    def SEreg(self, reg1, reg2):
        """instruction to skip to the next instruction if the value in
        reg 1 is the same as the value in reg 2"""
        if self.regs[reg1] == self.regs[reg2]:
            self.pc += 2;
        else:
            self.pc += 1;

    def LDval(self, reg, val):
        """instruction to load a value into a register"""
        self.regs[reg] = val;
        self.pc += 1;

    #TODO: should this account for a carry/8-bit limit?
    def ADDval(self, reg, val):
        """instruction to add a value to a register"""
        self.regs[reg] = self.regs[reg] + val;
        self.pc += 1;

    def LDreg(self, reg1, reg2):
        """instruction to load the value from one register into another"""
        self.regs[reg1] = self.regs[reg2];
        self.pc += 1;

    def OR(self, reg1, reg2):
        """instruction to bitwise or two registers and store the result"""
        self.regs[reg1] = self.regs[reg1] | self.regs[reg2];
        self.pc += 1;

    def AND(self, reg1, reg2):
        """instruction to bitwise and two registers and store the result"""
        self.regs[reg1] = self.regs[reg1] & self.regs[reg2];
        self.pc += 1;

    def XOR(self, reg1, reg2):
        """instruction to bitwise xor two registers and store the result"""
        self.regs[reg1] = self.regs[reg1] ^ self.regs[reg2];
        self.pc += 1;

    def ADDreg(self, reg1, reg2):
        """instruction to add the values in two registers and store the 
        result"""
        self.regs[reg1] = self.regs[reg1] + self.regs[reg2];

        if self.regs[reg1] > 255:
            self.regVF = 1; #set carry flag
            self.regs[reg1] = self.regs[reg1] & 255 #keep 8-bit limit
        else:
            self.regVF = 0; 

        self.pc += 1;

    def SUB(self, reg1, reg2):
        """instruction to subtract the value of one register from another"""
        if self.regs[reg1] > self.regs[reg2]:
            self.regVF = 1;
        else:
            self.regVF = 0;
        
        self.regs[reg1] = self.regs[reg1] - self.regs[reg2];
        self.regs[reg1] = self.regs[reg1] & 255; 
            #apparently this fixes unsigned 8-bit subtraction

        self.pc += 1;

    def SHR(self, reg):
        """instruction to divide the value of a register by 2"""
        self.regVF = self.regs[reg] % 2; #if it was odd, set the flag
        self.regs[reg] = self.regs[reg] // 2;
        self.pc += 1;
    
    def SUBN(self, reg1, reg2):
        """instruction to subtract the value of one register from another
        but in reverse"""
        self.regVF = self.regs[reg2] > self.regs[reg1]; #set flag?
        self.regs[reg1] = self.regs[reg2] - self.regs[reg1]; #subtract
        self.regs[reg1] = self.regs[reg1] & 255; #limit to 8 bits
        self.pc += 1;

    def SHL(self, reg):
        """instruction to multiply the value in a register by 2"""
        self.regVF = self.regs[reg] > 127; #set flag
        self.regs[reg] = self.regs[reg] * 2; #multiply
        self.regs[reg] = self.regs[reg] & 255; #limit to 8 bits
        self.pc += 1;

    def SNEreg(self, reg1, reg2):
        """instruction to skip the next instruction if two registers
        are not equal"""
        if self.regs[reg1] != self.regs[reg2]:
            self.pc += 2;
        else:
            self.pc += 1;

    def LDI(self, addr):
        """insruction to set the I register to a given address"""
        self.regI = addr;
        self.pc += 1;

    def JP0(self, addr):
        """instruction to jump to the instruction at addr + the value
        in register 0"""
        self.pc = addr + self.regs[0];

    def RND(self, reg, b):
        """instruction to generate a random byte, bitwise and it with a given
        byte and store the result"""
        r = random.randint(0,255);
        self.regs[reg] = r & b;
        self.pc += 1;

    def DRW(self):
        """instruction to draw a sprite on the display"""
        pass;

    def SKP(self, reg):
        """instruction to skip the next instruction if the key corresponding
        to the value in a given register is pressed"""
        pass;

    def SKNP(self, reg):
        """instruction to skip the next instruction if the key corresponding
        to the value in a given register is not pressed"""
        pass;

    def LDregdt(self, reg):
        """instruction to load the value in the delay timer into a 
        register"""
        self.regs[reg] = self.dt;
        self.pc += 1;

    def LDkey(self, reg):
        """instruction to load the value of the next key press into a
        register"""
        pass;

    def LDdt(self, reg):
        """instruction to load the value from a register into the delay
        timer"""
        self.dt = self.regs[reg];
        self.pc += 1;

    def LDst(self, reg):
        """instruction to load the value from a register into the sound
        timer"""
        self.st = self.regs[reg];
        self.pc += 1;

    def ADDi(self, reg):
        """instruction to add the value in a register to the I register"""
        self.regI += self.regs[reg];
        self.regI = self.regI & (2**12-1) #maintain 12 bits
        self.pc += 1;

    def LDdigit(self, reg):
        """instruction to set the I register to the memory address of the
        sprite for the value in a given register"""
        pass;

    def LDbcd(self, reg):
        """instruction to store the decimal representation of the value in
        a register in the memory addresses directly after the i register"""
        val = self.regs[reg];
        
        hundreds = val // 100;
        val -= 100 * hundreds;
        tens = val // 10;
        val -= 10 * tens;
        ones = val;

        self.mem[self.regI] = hundreds;
        self.mem[self.regI+1] = tens;
        self.mem[self.regI+2] = ones;

        self.pc += 1;

    def LDmemreg(self, reg):
        """instruction to store the values in registers 0 - x in memory
        starting at the value in the I register"""
        loc = self.regI;
        for r in range(0, reg+1): #TODO: are we sure this should be inclusive?
            self.mem[loc] = self.regs[r];
            loc += 1;
        self.pc += 1;

    def LDregmem(self, reg):
        """instruction to load values from memory starting at the address
        pointed to by the I register into registers 0 to x"""
        loc = self.regI;
        for r in range(0, reg+1): #TODO: are we sure this should be inclusive?
            self.regs[r] = self.mem[loc];
            loc += 1;
        self.pc += 1;


def main():
    pass;

if __name__ == "__main__":
    main();
