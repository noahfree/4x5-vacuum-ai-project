# Noah Free and Isaac Schroeder

from enum import Enum
import copy
import time

# Action enum containing the cost of each possible move
class Action(float, Enum):
    LEFT = 1.0
    RIGHT = 0.9
    UP = 0.8
    DOWN = 0.7
    SUCK = 0.6

# Coordinates class containing X and Y values
class Coordinates:
    def __init__(self, x, y):
        self.X = x
        self.Y = y

# class Env is the 4x5 grid with a vacuum
class Env:
    def __init__(self, x, y):
        matrix=[]
		# a 4x5 matrix is initialized with the string 'clean'
        for i in range(4):
            row=[]
            for j in range(5):
                row.append('clean')
            matrix.append(row)
        self.matrix = matrix
        self.position = Coordinates(x, y)
        self.total_cost = 0
        self.rooms_cleaned = 0
        self.path = []
		# layer is only used in the iterative deepening search
        self.layer = -1
	# set_dirt is used to create the initial environment
    def set_dirt(self, x, y):
        self.matrix[x][y] = 'dirty'
    def get_X(self):
        return self.position.X
    def get_Y(self):
        return self.position.Y
    def get_cost(self):
        return self.total_cost
	# the following 5 functions are called when the vacuum does a given action; the vacuum's position is altered, the total cost is updated, and the path is updated
    def move_left(self):
        self.position.Y -= 1
        self.total_cost += Action.LEFT.value
        self.path.append('LEFT')
    def move_right(self):
        self.position.Y += 1
        self.total_cost += Action.RIGHT.value
        self.path.append('RIGHT')
    def move_up(self):
        self.position.X -= 1
        self.total_cost += Action.UP.value
        self.path.append('UP')
    def move_down(self):
        self.position.X += 1
        self.total_cost += Action.DOWN.value
        self.path.append('DOWN')
    def clean_room(self):
        self.total_cost += Action.SUCK.value
        if (self.matrix[self.position.X][self.position.Y] == 'dirty'):
            self.rooms_cleaned += 1
            self.matrix[self.position.X][self.position.Y] = 'clean'
        self.path.append('SUCK')

# function compare_states() takes a node and a list of nodes; true is returned if the state of the given node is the same as the state of one of the nodes in the list
def compare_states(node, closed):
    toggle = True
    for state in closed:
		# if X or Y of the vacuum are not the same, then the states are not identical
        if node.get_X() != state.get_X():
            continue
        if node.get_Y() != state.get_Y():
            continue
        for i in range(len(node.matrix)):
            for j in range(len(node.matrix[i])):
                if (node.matrix[i][j] != state.matrix[i][j]):
                    toggle = False
		# if toggle is true, then a node with identical state has been found, so True is returned
        if toggle:
            return True
    return False

# print_state is used to print the state of the given node
def print_state(state):
    print("vacuum at: " + str(state.position.X) + ", " + str(state.position.Y) + "\n")
    for i in state.matrix:
        print(i[0] + " " + i[1] + " " + i[2] + " " + i[3] + " " + i[4])
        print("")

# expand_node is used to expand the given node/state; node expansion is optimized to prevent the vacuum from undoing the action that it just performed. For example, the vacuum cannot move Left if it moved Right in its previous move. Additionally, the number of nodes generated is returned
def expand_node(state, fringe, layer):
	# the generated count is initialized to 0
    generated_count = 0
    if (state.matrix[state.get_X()][state.get_Y()] == 'dirty'):
        new_state = copy.deepcopy(state)
        new_state.clean_room()
        new_state.layer = layer
        fringe.append(new_state)
		# if the room is dirty, the only possible move is to clean the room, so 1 is returned since only 1 node has been generated
        return 1
	# these if statements prevent the vacuum from moving outside of the grid, and the vacuum is also prevented from returning to its previous state
    if (state.get_Y() != 0 and (len(state.path) == 0 or state.path[len(state.path) - 1] != 'RIGHT')):
        new_state = copy.deepcopy(state)
        new_state.move_left()
        new_state.layer = layer
        fringe.append(new_state)
        generated_count += 1
    if (state.get_Y() != 4 and (len(state.path) == 0 or state.path[len(state.path) - 1] != 'LEFT')):
        new_state = copy.deepcopy(state)
        new_state.move_right()
        new_state.layer = layer
        fringe.append(new_state)
        generated_count += 1
    if (state.get_X() != 0 and (len(state.path) == 0 or state.path[len(state.path) - 1] != 'DOWN')):
        new_state = copy.deepcopy(state)
        new_state.move_up()
        new_state.layer = layer
        fringe.append(new_state)
        generated_count += 1
    if (state.get_X() != 3 and (len(state.path) == 0 or state.path[len(state.path) - 1] != 'UP')):
        new_state = copy.deepcopy(state)
        new_state.move_down()
        new_state.layer = layer
        fringe.append(new_state)
        generated_count += 1
	# the number of nodes generated is returned to the caller
    return generated_count

