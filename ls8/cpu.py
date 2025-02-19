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
        #           00000LGE
        self.fl = 0b00000000
        # This is the instruction register, it contains a copy of the currently executing instruction
        self.ir = []
        # This is the stack pointer. It points to the top item of the stack. If there is not a top item of the stack, it points to 0xF4, which is the address in memory that stores the most recently pressed key. The beginning of the stack is 0xF5.
        self.sp = 0xF5
        self.branch_table = {}

    def CMP_func(self):
        # Get the two operands
        operand_a = self.random_access_memory[self.pc + 1]
        operand_b = self.random_access_memory[self.pc + 2]
        # Get the two values from registers
        register_a = self.register[operand_a]
        register_b = self.register[operand_b]
        # subtract one operand from the other
        # If the result is 0
        if register_a - register_b == 0:
            # Set the equal bit to 1
            self.fl = 0b00000001
        # Else if the result if positive
        elif register_a - register_b > 0:
            # Set the greater than bit to 1
            self.fl = 0b00000010
        # Else
        elif register_a - register_b < 0:
            # Set the less than bit to 1
            self.fl = 0b00000100
        else:
            self.fl = 0b00000000
        self.pc += 3
    
    def JMP_func(self):
        # Get register value
        operand_a = self.random_access_memory[self.pc + 1]
        register_value = self.register[operand_a]
        # Set pc to register value, which is new address
        self.pc = register_value

    def JEQ_func(self):
        if self.fl == 0b00000001:
            self.JMP_func()
        else:
            self.pc += 2
#        else:
#            # Get address from register and jump to it
#            operand_a = self.random_access_memory[self.pc + 1]
#            self.pc = self.register[operand_a]

    def JNE_func(self):
        if self.fl == 0b00000010 or self.fl == 0b00000100:
            self.JMP_func()
        else:
            self.pc += 2
#        else:
#            # Get address from register and jump to it
#            operand_a = self.random_access_memory[self.pc + 1]
#            self.pc = self.register[operand_a]

    def CALL_func(self):
        # Decrement the stack pointer
        self.sp -= 1
        # Get the address of the instruction right affter CALL instruction and CALL operand instruction
        ret_addr = self.pc + 2
        # Push the address onto the stack
        self.random_access_memory[self.sp] = ret_addr
        # Get the operand
        operand_a = self.random_access_memory[self.pc + 1]
        # Set pc to operand_a index of the register, which is an address to jump to the subroutine
        self.pc = self.register[operand_a]
    
    def RET_func(self):
        # Get the return address
        ret_addr = self.random_access_memory[self.sp]
        # Increment the stack pointer
        self.sp += 1
        # Store address in PC
        self.pc = ret_addr
    
#    def ST_func(self):
#        operand_a = pc + 1
#        operand_b = pc + 2
#        self.random_access_memory[self.register[operand_a]] = self.register[operand_b]
#        pc += 3

    def PUSH_func(self):
        self.sp -= 1
        operand_a = self.random_access_memory[self.pc + 1]
        self.random_access_memory[self.sp] = self.register[operand_a]
        self.pc += 2
    
    def POP_func(self):
        operand_a = self.random_access_memory[self.pc + 1]
        self.register[operand_a] = self.random_access_memory[self.sp]
        self.sp += 1
        self.pc += 2
    
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
    
    def ADD_func(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("ADD", operand_a, operand_b)
        self.pc += 3

    def MUL_func(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("MUL", operand_a, operand_b)
        self.pc += 3

    def set_up_branch_table(self):
        CALL = 0b01010000
        RET = 0b00010001
        HLT = 0b00000001
        PRN = 0b01000111
        LDI = 0b10000010
        MUL = 0b10100010
        ADD = 0b10100000
        PUSH = 0b01000101
        POP = 0b01000110
        CMP = 0b10100111
        JMP = 0b01010100
        JNE = 0b01010110
        JEQ = 0b01010101
        self.branch_table = {
            HLT: self.HLT_func,
            PRN: self.PRN_func,
            LDI: self.LDI_func,
            MUL: self.MUL_func,
            ADD: self.ADD_func,
            PUSH: self.PUSH_func,
            POP: self.POP_func,
            RET: self.RET_func,
            CALL: self.CALL_func,
            CMP: self.CMP_func,
            JMP: self.JMP_func,
            JNE: self.JNE_func,
            JEQ: self.JEQ_func
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
