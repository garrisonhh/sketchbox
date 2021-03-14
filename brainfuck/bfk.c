#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/*
 * brainfuck parser and interpreter
 */

// memory model
typedef struct tape_t {
	uint8_t *pos;
	uint8_t *neg;
	size_t max_pos, max_neg;
	size_t ptr;
} tape_t;

tape_t *new_tape() {
	tape_t *tape = (tape_t *)malloc(sizeof(tape_t));

	tape->max_pos = 8;
	tape->max_neg = 8;
	tape->pos = (uint8_t *)malloc(sizeof(uint8_t) * 8);
	tape->neg = (uint8_t *)malloc(sizeof(uint8_t) * 8);
	tape->ptr = 0;

	for (int i = 0; i < 8; i++) {
		tape->pos[i] = 0;
		tape->neg[i] = 0;
	}

	return tape;
}

void ptr_left(tape_t *tape) {
	tape->ptr--;

	if (-tape->ptr + 1 == tape->max_neg) {
		tape->max_neg += 8;
		tape->neg = (uint8_t *)realloc(tape->neg, sizeof(uint8_t) * tape->max_neg);
		
		for (int i = 0; i < tape->max_neg; i++)
			tape->neg[i] = 0;
	}
}

void ptr_right(tape_t *tape) {
	tape->ptr++;

	if (tape->ptr == tape->max_pos) {
		tape->max_pos += 8;
		tape->pos = (uint8_t *)realloc(tape->pos, sizeof(uint8_t) * tape->max_pos);

		for (int i = 0; i < tape->max_pos; i++)
			tape->pos[i] = 0;
	}
}

uint8_t *ptr_val(tape_t *tape) {
	if (tape->ptr >= 0)
		return tape->pos + tape->ptr;
	else
		return tape->neg - (tape->ptr + 1);
}

// ast model
const char OPERANDS[6] = "+-<>.,";
typedef enum operand {
	INC = 0,
	DEC = 1,
	LEFT = 2,
	RIGHT = 3,
	OUT = 4,
	IN = 5,
} operand;

typedef enum ast_node_type {
	OPERAND_NODE,
	LOOP_NODE,
	COMPOSITE_NODE
} ast_node_type;

typedef struct operand_node {
	operand *operands;
	size_t size;
} operand_node;

struct composite_node {
	struct ast_node **nodes;
	size_t size, max_size;
};

typedef struct composite_node loop_node;
typedef struct composite_node composite_node;

typedef struct ast_node {
	ast_node_type type;
	operand_node *operand_n;
	loop_node *loop_n;
	composite_node *composite_n;
} ast_node;

typedef struct program_t {
	ast_node *root_n;
	tape_t tape;
} program_t;

struct composite_node *new_composite_node() {
	struct composite_node *node = (struct composite_node *)malloc(sizeof(struct composite_node));

	node->max_size = 1;
	node->size = 0;
	node->nodes = (ast_node **)malloc(sizeof(ast_node));

	return node;
}

ast_node *new_ast_node(ast_node_type type) {
	ast_node *node = (ast_node *)malloc(sizeof(ast_node));

	node->type = type;
	node->operand_n = NULL;
	node->loop_n = NULL;
	node->composite_n = NULL;

	return node;
}

ast_node *create_operand_node(const char *text, size_t length) {
	ast_node *wrapped_node;
	operand_node *node;
	operand cur;
	int op_index = 0;

	node = (operand_node *)malloc(sizeof(operand_node));
	node->operands = (operand *)malloc(sizeof(operand) * length);
	node->size = length;

	for (int i = 0; i < length; i++) {
		switch (text[i]) {
			case '+':
				cur = INC;
				break;
			case '-':
				cur = DEC;
				break;
			case '<':
				cur = LEFT;
				break;
			case '>':
				cur = RIGHT;
				break;
			case '.':
				cur = OUT;
				break;
			case ',':
				cur = IN;
				break;
			default:
				continue;
		}

		node->operands[op_index++] = cur;
	}

	node->size = op_index;
	node->operands = (operand *)realloc(node->operands, sizeof(operand) * node->size);

	wrapped_node = new_ast_node(OPERAND_NODE);
	wrapped_node->operand_n = node;
	return wrapped_node;
}

program_t *new_program() {
	program_t *program = (program_t *)malloc(sizeof(program_t));

	program->root_n = new_ast_node(COMPOSITE_NODE);
	program->tape = *new_tape();

	return program;
}

void composite_node_add(struct composite_node *node, ast_node *other) {
	node->nodes[node->size++] = other;

	if (node->size == node->max_size) {
		node->max_size <<= 1;
		node->nodes = (ast_node **)realloc(node->nodes, sizeof(ast_node *) * node->max_size);
	}
}

void bfk_error(const char *message) {
	printf("bfk error: %s\n", message);
	exit(EXIT_FAILURE);
}

