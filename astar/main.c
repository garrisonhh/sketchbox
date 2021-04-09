#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include <math.h>
#include "hash.h"
#include "heap.h"
#include "utils.h"

/* 
 * figuring out a* in c for sdl-iso-project
 */

// for open/closed hash_table to point to
const int OPENSET = 0, CLOSEDSET = 1;
const double SQRT2 = sqrt(2);

typedef struct {
	int x, y;
} v2i;

// probably give this a longer name for actual implementation
struct node_t {
	v2i pos;
	double g, h, f;
	struct node_t *last;
};
typedef struct node_t node_t;

// manhattan distance plus diagonals 
double path_dist(v2i a, v2i b) {
	double dx, dy, diag;

	dx = abs(a.x - b.x);
	dy = abs(a.y - b.y);
	diag = MIN(dx, dy);

	return (diag * SQRT2) + (MAX(dx, dy) - diag);
}

hash_t node_hash(const void *node_ptr, size_t size_node_ptr) {
	v2i pos = ((node_t *)node_ptr)->pos;
	hash_t hash = pos.x + pos.y;

	for (int i = 0; i < 4; i++) {
		hash = (hash << 3) + hash;
	}

	return hash;
}

/*
void set_last(node_t *node, node_t *last) {
	node->last = last;
	node->g = (last == NULL ? INFINITY : last->g + path_dist(node->pos, last->pos));
	node->f = node->g + node->h;
}
*/

node_t *new_node(v2i pos, v2i goal_pos, node_t *last) {
	node_t *node = (node_t *)malloc(sizeof(node_t));

	node->pos = pos;
	node->h = path_dist(pos, goal_pos);
	node->g = (last == NULL ? INFINITY : last->g + path_dist(node->pos, last->pos));
	node->f = node->g + node->h;
	node->last = last;

	return node;
}

int compare_nodes(const void *a, const void *b) {
	return ((node_t *)a)->f - ((node_t *)b)->f;
}

