import sys

"""
notes:
- should stack exist at heap + 1 onwards rather than -1 below? might be faster?
- variable deletion/scoping? how would this work tho?
- figure out how people do boolean expressions in brainfuck
"""

SET_ZERO = "[-]"

# TODO order of operations; do more than add and subtract
"""
# this dict is expanded
OPERATION_ORDER = {
    "/*" : 0,
    "+-" : 1,
}

for k, v in OPERATION_ORDER.items():
    for c in k:
        OPERATION_ORDER[c] = v
    OPERATION_ORDER.pop(k)
"""

OPERANDS = "+-"

class ExprNode: # self-generating expression tree
    def __init__(self, text):
        self.operand = None
        self.values = []

        # separate into left and right of operand
        split = [""]
        is_right = False
        level = 0
        for c in text:
            if c == '(':
                level += 1
            elif c == ')':
                level -= 1
            elif level == 0:
                if c in OPERANDS and not is_right:
                    self.operand = c 
                    is_right = True
                    split.append("")
                elif c.isdigit() or c.isalpha() or c == '_':
                    split[is_right] += c

            if level < 0:
                syntax_error(text)

        if level > 0:
            syntax_error(text)
   
        for expr in split:
            expr = expr.strip()

            if expr[0] == '(' and expr[-1] == ')':
                expr = expr[1:-1]
            
            if self.operand != None:
                self.values.append(ExprNode(expr))
            else:
                self.values.append(expr)

    def brainfuckify(self, pb):
        """
        if this node is a value, brainfuckify pushes value to stack
        if this node is an expression, brainfuckify applies operation to top 2 stack values, pops higher when done
        at the end of brainfuckification, pb should have only 1 value left at top of stack which can be _moved to
        a variable or whatever
        """
        if self.operand is None:
            if self.values[0].isdigit():
                addr = pb._push()
                pb._gen_const(addr, int(self.values[0]))
            elif self.values[0] in pb.vars:
                pb._push_var_copy(self.values[0])
            else:
                syntax_error(f"unknown expression {self.values[0]}")
        else:
            for value in self.values:
                value.brainfuckify(pb)

            if self.operand == '+':
                pb.bfk += "ADD:\n"
                pb.bfk += "%s [ > + < - ]\n" % (pb._goto_addr(pb._peek()),)
            elif self.operand == '-':
                pb.bfk += "SUB:\n"
                pb.bfk += "%s [ > - < - ]\n" % (pb._goto_addr(pb._peek()),)

            pb._pop()