void loop_check(const char *text, size_t length) {
	int level = 0, i;

	for (i = 0; i < length; i++) {
		switch (text[i]) {
			case '[':
				level++;
				break;
			case ']':
				level--;
				break;
		}

		if (level < 0) {
			char error[50];
			sprintf(error, "loop closed without start at index %d.", i);
			bfk_error(error);
		}
	}

	if (level > 0) {
		bfk_error("EOF reached with an open loop block.");
	}
}

ast_node *parse_composite(const char *text, size_t length, bool is_root) {
	ast_node *wrapped_node;
	struct composite_node *node;
	int i, level = 0, local_start = 0;

	wrapped_node = new_ast_node(is_root ? COMPOSITE_NODE : LOOP_NODE);
	node = new_composite_node();

	for (i = 0; i < length; i++) {
		switch (text[i]) {
			case '[':
				if (level == 0 && i != local_start) {
					composite_node_add(node, create_operand_node(text + local_start, i - local_start));
					local_start = i + 1;
				}
				level++;
				break;
			case ']':
				level--;
				if (level == 0) {
					composite_node_add(node, parse_composite(text + local_start, i - local_start, false));
					local_start = i + 1;
				}
				break;
		}
	}

	composite_node_add(node, create_operand_node(text + local_start, i - local_start));

	if (is_root)
		wrapped_node->composite_n = node;
	else
		wrapped_node->loop_n = node;

	return wrapped_node;
}

program_t *parse(const char *text, size_t length) {
	program_t *program = new_program();

	program->root_n->composite_n = parse_composite(text, length, true)->composite_n;

	return program;
}

void print_node(ast_node *node, int level) {
	size_t len_padding = level * 2;
	char padding[len_padding + 1];
	int i;

	for (i = 0; i < len_padding; i++)
		padding[i] = ' ';
	padding[len_padding] = 0;

	if (node->type == OPERAND_NODE) {
		printf(padding);
		for (i = 0; i < node->operand_n->size; i++)
			putchar(OPERANDS[node->operand_n->operands[i]]);
		printf("\n");
	} else if (node->type == COMPOSITE_NODE) {
		for (i = 0; i < node->composite_n->size; i++)
			print_node(node->composite_n->nodes[i], level);
	} else {
		printf("%s[\n", padding);
		for (i = 0; i < node->loop_n->size; i++)
			print_node(node->loop_n->nodes[i], level + 1);
		printf("%s]\n", padding);
	}
}

void print_program_ast(program_t *program) {
	printf("<<<PROGRAM AST>>>\n");
	print_node(program->root_n, 0);
}

void print_program_tape(program_t *program) {
	printf("<<<TAPE STATE>>>\n");

	int i;
	for (i = program->tape.max_neg - 1; i >= 0; i--)
		printf("%6i:\t%hhu\n", -(i + 1), program->tape.neg[i]);
	for (i = 0; i < program->tape.max_pos; i++)
		printf("%6i:\t%hhu\n", i, program->tape.pos[i]);
}

void run_node(program_t *program, ast_node *node) {
	switch (node->type) {
		case OPERAND_NODE:
			for (int i = 0; i < node->operand_n->size; i++) {
				switch (node->operand_n->operands[i]) {
					case INC:
						(*ptr_val(&program->tape))++;
						break;
					case DEC:
						(*ptr_val(&program->tape))--;
						break;
					case LEFT:
						ptr_left(&program->tape);
						break;
					case RIGHT:
						ptr_right(&program->tape);
						break;
					case OUT:
						putchar((char)*ptr_val(&program->tape));
						break;
					case IN:
						*ptr_val(&program->tape) = getchar();
						break;
				}
			}
			break;
		case LOOP_NODE:
			while ((*ptr_val(&program->tape)) != 0) {
				for (int i = 0; i < node->loop_n->size; i++)
					run_node(program, node->loop_n->nodes[i]);
			}

			break;
		case COMPOSITE_NODE:
			for (int i = 0; i < node->composite_n->size; i++)
				run_node(program, node->composite_n->nodes[i]);
			break;
	}
}

void run_program(program_t *program) {
	run_node(program, program->root_n);
}

int main(int argc, char *argv[]) {
	char *text;
	size_t len_text;

	if (argc == 2) {
		text = argv[1];
		len_text = strlen(text);
	} else if (argc == 3 && strcmp(argv[1], "-f") == 0) {
		FILE *f = fopen(argv[2], "r");
		size_t i = 0;
		len_text = 0;

		while (fgetc(f) != EOF)
			len_text++;

		rewind(f);
		text = (char *)malloc(sizeof(char) * (len_text + 1));
		text[len_text] = 0;

		for (i = 0; i < len_text; i++)
			text[i] = fgetc(f);

		fclose(f);
	} else {
		bfk_error("could not parse arguments.\n");
	}

	program_t *program;

	loop_check(text, len_text);
	program = parse(text, len_text);
	// print_program_ast(program);

	run_program(program);
	printf("\n");

	// print_program_tape(program);

	return EXIT_SUCCESS;
}
