class chip:
    def __init__():

        #memory
        mem = [0] * 4096; #main memory
        pc = 512; #program counter
                #program space is expected to start 512 bytes in

        #registers
        regs = [0]*16; #general purpose registers
        regI = 0; #"I" register
        regVF = 0; #"VF" register, usually used a flag

        #stack
        stack = []; #stack of return addresses for subroutines
        sp = 0; #stack pointer

        #timers
        dt = 0; #delay timer register, decreases to 0 at 60Hz
        st = 0; #sound timer registser, decreases to 0 at 60Hz
                #plays a sound as it decrmeents

def main():
    pass;





    #load our program

    #execute instructions







if __name__ == "__main__":
    main();
