import random;

class chip:
    def __init__():

        #memory
        mem = [0] * 4096; #main memory, each entry is one byte
        pc = 512; #program counter
                #program space is expected to start 512 bytes in

        #registers
        regs = [0]*16; #general purpose registers
        regI = 0; #"I" register
        regVF = 0; #"VF" register, usually used a flag

        #stack
        stack = [0]*16; #stack of return addresses for subroutines
        sp = 0; #stack pointer

        #timers
        dt = 0; #delay timer register, decreases to 0 at 60Hz
        st = 0; #sound timer registser, decreases to 0 at 60Hz
                #plays a sound as it decrmeents

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
        are equal"""
        if self.regs[reg1] == self.regs[reg2]:
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