/* 
function A*(start,goal)
	closedset := the empty set    // The set of nodes already evaluated.
	openset := {start}    // The set of tentative nodes to be evaluated, initially containing the start node
	came_from := the empty map    // The map of navigated nodes.

	g_score[start] := 0    // Cost from start along best known path.
	// Estimated total cost from start to goal through y.
	f_score[start] := g_score[start] + heuristic_cost_estimate(start, goal)

	while openset is not empty
		current := the node in openset having the lowest f_score[] value
		if current = goal
			return reconstruct_path(came_from, goal)

		remove current from openset
		add current to closedset
		for each neighbor in neighbor_nodes(current)
			tentative_g_score := g_score[current] + dist_between(current,neighbor)
			if neighbor in closedset
				if tentative_g_score >= g_score[neighbor]
					continue

			if neighbor not in openset or tentative_g_score < g_score[neighbor] 
				came_from[neighbor] := current
				g_score[neighbor] := tentative_g_score
				f_score[neighbor] := g_score[neighbor] + heuristic_cost_estimate(neighbor, goal)
				if neighbor not in openset
					add neighbor to openset

	return failure
*/
node_t *astar(size_t side, int world[side][side], v2i start_pos, v2i goal_pos) {
	// node lookup (in the actual sdl-iso-project implementation, this will be precomputed)
	v2i node_pos;
	node_t *node_world[side][side];

	for (node_pos.x = 0; node_pos.x < side; node_pos.x++)
		for (node_pos.y = 0; node_pos.y < side; node_pos.y++)
			node_world[node_pos.y][node_pos.x] = new_node(node_pos, goal_pos, NULL);

	// algo
	v2i nbor_pos;
	int *nbor_set;
	double potential_g;
	node_t *start, *current, *nbor;
	heap_t *open, *closed;
	hash_table *navigated;

	open = heap_create(compare_nodes);
	closed = heap_create(compare_nodes);
	navigated = hash_table_create(side * side, node_hash);

	start = node_world[start_pos.y][start_pos.x];
	start->g = 0;

	heap_insert(open, start);
	hash_set(navigated, start, sizeof start, (void *)&OPENSET);

	while (open->entries > 0) {
		current = heap_pop(open);

		if (current->h == 0)
			return current; // in sdl iso proj reconstruct path with dyn_array here
		
		heap_insert(closed, current);
		hash_set(navigated, current, sizeof start, (void *)&CLOSEDSET);

		for (nbor_pos.x = current->pos.x - 1; nbor_pos.x <= current->pos.x + 1; nbor_pos.x++) {
			for (nbor_pos.y = current->pos.y - 1; nbor_pos.y <= current->pos.y + 1; nbor_pos.y++) {
				if (nbor_pos.x == current->pos.x && nbor_pos.y == current->pos.y)
					continue;
				else if (nbor_pos.x < 0 || nbor_pos.x >= side || nbor_pos.y < 0 || nbor_pos.y >= side)
					continue;
				else if (world[nbor_pos.y][nbor_pos.x])
					continue;
				// no squeezing through diags
				else if (abs(nbor_pos.x - current->pos.x) + abs(nbor_pos.y - current->pos.y)
					  && (world[current->pos.y][nbor_pos.x] || world[nbor_pos.y][current->pos.x]))
					continue;
				
				potential_g = current->g + path_dist(current->pos, nbor_pos);
				nbor = node_world[nbor_pos.y][nbor_pos.x];
				nbor_set = (int *)hash_get(navigated, nbor, sizeof nbor);

				if (nbor_set == &CLOSEDSET && potential_g >= nbor->g)
					continue;

				if (nbor_set != &OPENSET || potential_g < nbor->g) {
					nbor->last = current;
					nbor->g = potential_g;
					nbor->f = nbor->g + nbor->h;

					if (nbor_set != &OPENSET) {
						hash_set(navigated, nbor, sizeof nbor, (void *)&OPENSET);
						heap_insert(open, nbor);
					}
				}
			}
		}
	}

	return NULL;
}

int main() {
	size_t side = 50;
	v2i start = {0, 0}, goal = {side - 1, side - 1};
	int world[side][side];
	srand(time(0));

	for (int i = 0; i < side * side; i++)
		((int *)world)[i] = (int)(rand() % 4 == 0 ? 1 : 0);

	while (world[start.y][start.x] && start.x < side - 1)
		start.x++;

	while (world[goal.y][goal.x] && goal.x > 0)
		goal.x--;

	struct timeval t1, t2;
	gettimeofday(&t1, NULL);
	node_t *path = astar(side, world, start, goal);
	gettimeofday(&t2, NULL);
	printf("astar execution took %ld seconds and %ld microseconds.\n",
		   t2.tv_sec - t1.tv_sec, t2.tv_usec - t1.tv_usec);

	int pathed[side][side];
	int pathsize = 0, c;
	memcpy(pathed, world, sizeof world);

	while (path != NULL) {
		if (pathed[path->pos.y][path->pos.x])
			printf("shit\n");
		pathed[path->pos.y][path->pos.x] = 100 + (pathsize++);
		path = path->last;
	}


	for (int y = 0; y < side; y++) {
		printf("\e[48;2;0;0;0m");
		printf("\e[38;2;255;255;255m");

		for (int x = 0; x < side; x++) {
			switch (pathed[y][x]) {
				case 0:
					printf("  ");
					break;
				case 1:
					printf("\u2588\u2588");
					break;
				default:
					c = (int)((((double)pathed[y][x] - 100) / (double)(pathsize - 1)) * 255);

					printf("\e[38;2;%i;%i;255m", c, (255 - c));
					printf("\u2588\u2588");
					printf("\e[38;2;255;255;255m");
					break;
			}
		}

		printf("\e[0m\n");
	}

	return 0;
}
