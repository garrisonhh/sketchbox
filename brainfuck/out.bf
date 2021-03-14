DECLARE a at 0
EVAL_EXPR start
GEN_CONST 26 at minus 1:
< [-] < [-] ++ [ > +++++++++++++ < - ]
EVAL_EXPR end
MOVE minus 1 to 0:
>> [-] < [ > + < - ]
START_LOOP a:
> [
EVAL_EXPR start
PUSH_COPY of 0:
< [-] < [-] >> [ < + < + >> - ]
PUSH_COPY: MOVE minus 2 to 0:
 [-] << [ >> + << - ]
GEN_CONST 64 at minus 2:
 [-] < [-] ++++++++ [ > ++++++++ < - ]
ADD:
> [ > + < - ]
EVAL_EXPR end
MOVE minus 1 to 0:
>> [-] < [ > + < - ]
PRINT_VAR a:
> .
EVAL_EXPR start
PUSH_COPY of 0:
< [-] < [-] >> [ < + < + >> - ]
PUSH_COPY: MOVE minus 2 to 0:
 [-] << [ >> + << - ]
GEN_CONST 65 at minus 2:
 [-] < [-] +++++ [ > +++++++++++++ < - ]
SUB:
> [ > - < - ]
EVAL_EXPR end
MOVE minus 1 to 0:
>> [-] < [ > + < - ]
END_LOOP:
> ]