# select_node() is called to return the node in the given list that has the lowest total cost
def select_node(fringe):
	selected = 0
	for i in range(len(fringe)):
		if fringe[i].total_cost < fringe[selected].total_cost:
			selected = i
		# if the two nodes have the same cost, the tie breaker is based on which has the lower X coordinate, followed by which has the lower Y coordinate
		if fringe[i].total_cost == fringe[selected].total_cost:
			if fringe[i].get_X() < fringe[selected].get_X():
				selected = i
			if fringe[i].get_X() == fringe[selected].get_X() and fringe[i].get_Y() < fringe[selected].get_Y():
				selected = i
	return selected

# uniform_graph_search is used to run the uniform cost graph search algorithm on the given state until it cleans num_of_dirty_rooms rooms
def uniform_graph_search(state, num_of_dirty_rooms):
    expanded_count = 0
    generated_count = 0
    goal = []
	fringe = []
    closed = []
    fringe.append(state)
    while len(fringe) > 0:
        node = fringe.pop(select_node(fringe))
		# when a solution is found, the generated and expanded counts are returned, and the goal node is returned
        if (node.rooms_cleaned == num_of_dirty_rooms):
            print("   Generated Count => " + str(generated_count))
            print("   Expanded Count => " + str(expanded_count))
            return node
		# compare_states is called to see if the current node has already been expanded
        if (not compare_states(node, closed)):
            closed.append(node)
			# generated_count and expanded_count are incremented accordingly
            generated_count += expand_node(node, fringe, -1)
            expanded_count += 1
	# none is returned if a goal was not able to be found
    return None

# uniform_tree_search is used to run the uniform cost tree search algorithm on the given state until if cleans num_of_dirty_rooms rooms
def uniform_tree_search(state, num_of_dirty_rooms):
    expanded_count = 0
    generated_count = 0
    goal = []
	fringe = []
    fringe.append(state)
    while len(fringe) > 0:
        node = fringe.pop(select_node(fringe))
		# when a solution is found, the generated and expanded counts are returned, and the goal node is returned
        if (node.rooms_cleaned == num_of_dirty_rooms):
            print("   Generated Count => " + str(generated_count))
            print("   Expanded Count => " + str(expanded_count))
            return node
		# the generated count and expanded count are incremented accordingly
        generated_count += expand_node(node, fringe, -1)
        expanded_count += 1
	# none is returned if a goal was not able to be found
    return None

class NodeStats:
    def __init__(self, expanded_count, generated_count):
        self.Expanded_count = expanded_count
        self.Generated_count = generated_count


def ids(init_state, num_of_dirty_rooms):
    node_stats = NodeStats(0,0)
    depth = 0
    while True:
        result = dls(init_state, num_of_dirty_rooms, depth, node_stats)
        print("Depth " + str(depth) + " complete")
        if result != -1:  # if solution found instead of cutoff occurring
            print("   Generated Count => " + str(node_stats.Generated_count))
            print("   Expanded Count => " + str(node_stats.Expanded_count))
            return result
        depth += 1

def dls(node, num_of_dirty_rooms, limit, node_stats):
    cutoff_occurred = False
    if (node.rooms_cleaned == num_of_dirty_rooms):
        return node
    elif node.layer == limit:
        return -1  #cutoff reached
    else:
        successors = []
        node_stats.Expanded_count += 1
        node_stats.Generated_count += expand_node(node, successors, node.layer + 1)
        for successor in successors:
            result = dls(successor, num_of_dirty_rooms, limit, node_stats)
            if result == -1:
                cutoff_occurred = True
            elif result != -1:
                return result
    if cutoff_occurred:
        return -1

