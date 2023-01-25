from random import randint, choice


def sudoku_zero_board():
    return [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]


def copy_board(board_to_copy):
    copied_board = [[index for index in row] for row in board_to_copy]
    return copied_board


def find_column_numbers(_sudoku, index):
    # Builds a list comprehension of the numbers in the specified column
    numbers_in_column = [i[index] for i in _sudoku]
    return numbers_in_column


def row_index_grid_start(starting_point):
    # Calculates the starting position for the 3x3 grid
    if starting_point % 3 == 2:
        return starting_point - 2
    if starting_point % 3 == 1:
        return starting_point - 1
    return starting_point


def find_grid(_sudoku, __row, index):
    # Used to find the numbers in the 3x3 grid
    beginning_row = row_index_grid_start(__row)
    beginning_index = row_index_grid_start(index)
    three_by_three = _sudoku[beginning_row][beginning_index:beginning_index + 3]
    three_by_three += _sudoku[beginning_row + 1][beginning_index:beginning_index + 3]
    three_by_three += _sudoku[beginning_row + 2][beginning_index:beginning_index + 3]
    return three_by_three


def find_nums_not_available(s_board, row, index):
    three_by_three = find_grid(s_board, row, index)
    column_row = find_column_numbers(s_board, index)
    current_row = s_board[row]
    # Returns numbers that cannot be used at the current index
    return set(current_row + three_by_three + column_row)


def sudoku_solver(sudoku, row=0, index=0):
    """
    Takes a sudoku board as a parameter and finds its one solution

    :param sudoku: This is the sudoku board that used to find its solution
    :param row: The current row of the board
    :param index: The current index of the board
    :return: Returns False if the number will not work in that position
    """
    if row >= 9:
        return True
    if sudoku[row][index] != 0:
        if index >= 8:
            return sudoku_solver(sudoku, row + 1)
        else:
            return sudoku_solver(sudoku, row, index + 1)
    current_row = sudoku[row]
    numbers_not_available = find_nums_not_available(sudoku, row, index)
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    available_numbers_list = tuple(filter(lambda x: x not in numbers_not_available, numbers))
    available_numbers_count = len(available_numbers_list)

    for count in range(available_numbers_count):
        current_row[index] = available_numbers_list[count]
        if index == 8:
            if sudoku_solver(sudoku, row + 1):
                return True
            else:
                current_row[index] = 0
                continue
        else:
            if not sudoku_solver(sudoku, row, index + 1):
                continue
            else:
                return True

    current_row[index] = 0
    return False


def find_permanent_numbers_per_row():
    # First step to generating a board. Generates how many permanent numbers for each row
    total_permanent_numbers_to_use, tracking_permanent_numbers_used = 30, 0
    numbers_to_set_per_row, permanent_numbers_list = [2, 3, 4, 5, 6, 7], []

    for counter in range(9):
        x = choice(numbers_to_set_per_row)
        if x == 6 or x == 7:
            if x == 6:
                numbers_to_set_per_row.remove(6)
            elif x == 7:
                numbers_to_set_per_row.remove(7)
        tracking_permanent_numbers_used += x

        if tracking_permanent_numbers_used > total_permanent_numbers_to_use + 3:
            return find_permanent_numbers_per_row()
        permanent_numbers_list.append(x)

    if not total_permanent_numbers_to_use + 2 >= tracking_permanent_numbers_used >= total_permanent_numbers_to_use - 2:
        return find_permanent_numbers_per_row()

    return permanent_numbers_list


def create_sudoku_board(permanent_numbers_per_row):
    # Second step in creating a board
    # Randomly generated numbers between 1 and 9 will be created and input into the sudoku board
    zero_board = sudoku_zero_board()
    for row in range(9):
        permanent_number_index = []
        for rand_gen in range(permanent_numbers_per_row[row]):
            random_number_list = randint(0, 8)
            while random_number_list in permanent_number_index:
                random_number_list = 1 if random_number_list + 1 > 8 else random_number_list + 1
            permanent_number_index.append(random_number_list)

        for index in range(9):
            if index not in permanent_number_index:
                continue
            numbers_not_available = find_nums_not_available(zero_board, row, index)
            random_number_to_insert = randint(1, 9)
            count = 0
            while random_number_to_insert in numbers_not_available:
                count += 1
                random_number_to_insert = 1 if random_number_to_insert + 1 > 9 else random_number_to_insert + 1
                # If stuck in loop, return False so that a new board can be generated
                if count >= 10:
                    return False, zero_board
            zero_board[row][index] = random_number_to_insert

    possible_answer = copy_board(zero_board)
    if not sudoku_solver(zero_board):
        return create_sudoku_board(permanent_numbers_per_row)
    return True, possible_answer


def get_available_numbers(numbers_not_available):
    possible_numbers = [x for x in range(1, 10) if x not in numbers_not_available]
    return possible_numbers


def one_solution(possible_board, permanent_numbers):
    orig_sud = copy_board(possible_board)

    for row in range(9):
        right_number = 0
        for index in range(9):
            solution_counter = 0
            if permanent_numbers[row][index] != 0:
                continue
            numbers_not_available = find_nums_not_available(possible_board, row, index)
            numbers_to_try = get_available_numbers(numbers_not_available)
            for number_to_insert in numbers_to_try:
                possible_board[row][index] = number_to_insert
                permanent_numbers = copy_board(possible_board)
                if sudoku_solver(possible_board, row):
                    solution_counter += 1
                    if solution_counter > 1:
                        return False
                    right_number = number_to_insert
                    possible_board = copy_board(orig_sud)

            if solution_counter != 1:
                return False

            orig_sud[row][index] = right_number
            possible_board = copy_board(orig_sud)
    return True


def generate_one_solution():
    #Main loop. While there is not a board with just one solution, keep generating
    while 1:
        possible_playing_board = generate_new_board()
        sudoku_permanent_indexes = copy_board(possible_playing_board)
        # This will take the generated solution and check it to make sure there is only one solution
        if one_solution(possible_playing_board, sudoku_permanent_indexes):
            break

    return sudoku_permanent_indexes


def generate_new_board():
    #If the board did not work, generate a new one
    x = False
    while not x:
        permanent_numbers_per_row = find_permanent_numbers_per_row()
        x, possible_playing_board = create_sudoku_board(permanent_numbers_per_row)
        if x:
            return possible_playing_board


def gen_main(queue):
    playing_board = generate_one_solution()
    queue.put(playing_board)


def get_answer(user_board):
    sudoku_solver(user_board)
    return user_board
