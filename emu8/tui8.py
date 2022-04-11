import curses
import debug8


class Tui:
    """represent the terminal user interface for a chip8 Chip object"""

    def __init__(self, stdscr, chip, compmode):
        """inintialize instance data and set curses settings"""
        self.stdscr = stdscr
        self.chip = chip
        self.compmode = compmode # are we running in fast mode or comprehensive mode

        curses.initscr()  # intialize screen
        curses.noecho()  # don't write pressed characters to the screen
        curses.curs_set(0)  # set cursor to invisible

        if self.compmode:
            self.init_windows_comp()
        else:
            self.init_windows_fast()

    def init_windows_fast(self):
        """initialize the minmal number of windows"""
        self.init_chip_win()
        self.init_key_win()
        self.init_input_win()

    def init_windows_comp(self):
        """initialize all windows"""
        self.init_chip_win()
        self.init_reg_win()
        self.init_mem_win()
        self.init_key_win()
        self.init_desc_win()
        self.init_input_win()

    def init_chip_win(self):
        """create window to display chip-8 screen contents"""
        self.chipWin = curses.newwin(33, 129, 0, 0)

        # set colors
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_GREEN)
        self.chipWinColors = curses.color_pair(1)

        for i in range(32):
            self.chipWin.addstr(i, 0, " " * 129)
        self.chipWin.refresh()

    def init_reg_win(self):
        """create window to display register contents and insert labels"""
        self.regWin = curses.newwin(6, 41, 33, 0)

        # registers 0 - F
        for row in range(4):
            for col in range(4):

                reg = 4 * row + col
                regstr = f"v{hex(reg)[2]}:{Tui.double_hex(0)}   "
                self.regWin.addstr(row, col * len(regstr), regstr)

        # special purpose registers
        istr = f"rI:{Tui.triple_hex(0)}"
        dtstr = f"rDT:{Tui.double_hex(0)}"
        ststr = f"rST:{Tui.double_hex(0)}"

        self.regWin.addstr(5, 0, istr)
        self.regWin.addstr("   " + dtstr)
        self.regWin.addstr("   " + ststr)

        self.regWin.refresh()

    def init_mem_win(self):
        """create window to display chip memory contents"""
        self.memWin = curses.newwin(45, 27, 0, 130)

        memlimit = 20 

        # each row in the 3 columns
        for y in range(2*memlimit + 1):

            # memory address column
            self.memWin.addstr(y, 0, Tui.triple_hex(0))
            # memory value column
            self.memWin.addstr(y, 6, Tui.double_hex(0))
            # assembly instruction column
            if y % 2 == 0:
                self.memWin.addstr(y, 12, debug8.inst_to_asm(0))
            else:
                self.memWin.addstr(y, 12, "               ")

        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)
        # self.memWin.addstr(3, 6 * memlimit, "^", curses.color_pair(5))

        self.memWin.refresh()

    def init_key_win(self):
        """create window to display keys pressed on the chip"""
        self.keyWin = curses.newwin(5, 15, 33, 42)
        offset = 5

        # set key coordinates in the window
        self.keyCoords = dict()

        # 1-9
        for row in range(3):
            for col in range(3):
                self.keyCoords[row * 3 + col + 1] = (row, col * 2 + offset)
        # C-F
        for row in range(4):
            self.keyCoords[12 + row] = (row, 2 * 3 + offset)

        # everything else
        self.keyCoords[10] = (3, 0 + offset)  # A
        self.keyCoords[0] = (3, 2 + offset)  # 0
        self.keyCoords[11] = (3, 4 + offset)  # B

        # put keys on the window
        for key in range(16):
            y, x = self.keyCoords[key]
            self.keyWin.addstr(y, x, hex(key)[2])

        # set highlight color for update method
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self.keyHighlightColor = curses.color_pair(2)

        self.keyWin.refresh()

    def init_desc_win(self):
        """create a window to describe currently executing instructions"""
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self.descHighlightColor = curses.color_pair(3)

        self.descWin = curses.newwin(3, 100, 41, 56)

        self.descWin.addstr(0, 0, "invalid instruction")
        self.descWin.addstr(1, 0, "invalid instruction", self.descHighlightColor)
        self.descWin.addstr(2, 0, "invalid instruction", curses.color_pair(0))

        self.descWin.refresh()


    def init_input_win(self):
        """initialize a blank window to accept user input"""
        self.inputWin = curses.newwin(1, 1, 39, 0)
        self.inputWin.addstr(0, 0, "")  # add blank sting to set cursor

    def update(self):
        """alternative method to update all windows"""
        if self.compmode:
            self.update_windows_comp()
        else:
            self.update_windows_fast()

    def update_windows_fast(self):
        """update the minimal number of windows (fast mode)"""
        self.update_chip_win()
        self.update_key_win()
        self.update_input_win()

    def update_windows_comp(self):
        """update all windows (comprehensive mode)"""
        self.update_chip_win()
        self.update_reg_win()
        self.update_mem_win()
        self.update_key_win()
        self.update_desc_win()
        self.update_input_win()

    def update_chip_win(self):
        """update the chip display window to match the chip"""

        # note that the display on the chip is sideways
        disp = self.chip.disp
        for x, column in enumerate(disp):
            for y, val in enumerate(column):
                if val:
                    self.chipWin.addstr(y, x * 2, "  ", self.chipWinColors)
                else:
                    self.chipWin.addstr(y, x * 2, "  ", curses.color_pair(0))

        self.chipWin.refresh()

    def update_reg_win(self):
        """update register window to match contents of chip registers"""

        # registers 0-15
        for row in range(4):
            for col in range(4):
                reg = 4 * row + col
                valstr = Tui.double_hex(self.chip.regs[reg])
                self.regWin.addstr(row, 10 * col + 3, valstr)

        # special purpose registers
        # I
        valstr = Tui.triple_hex(self.chip.regI)
        self.regWin.addstr(5, 3, valstr)
        # DT
        valstr = Tui.double_hex(self.chip.dt)
        self.regWin.addstr(5, 15, valstr)
        # ST
        valstr = Tui.double_hex(self.chip.st)
        self.regWin.addstr(5, 26, valstr)

        self.regWin.refresh()

    def update_mem_win(self):
        """update memory window to match contents of chip memory"""

        memlimit = 20  # this should be instance data probably
        pc = self.chip.pc
        mem = self.chip.mem

        self.memWin.erase()

        y = 0
        for addr in range(pc - memlimit, pc + memlimit + 1):

            if addr == pc:
                color = 5
            else:
                color = 0

            # memory address column
            self.memWin.addstr(y, 0, Tui.triple_hex(addr), curses.color_pair(color))
            # memory value column
            self.memWin.addstr(y, 6, Tui.double_hex(mem[addr]), curses.color_pair(color))
            # assembly instruction column
            if addr % 2 == 0:
                inst = (mem[addr] << 8) + mem[addr+1]
                self.memWin.addstr(y, 12, debug8.inst_to_asm(inst), curses.color_pair(color))
            else:
                self.memWin.addstr(y, 12, "               ", curses.color_pair(color))

            y += 1

        self.memWin.refresh()

    def update_key_win(self):
        """update key window to match contents of keys on chip"""

        for key, value in enumerate(self.chip.keys):
            y, x = self.keyCoords[key]
            if value:
                self.keyWin.addstr(y, x, hex(key)[2], self.keyHighlightColor)
            else:
                self.keyWin.addstr(y, x, hex(key)[2], curses.color_pair(0))

        self.keyWin.refresh()

    def update_desc_win(self):
        """update description window with previous, current, and next instruction descriptions"""
        # note that we base this off mem so previous and current may not be accurate since we don't
        # account for jumps

        pc = self.chip.pc
        mem = self.chip.mem

        self.descWin.erase()
        
        prevInst = (mem[pc-2] << 8) + mem[pc-1]
        currInst = (mem[pc] << 8) + mem[pc+1]
        nextInst = (mem[pc+2] << 8) + mem[pc+3]

        prevDesc = debug8.inst_to_asmdesc(prevInst)
        currDesc = debug8.inst_to_asmdesc(currInst)
        nextDesc = debug8.inst_to_asmdesc(nextInst)

        self.descWin.addstr(0, 0, prevDesc)
        self.descWin.addstr(1, 0, currDesc, self.descHighlightColor)
        self.descWin.addstr(2, 0, nextDesc, curses.color_pair(0))

        self.descWin.refresh()

    def update_input_win(self):
        """update input window to set cursor to receive input"""
        self.inputWin.addstr(0, 0, "")

    @staticmethod
    def double_hex(n):
        """return a two digit hex representation of an integer"""
        h = hex(n)
        if len(h) == 3:
            h = h[:2] + "0" + h[2]
        return h

    @staticmethod
    def triple_hex(n):
        """return a three digit hex representation of an integer"""
        h = Tui.double_hex(n)
        if len(h) == 4:
            h = h[:2] + "0" + h[2:]
        return h


def main(stdscr):
    pass


if __name__ == "__main__":
    curses.wrapper(main)
