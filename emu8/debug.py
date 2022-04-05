import tui8


def inst_to_asm(inst):
    """convert a two-byte integer instruction to chip-8 assembly"""

    # instructions with 0 params
    if inst == 0x00E0:
        return "CLS"
    elif inst == 0x00EE:
        return "RET"

    # single parameter (12-bit address)
    prefix = inst >> 12
    addr = inst & 0x0FFF
    if prefix == 0x1:
        return f"JP {tui8.triple_hex(addr)}"
    elif prefix == 0x2:
        return f"CALL {tui8.triple_hex(addr)}"
    elif prefix == 0xA:
        return f"LD I, {tui8.triple_hex(addr)}"
    elif prefix == 0xB:
        return f"JP V0, {tui8.triple_hex(addr)}"

    # two parameters, one of which is a register and the other is a value
    reg = addr >> 8
    val = addr & 0x0FF
    if prefix == 0x3:
        return f"SE v{hex(reg)[-1]}, {tui8.double_hex(val)}"
    elif prefix == 0x4:
        return f"SNE v{hex(reg)[-1]}, {tui8.double_hex(val)}"
    elif prefix == 0x6:
        return f"LD v{hex(reg)[-1]}, {tui8.double_hex(val)}"
    elif prefix == 0x7:
        return f"ADD v{hex(reg)[-1]}, {tui8.double_hex(val)}"
    elif prefix == 0xC:
        return f"RND v{hex(reg)[-1]}, {tui8.double_hex(val)}"

    # one parameter which is a single register
    postfix = val
    if prefix == 0xE:
        if postfix == 0x9E:
            return f"SKP v{hex(reg)[-1]}"
        elif postfix == 0xA1:
            return f"SKNP v{hex(reg)[-1]}"
    elif prefix == 0xF:
        if postfix == 0x07:
            return f"LD v{hex(reg)[-1]}, DT"
        elif postfix == 0x0A:
            return f"LD v{hex(reg)[-1]}, K"
        elif postfix == 0x15:
            return f"LD DT, v{hex(reg)[-1]}"
        elif postfix == 0x18:
            return f"LD ST, v{hex(reg)[-1]}"
        elif postfix == 0x1E:
            return f"ADD I, v{hex(reg)[-1]}"
        elif postfix == 0x29:
            return f"LD F, v{hex(reg)[-1]}"
        elif postfix == 0x33:
            return f"LD B, v{hex(reg)[-1]}"
        elif postfix == 0x55:
            return f"LD [I], v{hex(reg)[-1]}"
        elif postfix == 0x55:
            return f"LD v{hex(reg)[-1]}, [I]"

    # two parameters, both of which are registers
    reg1 = reg
    reg2 = postfix >> 4
    postfix = postfix & 0x0F
    if prefix == 0x5 and postfix == 0x0:
        return f"SE v{hex(reg1)[-1]}, v{hex(reg2[-1])}"
    elif prefix == 0x8:
        if postfix == 0x0:
            return f"LD v{hex(reg1)[-1]}, v{hex(reg2[-1])}"
        elif postfix == 0x1:
            return f"OR v{hex(reg1)[-1]}, v{hex(reg2[-1])}"
        elif postfix == 0x2:
            return f"AND v{hex(reg1)[-1]}, v{hex(reg2[-1])}"
        elif postfix == 0x3:
            return f"XOR v{hex(reg1)[-1]}, v{hex(reg2[-1])}"
        elif postfix == 0x4:
            return f"ADD v{hex(reg1)[-1]}, v{hex(reg2[-1])}"
        elif postfix == 0x5:
            return f"SUB v{hex(reg1)[-1]}, v{hex(reg2[-1])}"
        elif postfix == 0x6:
            return f"SHR v{hex(reg1)[-1]}, v{hex(reg2[-1])}"
        elif postfix == 0x7:
            return f"SUBN v{hex(reg1)[-1]}, v{hex(reg2[-1])}"
        elif postfix == 0xE:
            return f"SHL v{hex(reg1)[-1]}, v{hex(reg2[-1])}"
    elif prefix == 0x9 and postfix == 0x0:
        return f"SNE v{hex(reg1)[-1]}, v{hex(reg2[-1])}"

    # invalid instruction
    else:
        return f"ERR: {hex(inst)}"