# print_info is used to print the goal path, cost of traversal, and execution time of the inputted node
def print_info(goal, start_time, end_time):
    print('   Goal path =>', end=' ')
    if goal != None:
        print(goal.path)
        print('   Cost of traversal => ' + str(goal.get_cost()))
    else:
        print('Goal path not found')
    print('   Execution time => ' + str(end_time-start_time))


def main():
	# while loop is used to create a menu system for the user
    while True:
        print("\n\nChoose algorithm to run:")
        print("  (A) Instance 1, Uniform Tree Search")
        print("  (B) Instance 1, Uniform Graph Search")
        print("  (C) Instance 1, Iterative Deepening Search")
        print("  (D) Instance 2, Uniform Tree Search")
        print("  (E) Instance 2, Uniform Graph Search")
        print("  (F) Instance 2, Iterative Deepening Search")
        print("  (G) Quit")
        selection = input("Please enter a letter: ")

        if (selection == 'A' or selection == 'a'):
            print('\nInstance 1 - Uniform Tree Search:')
			# instance 1's environment is set up, indexed at zero so each coordinate is decreased by 1
            instance_1 = Env(1, 1)
            instance_1.set_dirt(0, 1)
            instance_1.set_dirt(1, 3)
            instance_1.set_dirt(2, 4)
			# time() is called to calculate the execution time of the search function
            start = time.time()
            goal = uniform_tree_search(instance_1, 3)
            end = time.time()
            print_info(goal, start, end)
        elif (selection == 'B' or selection == 'b'):
            print('\nInstance 1 - Uniform Graph Search:')
			# instance 1's environment is set up, indexed at zero so each coordinate is decreased by 1
            instance_1 = Env(1, 1)
            instance_1.set_dirt(0, 1)
            instance_1.set_dirt(1, 3)
            instance_1.set_dirt(2, 4)
			# time() is called to calculate the execution time of the search function
            start = time.time()
            goal = uniform_graph_search(instance_1, 3)
            end = time.time()
            print_info(goal, start, end)
        elif (selection == 'C' or selection == 'c'):
            print('\nInstance 1 - Iterative Deepening Search:')
			# instance 1's environment is set up, indexed at zero so each coordinate is decreased by 1
            instance_1 = Env(1, 1)
            instance_1.set_dirt(0, 1)
            instance_1.set_dirt(1, 3)
            instance_1.set_dirt(2, 4)
			# time() is called to calculate the execution time of the search function
            start = time.time()
            goal = ids(instance_1, 3)
            end = time.time()
            print_info(goal, start, end)
        elif (selection == 'D' or selection == 'd'):
            print('\nInstance 2 - Uniform Tree Search:')
			# instance 2's environment is set up, indexed at zero so each coordinate is decreased by 1
            instance_2 = Env(2, 1)
            instance_2.set_dirt(0, 1)
            instance_2.set_dirt(1, 0)
            instance_2.set_dirt(1, 3)
            instance_2.set_dirt(2, 2)
			# time() is called to calculate the execution time of the search function
            start = time.time()
            goal = uniform_tree_search(instance_2, 4)
            end = time.time()
            print_info(goal, start, end)
        elif (selection == 'E' or selection == 'e'):
            print('\nInstance 2 - Uniform Graph Search:')
			# instance 2's environment is set up, indexed at zero so each coordinate is decreased by 1
            instance_2 = Env(2, 1)
            instance_2.set_dirt(0, 1)
            instance_2.set_dirt(1, 0)
            instance_2.set_dirt(1, 3)
            instance_2.set_dirt(2, 2)
			# time() is called to calculate the execution time of the search function
            start = time.time()
            goal = uniform_graph_search(instance_2, 4)
            end = time.time()
            print_info(goal, start, end)
        elif (selection == 'F' or selection == 'f'):
            print('\nInstance 2 - Iterative Deepening Search:')
			# instance 2's environment is set up, indexed at zero so each coordinate is decreased by 1
            instance_2 = Env(2, 1)
            instance_2.set_dirt(0, 1)
            instance_2.set_dirt(1, 0)
            instance_2.set_dirt(1, 3)
            instance_2.set_dirt(2, 2)
			# time() is called to calculate the execution time of the search function
            start = time.time()
            goal = ids(instance_2, 4)
            end = time.time()
            print_info(goal, start, end)
        elif (selection == 'G' or selection == 'g'):
			print('\nExiting program...\n')
            break
        else:
            print("Invalid input: please enter a letter A-G.")

# call main()
main()
