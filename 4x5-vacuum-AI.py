from enum import Enum
import copy
import time

class Action(float, Enum):
    LEFT = 1.0
    RIGHT = 0.9
    UP = 0.8
    DOWN = 0.7
    SUCK = 0.6

class Coordinates:
    def __init__(self, x, y):
        self.X = x
        self.Y = y

class Env:
    def __init__(self, x, y):
        matrix=[]
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
        self.layer = -1
    def set_dirt(self, x, y):
        self.matrix[x][y] = 'dirty'
    def get_X(self):
        return self.position.X
    def get_Y(self):
        return self.position.Y
    def get_cost(self):
        return self.total_cost
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

def compare_states(node, closed):
    toggle = True
    for state in closed:
        if node.get_X() != state.get_X():
            continue
        if node.get_Y() != state.get_Y():
            continue
        for i in range(len(node.matrix)):
            for j in range(len(node.matrix[i])):
                if (node.matrix[i][j] != state.matrix[i][j]):
                    toggle = False
        if toggle:
            return True
    return False

def print_state(state):
    print("vacuum at: " + str(state.position.X) + ", " + str(state.position.Y) + "\n")
    for i in state.matrix:
        print(i[0] + " " + i[1] + " " + i[2] + " " + i[3] + " " + i[4])
        print("")

def expand_node(state, fringe, layer):
    generated_count = 0
    if (state.matrix[state.get_X()][state.get_Y()] == 'dirty'):
        new_state = copy.deepcopy(state)
        new_state.clean_room()
        new_state.layer = layer
        fringe.append(new_state)
        return 1
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
    return generated_count

def select_node(fringe):
	selected = 0
	for i in range(len(fringe)):
		if fringe[i].total_cost < fringe[selected].total_cost:
			selected = i
	return selected

def uniform_graph_search(state, fringe, num_of_dirty_rooms):
    expanded_count = 0
    generated_count = 0
    goal = []
    closed = []
    fringe.append(state)
    while len(fringe) > 0:
        node = fringe.pop(select_node(fringe))
        if (node.rooms_cleaned == num_of_dirty_rooms):
            print("   Generated Count => " + str(generated_count))
            print("   Expanded Count => " + str(expanded_count))
            return node
        if (not compare_states(node, closed)):
            closed.append(node)
            generated_count += expand_node(node, fringe, -1)
            expanded_count += 1
    return None

def uniform_tree_search(state, fringe, num_of_dirty_rooms):
    expanded_count = 0
    generated_count = 0
    goal = []
    fringe.append(state)
    while len(fringe) > 0:
        node = fringe.pop(select_node(fringe))
        if (node.rooms_cleaned == num_of_dirty_rooms):
            print("   Generated Count => " + str(generated_count))
            print("   Expanded Count => " + str(expanded_count))
            return node
        generated_count += expand_node(node, fringe, -1)
        expanded_count += 1
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

def print_info(goal, start_time, end_time):
    print('   Goal path =>', end=' ')
    if goal != None:
        print(goal.path)
        print('   Cost of traversal => ' + str(goal.get_cost()))
    else:
        print('Goal path not found')
    print('   Execution time => ' + str(end_time-start_time))


def main():
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
            instance_1 = Env(1, 1)
            instance_1.set_dirt(0, 1)
            instance_1.set_dirt(1, 3)
            instance_1.set_dirt(2, 4)
            start = time.time()
            goal = uniform_tree_search(instance_1, [], 3)
            end = time.time()
            print_info(goal, start, end)
        elif (selection == 'B' or selection == 'b'):
            print('\nInstance 1 - Uniform Graph Search:')
            instance_1 = Env(1, 1)
            instance_1.set_dirt(0, 1)
            instance_1.set_dirt(1, 3)
            instance_1.set_dirt(2, 4)
            start = time.time()
            goal = uniform_graph_search(instance_1, [], 3)
            end = time.time()
            print_info(goal, start, end)
        elif (selection == 'C' or selection == 'c'):
            print('\nInstance 1 - Iterative Deepening Search:')
            instance_1 = Env(1, 1)
            instance_1.set_dirt(0, 1)
            instance_1.set_dirt(1, 3)
            instance_1.set_dirt(2, 4)
            start = time.time()
            goal = ids(instance_1, 3)
            end = time.time()
            print_info(goal, start, end)
        elif (selection == 'D' or selection == 'd'):
            print('\nInstance 2 - Uniform Tree Search:')
            instance_2 = Env(2, 1)
            instance_2.set_dirt(0, 1)
            instance_2.set_dirt(1, 0)
            instance_2.set_dirt(1, 3)
            instance_2.set_dirt(2, 2)
            start = time.time()
            goal = uniform_tree_search(instance_2, [], 4)
            end = time.time()
            print_info(goal, start, end)
        elif (selection == 'E' or selection == 'e'):
            print('\nInstance 2 - Uniform Graph Search:')
            instance_2 = Env(2, 1)
            instance_2.set_dirt(0, 1)
            instance_2.set_dirt(1, 0)
            instance_2.set_dirt(1, 3)
            instance_2.set_dirt(2, 2)
            start = time.time()
            goal = uniform_graph_search(instance_2, [], 4)
            end = time.time()
            print_info(goal, start, end)
        elif (selection == 'F' or selection == 'f'):
            print('\nInstance 2 - Iterative Deepening Search:')
            instance_2 = Env(2, 1)
            instance_2.set_dirt(0, 1)
            instance_2.set_dirt(1, 0)
            instance_2.set_dirt(1, 3)
            instance_2.set_dirt(2, 2)
            start = time.time()
            goal = ids(instance_2, 4)
            end = time.time()
            print_info(goal, start, end)
        elif (selection == 'G' or selection == 'g'):
            break
        else:
            print("Invalid input: please enter a letter A-G.")


main()