def inst_to_asmdesc(inst):
    """convert a two-byte integer instruction to a
    description of the chip-8 assemly instruction"""

    # instructions with 0 params
    if inst == 0x00E0:
        return "clear the display"
    elif inst == 0x00EE:
        return "return from a subroutine"

    # single parameter (12-bit address)
    prefix = inst >> 12
    addr = inst & 0x0FFF
    if prefix == 0x1:
        return f"jump to instruction at {tui8.triple_hex(addr)}"
    elif prefix == 0x2:
        return f"call subroutine at {tui8.triple_hex(addr)}"
    elif prefix == 0xA:
        return f"load the value {tui8.triple_hex(addr)} into the I register"
    elif prefix == 0xB:
        return f"jump to {tui8.triple_hex(addr)} plus the value in V0"

    # two parameters, one of which is a register and the other is a value
    reg = addr >> 8
    val = addr & 0x0FF
    if prefix == 0x3:
        return f"skip the next instruction if v{hex(reg)[-1]} and {tui8.double_hex(val)} have the same value"
    elif prefix == 0x4:
        return f"skip the next instruction if v{hex(reg)[-1]} and {tui8.double_hex(val)} do not have the same value"
    elif prefix == 0x6:
        return f"load the value {tui8.double_hex(val)} into v{hex(reg)[-1]}"
    elif prefix == 0x7:
        return f"add the value {tui8.double_hex(val)} to v{hex(reg)[-1]}"
    elif prefix == 0xC:
        return f"generate a random byte, bitewise and it with {tui8.double_hex(val)} and store it in v{hex(reg)[-1]}"

    # one parameter which is a single register
    postfix = val
    if prefix == 0xE:
        if postfix == 0x9E:
            return f"skip the next instruction if the key in v{hex(reg)[-1]} is being pressed"
        elif postfix == 0xA1:
            return f"skip the next instruction if the key in v{hex(reg)[-1]} is not being pressed"
    elif prefix == 0xF:
        if postfix == 0x07:
            return f"load the value in DT into v{hex(reg)[-1]}"
        elif postfix == 0x0A:
            return f"wait for a keypress then store the key in  v{hex(reg)[-1]}"
        elif postfix == 0x15:
            return f"load the value from v{hex(reg)[-1]} into DT"
        elif postfix == 0x18:
            return f"load the value from v{hex(reg)[-1]} into ST"
        elif postfix == 0x1E:
            return f"add the value in v{hex(reg)[-1]} to the I register"
        elif postfix == 0x29:
            return f"set I to the location of the digit for the value stored in v{hex(reg)[-1]}"
        elif postfix == 0x33:
            return f"convert the value in v{hex(reg)[-1]} to decimal and store the digits in memory at I through I+2"
        elif postfix == 0x55:
            return f"store the values in registers v0 through v{hex(reg)[-1]} in memory starting at the address in I"
        elif postfix == 0x55:
            return f"read memory into registers v0 through v{hex(reg)[-1]} starting at the address in I"

    # two parameters, both of which are registers
    reg1 = reg
    reg2 = postfix >> 4
    postfix = postfix & 0x0F
    if prefix == 0x5 and postfix == 0x0:
        return f"skip the next instruction if the values in v{hex(reg1)[-1]} and v{hex(reg2[-1])} are equal"
    elif prefix == 0x8:
        if postfix == 0x0:
            return f"load the value from v{hex(reg2)[-1]} into v{hex(reg2[-1])}"
        elif postfix == 0x1:
            return f"bitwise OR the values in v{hex(reg1)[-1]} and v{hex(reg2[-1])} and store the result in v{hex(reg1)[-1]}"
        elif postfix == 0x2:
            return f"bitwise AND the values in v{hex(reg1)[-1]} and v{hex(reg2[-1])} and store the result in v{hex(reg1)[-1]}"
        elif postfix == 0x3:
            return f"bitwise XOR the values in v{hex(reg1)[-1]} and v{hex(reg2[-1])} and store the result in v{hex(reg1)[-1]}"
        elif postfix == 0x4:
            return f"add the value from v{hex(reg2)[-1]} to v{hex(reg2[-1])}"
        elif postfix == 0x5:
            return f"subtract the value in v{hex(reg2)[-1]} from v{hex(reg1[-1])}"
        elif postfix == 0x6:
            return f"divide the value in v{hex(reg1)[-1]} by 2, store the result in v{hex(reg1[-1])}, and set VF accordingly"
        elif postfix == 0x7:
            return f"set v{hex(reg1)[-1]} to v{hex(reg2[-1])} minus v{hex(reg1)[-1]} and set VF to NOT borrow"
        elif postfix == 0xE:
            return f"the value in v{hex(reg1)[-1]} is multiplied by 2 and stored in v{hex(reg1[-1])} and VF is set to overflow"
    elif prefix == 0x9 and postfix == 0x0:
        return f"skip the next instruction if the values in v{hex(reg1)[-1]} and v{hex(reg2[-1])} are not equal"

    # invalid instruction
    else:
        return "invalid instruction"
