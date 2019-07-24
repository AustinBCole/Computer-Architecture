"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.register = [0] * 8
        self.random_access_memory = [0b00000000] * 256
        self.pc = 0
        # This is a flag
        self.fl = 0b0000
        # This flag is used to indicate less-than
        self.l = 0
        # This flag is used to indicate greater-than
        self.g = 0
        # This flag is used to indicate equality between values
        self.e = 0
        # This is temporary memory
        self.stack = []
        # This is the instruction register, it contains a copy of the currently executing instruction
        self.ir = []
        if len(self.stack) > 0:
            # This is the stack pointer. It points to the top item of the stack. If there is not a top item of the stack, it points to 0xF4, which is the address in memory that stores the most recently pressed key.
            sp = self.stack[0]
        else:
            sp = self.random_access_memory[0xF4]
        self.branch_table = {}

    def HLT_func(self):
        sys.exit(0)
    
    def PRN_func(self):
        operand_a = self.ram_read(self.pc + 1)
        value = self.register[operand_a]
        print(value)
        self.pc += 2
    
    def LDI_func(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.register[operand_a] = operand_b
        self.pc += 3

    def MUL_func(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("MUL", operand_a, operand_b)
        self.pc += 3

    def set_up_branch_table(self):
        HLT = 0b00000001
        PRN = 0b01000111
        LDI = 0b10000010
        MUL = 0b10100010
        self.branch_table = {
            HLT: self.HLT_func,
            PRN: self.PRN_func,
            LDI: self.LDI_func,
            MUL: self.MUL_func
        }
        return

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        for instruction in program:
            self.random_access_memory[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.register[reg_a] *= self.register[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address):
        return self.random_access_memory[address]
    
    def ram_write(self, address, value):
        self.random_access_memory[address] = value
    
    def load_file(self):
        address = 0
        # This opens a file, goes through every line of the file and prints that line
        if len(sys.argv) != 2:
            print(f"usage: {sys.argv[0]} filename")
            sys.exit(1)
        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    num = line.split("#", 1)[0]
                
                    if num.strip() != '':
                        converted = int(num, 2)
                        self.random_access_memory[address] = converted
                        address += 1

        # Expect the unexpected, code defensively.
        except FileNotFoundError:
                    print(f"{sys.argv[0]}: {ssys.argv[1]} not found")
                    # In unix land, 0 exit status meanst that the program succeeded in working, non-zero means that it failed in some way.
                    sys.exit(2)

    

    def run(self):
        self.set_up_branch_table()
        self.load_file()
        """Run the CPU."""
        while self.random_access_memory[self.pc] != 0 :
            self.ir.append(self.random_access_memory[self.pc])
        
            op_code = self.random_access_memory[self.pc]
            self.branch_table[op_code]()



CPU().run()
