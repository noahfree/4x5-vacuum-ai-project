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
        if (self.position.Y != 0):
            self.position.Y -= 1
            self.total_cost += Action.LEFT.value
            self.path.append('LEFT')
    def move_right(self):
        if (self.position.Y != 4):
            self.position.Y += 1
            self.total_cost += Action.RIGHT.value
            self.path.append('RIGHT')
    def move_up(self):
        if (self.position.X != 0):
            self.position.X -= 1
            self.total_cost += Action.UP.value
            self.path.append('UP')
    def move_down(self):
        if (self.position.X != 3):
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
    if (state.get_Y() != 0):
        new_state = copy.deepcopy(state)
        new_state.move_left()
        new_state.layer = layer
        fringe.append(new_state)
        generated_count += 1
    if (state.get_Y() != 4):
        new_state = copy.deepcopy(state)
        new_state.move_right()
        new_state.layer = layer
        fringe.append(new_state)
        generated_count += 1
    if (state.get_X() != 0):
        new_state = copy.deepcopy(state)
        new_state.move_up()
        new_state.layer = layer
        fringe.append(new_state)
        generated_count += 1
    if (state.get_X() != 3):
        new_state = copy.deepcopy(state)
        new_state.move_down()
        new_state.layer = layer
        fringe.append(new_state)
        generated_count += 1
    return generated_count

def uniform_graph_search(state, fringe, num_of_dirty_rooms):
    expanded_count = 0
    generated_count = 0
    goal = []
    closed = []
    fringe.append(state)
    while len(fringe) > 0:
        #print("FRINGE COUNT: " + str(len(fringe)))
        #print("CLOSED COUNT: " + str(len(closed)) + "\n")
        fringe.sort(key=lambda x: x.total_cost)
        node = fringe.pop(0)
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
    while True:
        #print("FRINGE COUNT: " + str(len(fringe)))
        #print("CLOSED COUNT: " + str(len(closed)) + "\n")
        if len(fringe) == 0:
            print("   Generated Count => " + str(generated_count))
            print("   Expanded Count => " + str(expanded_count))
            return goal
        fringe.sort(key=lambda x: x.total_cost)
        node = fringe.pop(0)
        if (node.rooms_cleaned == num_of_dirty_rooms):
            print("   Generated Count => " + str(generated_count))
            print("   Expanded Count => " + str(expanded_count))
            return node
        generated_count += expand_node(node, fringe, -1)
        expanded_count += 1

def iterative_deepening_search(state, closed, num_of_dirty_rooms, layer):
    print(layer)
    state.layer = 0
    fringe = [state]
    while len(fringe) > 0:
        node = fringe.pop(0)
        if node.layer > layer:
            break
        if (node.rooms_cleaned == num_of_dirty_rooms):
            return node
        if (not compare_states(node, closed)):
            closed.append(node)
            expand_node(node, fringe, node.layer+1)
    return iterative_deepening_search(state, closed, num_of_dirty_rooms, layer+1)

def print_info(goal, start_time, end_time):
    print('   Goal path =>', end=' ')
    if goal != None:
        print(goal.path)
        print('   Cost of traversal => ' + str(goal.get_cost()))
    else:
        print('Goal path not found')
    print('   Execution time => ' + str(end_time-start_time))


def main():
    print('\nInstance 1 - Uniform Tree Search:')
    start = time.time()
    instance_1 = Env(1, 1)
    instance_1.set_dirt(0, 1)
    instance_1.set_dirt(1, 3)
    instance_1.set_dirt(2, 4)
    goal = uniform_tree_search(instance_1, [], 3)
    end = time.time()
    print_info(goal, start, end)

    print('\nInstance 1 - Uniform Graph Search:')
    instance_1 = Env(1, 1)
    instance_1.set_dirt(0, 1)
    instance_1.set_dirt(1, 3)
    instance_1.set_dirt(2, 4)
    start = time.time()
    goal = uniform_graph_search(instance_1, [], 3)
    end = time.time()
    print_info(goal, start, end)

    # print('\nInstance 1 - Iterative Deepening Search:')
    # start = time.time()
    # instance_1 = Env(1, 1)
    # instance_1.set_dirt(1, 1)
    # # instance_1.set_dirt(0, 1)
    # # instance_1.set_dirt(1, 3)
    # # instance_1.set_dirt(2, 4)
    # goal = iterative_deepening_search(instance_1, [], 1, 0)
    # end = time.time()
    # print_info(goal, start, end)

    # print('\nInstance 2 - Uniform Graph Search:')
    # start = time.time()
    # instance_2 = Env(2, 1)
    # instance_2.set_dirt(0, 1)
    # instance_2.set_dirt(1, 0)
    # instance_2.set_dirt(1, 3)
    # instance_2.set_dirt(2, 2)
    # goal = uniform_graph_search(instance_2, [], 4)
    # end = time.time()
    # print_info(goal, start, end)



main()