class ProgramBuilder:
    def __init__(self):
        self.bfk = ""
        self.ptr = 0

        self.vars = {}
        self.heap = 0
        self.stack = 0

        self.loops = []

    def _push(self):
        self.stack += 1
        return self._peek()

    def _pop(self): # "frees" stack memory
        self.stack -= 1

    def _peek(self):
        return -self.stack

    def _goto_addr(self, addr):
        diff = addr - self.ptr
        self.ptr = addr

        if diff >= 0:
            return ">" * diff
        else:
            return "<" * -diff

    def _goto_var(self, var):
        return self._goto_addr(self.vars[var])

    #TODO eval_rvalue + stack checking after expr eval
    def _gen_const(self, addr, constant):
        if constant == 0:
            self.bfk += "GEN_CONST 0 at %i:\n%s %s\n" % (addr_str(addr), self._goto_addr(addr), SET_ZERO)
            return

        # find best factors
        factor1 = 1
        for n in range(1, int(constant ** .5) + 1):
            if constant % n == 0:
                factor1 = n
        factor2 = int(constant / factor1)

        # generate code
        if factor1 == 1:
            self._gen_const(addr, constant - 1)
            self.bfk += "GEN_CONST adjust for prime:\n%s +\n" % (self._goto_addr(addr),)
        else:
            tempaddr = self._push()

            self.bfk += "GEN_CONST %i at %s:\n" % (constant, addr_str(addr))

            # zero out address being set
            self.bfk += "%s %s " % (self._goto_addr(addr), SET_ZERO)

            # set temporary address to factor1
            self.bfk += "%s %s %s " % (self._goto_addr(tempaddr), SET_ZERO, "+" * factor1)

            # add factor2 to addr factor1 times
            self.bfk += "[ %s %s %s - ]" % (self._goto_addr(addr), "+" * factor2, self._goto_addr(tempaddr))
            self.bfk += "\n"

            self._pop()

    def _move(self, addr, src_addr):
        self.bfk += "MOVE %s to %s:\n" % (addr_str(src_addr), addr_str(addr))
        self.bfk += "%s %s %s " % (self._goto_addr(addr), SET_ZERO, self._goto_addr(src_addr))
        self.bfk += "[ %s + %s - ]\n" % (self._goto_addr(addr), self._goto_addr(src_addr))

    def _push_copy(self, addr):
        tempaddrs = (self._push(), self._push())
        
        self.bfk += "PUSH_COPY of %s:\n" % (addr_str(addr),)
    
        # zero out tempaddrs
        for tempaddr in tempaddrs:
            self.bfk += "%s %s " % (self._goto_addr(tempaddr), SET_ZERO)

        # copy addr to tempaddrs
        self.bfk += "%s [ %s + %s + %s - ]\n" % (self._goto_addr(addr), self._goto_addr(tempaddrs[0]),
                                                 self._goto_addr(tempaddrs[1]), self._goto_addr(addr))

        # move top copy back
        self.bfk += "PUSH_COPY: "
        self._move(addr, tempaddrs[1])
        self._pop()

    def _push_var_copy(self, var):
        self._push_copy(self.vars[var])

    def _eval_expr(self, expr):
        node = ExprNode(expr)
        node.brainfuckify(self)

    def declare(self, var):
        self.vars[var] = self.heap
        self.heap += 1
        self.bfk += "DECLARE %s at %s\n" % (var, addr_str(self.vars[var]))

    def set_var(self, var, expr):
        self.bfk += "EVAL_EXPR start\n"
        self._eval_expr(expr)
        self.bfk += "EVAL_EXPR end\n"
        self._move(self.vars[var], self._peek())
        self._pop()

    def start_loop(self, var):
        self.loops.append(var)
        self.bfk += "START_LOOP %s:\n%s [\n" % (var, self._goto_var(var))

    def end_loop(self):
        var = self.loops.pop()
        self.bfk += "END_LOOP:\n%s ]\n" % (self._goto_var(var),)

    # TODO generalize these to expr?
    def print_var(self, var):
        self.bfk += "PRINT_VAR %s:\n%s .\n" % (var, self._goto_var(var))

    def input_var(self, var):
        self.bfk += "INPUT_VAR %s:\n%s ,\n" % (var, self._goto_var(var))

def syntax_error(message):
    print(f"B++ SYNTAX ERROR:\n{message}\n")
    exit(1)

def addr_str(addr):
    return f"minus {abs(addr)}" if addr < 0 else str(addr)

def transpile_recursive(pb, lines):
    i = 0
    while i < len(lines):
        line = lines[i]
        tokens = line.split()

        # TODO refactor, this is a mess
        if len(tokens) > 0:
            if tokens[0] in pb.vars and tokens[1] == ":=":
                pb.set_var(tokens[0], line[line.index(":=") + 2:])
            elif tokens[0] == "var":
                if len(tokens) == 2 and len(pb.loops) == 0:
                    if tokens[1] in pb.vars:
                        syntax_error(f"variable {tokens[1]} declared more than once")
                    else:
                        pb.declare(tokens[1])
                else:
                    syntax_error(line)
            elif tokens[0] == "loop":
                if len(tokens) == 2 and tokens[1] in pb.vars:
                    pb.start_loop(tokens[1])
                    
                    next_end = i + 1
                    while next_end < len(lines):
                        if lines[next_end].strip() == "end":
                            break
                        next_end += 1

                    if next_end == len(lines):
                        syntax_error("loop not ended.")
                    else:
                        transpile_recursive(pb, lines[i + 1:next_end])
                        pb.end_loop()
                        i = next_end
                else:
                    syntax_error(line)
            elif tokens[0] == "print":
                if len(tokens) == 2 and tokens[1] in pb.vars:
                    pb.print_var(tokens[1])
                else:
                    syntax_error(line)
            elif tokens[0] == "input":
                if len(tokens) == 2 and tokens[1] in pb.vars:
                    pb.input_var(tokens[1])
                else:
                    syntax_error(line)
            else:
                syntax_error(line)

        i += 1

def transpile(text):
    pb = ProgramBuilder()
    transpile_recursive(pb, text.split("\n"))
    return pb.bfk

def main():
    with open(sys.argv[1], "r") as f:
        print(transpile(f.read()))

if __name__ == "__main__":
    main()
