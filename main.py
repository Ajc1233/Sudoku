from copy import deepcopy
import pygame
from board_generator import gen_main, get_answer
from sys import exit
from time import time
import multiprocessing as mp


class Button:

    def __init__(self, x, y, image):
        self.width_start, self.width_end = x
        self.height_start, self.height_end = y
        self.image = image
        self.clicked = False

    def is_clicked(self):
        return self.clicked

    def draw(self, new_image=None):
        if not new_image:
            new_image = self.image
        screen.blit(new_image, (self.width_start, self.height_start))
        *_, image_width, image_height = new_image.get_rect()
        pygame.display.update([self.width_start, self.height_start, image_width, image_height])

    def get_width_coords(self):
        return [self.width_start, self.width_end]

    def get_height_coords(self):
        return [self.height_start, self.height_end]


class Tile:
    to_note = False

    def __init__(self, permanent, w_coords, h_coords, number):
        self.width_start, self.width_end = w_coords
        self.height_start, self.height_end = h_coords
        self.current_number = number
        self.note_numbers = []
        self.PERMANENT = permanent
        if self.PERMANENT:
            self.change_image_permanent(number)

    def has_notes(self):
        if self.note_numbers:
            return True
        return False

    def get_notes(self):
        numbers_list = []
        for number in self.note_numbers:
            numbers_list.append(number)
        return numbers_list

    def empty_notes(self):
        self.note_numbers = []

    def get_current_number(self):
        return self.current_number

    def get_width_coords(self):
        return [self.width_start, self.width_end]

    def get_height_coords(self):
        return [self.height_start, self.height_end]

    def is_permanent(self):
        return self.PERMANENT

    def change_image_permanent(self, number_selected):
        self.current_number = number_selected
        number_image = f'{self.number_to_image_name(number_selected)}-perm.png'
        num_chosen = pygame.image.load(number_image)
        screen.blit(num_chosen, (self.width_start, self.height_start))

    def change_image(self, number_selected):
        if self.is_permanent():
            return

        if Tile.to_note and not number_selected == 10:
            image_to_load, height_margin, width_margin = self.change_image_to_note(number_selected)

        else:
            image_to_load = f'{self.number_to_image_name(number_selected)}.png'
            width_margin = height_margin = 0
            self.current_number = number_selected
            self.note_numbers = []

        num_chosen = pygame.image.load(image_to_load)
        screen.blit(num_chosen, (self.width_start + width_margin, self.height_start + height_margin))
        self.set_focus()

    def change_image_to_note(self, number_selected):
        if self.does_note_number_exist(number_selected):
            image_to_load = "img/blank-mini.png"
        else:
            image_to_load = f'{self.number_to_image_name(number_selected)}-mini.png'
        height_margin, width_margin = self.get_mini_height_width(number_selected)
        if self.current_number:
            reset_number = pygame.image.load("img/blank.png")
            screen.blit(reset_number, (self.width_start, self.height_start))
            self.current_number = 0
        return image_to_load, height_margin, width_margin

    def does_note_number_exist(self, number):
        if number in self.note_numbers:
            self.note_numbers.remove(number)
            return True
        self.note_numbers.append(number)
        return False

    def set_focus(self):
        if not Tile.to_note:
            color = (201, 8, 18)
        else:
            color = (12, 23, 145)
        self.draw_focus(color)

    def remove_focus(self):
        color = (228, 228, 228)
        if self.PERMANENT:
            color = (153, 217, 234)
        self.draw_focus(color)

    def tile_correct(self):
        self.draw_focus((4, 201, 47))

    def tile_incorrect(self):
        self.draw_focus((201, 4, 14))

    def draw_focus(self, color):
        pygame.draw.rect(screen, color, [self.width_start, self.height_start, 60, 60], 3)

    @staticmethod
    def get_mini_height_width(number_selected):
        height_margin = width_margin = 0
        if number_selected in range(1, 4):
            height_margin = 0
        elif number_selected in range(4, 7):
            height_margin = 20
        elif number_selected in range(7, 10):
            height_margin = 40

        if number_selected % 3 == 1:
            width_margin = 0
        elif number_selected % 3 == 2:
            width_margin = 20
        elif number_selected % 3 == 0:
            width_margin = 40

        return height_margin, width_margin

    @staticmethod
    def number_to_image_name(number):
        number -= 1
        images = ["img/1", "img/2", "img/3", "img/4", "img/5", "img/6",
                  "img/7", "img/8", "img/9", "img/blank"]
        return images[number]

    @staticmethod
    def toggle_note():
        Tile.to_note = not Tile.to_note


def init_game():
    build_grid(1)
    build_border()
    return build_tile_row()


def build_grid(width, count=1):
    thick_line = False
    if width == 502:
        return
    line_color = (122, 122, 122)

    offset = 63
    if count % 2 == 0:
        offset = 62
    new_width = width + offset

    thickness = 2
    if count % 3 == 0:
        thickness = 4
        line_color = (0, 0, 0)
        thick_line = True
        count = 1 if count > 2 else count + 1
        build_grid(new_width, count)

    pygame.draw.line(screen, line_color, (0, new_width), (567, new_width), thickness)
    pygame.draw.line(screen, line_color, (new_width, 0), (new_width, 567), thickness)
    count = 1 if count > 2 else count + 1
    if thick_line:
        return

    build_grid(new_width, count)


def build_border():
    color1 = (0, 0, 0)
    # Top, right, bottom, left
    pygame.draw.lines(screen, color1, False, ((0, 1), (568, 1)), 4)
    pygame.draw.lines(screen, color1, False, ((565, 0), (565, 567)), 4)
    pygame.draw.lines(screen, color1, False, ((0, 565), (568, 565)), 4)
    pygame.draw.lines(screen, color1, False, ((1, 0), (1, 567)), 4)


def build_tile_row():
    tile_list = []
    start_row_coords = 0
    perm_numbs = generate_playing_board()
    for tile in range(0, 9):
        offset_tile_height_start, offset_tile_height_end = get_offsets(start_row_coords, tile)
        tile_list += create_tile(offset_tile_height_start, offset_tile_height_end, perm_numbs)
        start_row_coords = offset_tile_height_end
    return tile_list


def generate_playing_board_from_user():
    temp_tiles = deepcopy(tiles)
    for tile in temp_tiles:
        yield tile


def create_tile(offset_height_start, offset_height_end, perm_numbs):
    tile_list = []
    start_coords = 0
    for line in range(0, 9):
        is_tile_permanent = next(perm_numbs)
        offset_width_start, offset_width_end = get_offsets(start_coords, line)
        if is_tile_permanent != 0:
            tile_list.append(
                Tile(True, (offset_width_start, offset_width_end),
                     (offset_height_start, offset_height_end), is_tile_permanent))
        else:
            tile_list.append(
                Tile(False, (offset_width_start, offset_width_end),
                     (offset_height_start, offset_height_end), 0))

        start_coords = offset_width_end
    return tile_list


def create_buttons():
    n_button = Button((0, 130), (625, 668), pygame.image.load("img/note-button.png"))
    g_button = Button((219, 349), (625, 668), pygame.image.load("img/gen_button.png"))
    s_button = Button((438, 568), (625, 668), pygame.image.load("img/solution_btn.png"))
    n_button.draw()
    s_button.draw()
    g_button.draw()
    return g_button, n_button


def generate_board():
    boards = []
    queue = mp.Queue()
    board_number = 3
    for _ in range(board_number):
        boards.append(mp.Process(target=gen_main, args=(queue,)))

    for board in boards:
        board.start()

    wait_no_freeze()
    generated_board = queue.get()
    for board in boards:
        if board.is_alive():
            board.kill()
    return generated_board


def wait_no_freeze():
    for _ in range(3):
        pygame.event.pump()
        pygame.time.delay(2 * 1000)


def opening_page():
    screen.blit(pygame.image.load("img/start-screen.png"), (0, 0))
    start_button = Button((204, 364), (561, 611), pygame.image.load("img/start-button.png"))
    start_button.draw()
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            width, height = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN and 204 <= width <= 364 and 562 <= height <= 611:
                start_button.draw(pygame.image.load("img/loading-start-button.png"))
                new_playing_board = generate_board()
                screen.fill((228, 228, 228))
                return new_playing_board
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()


def check_user_puzzle():
    global users_solution, board_solution
    users_solution = build_user_board()
    board_solution = get_answer(playing_board)
    count = 0
    for row in range(0, 9):
        if board_solution[row] == users_solution[row]:
            count += 1
    if count == 9:
        return True
    else:
        return False


def user_won():
    screen.blit(pygame.image.load("img/winner.png"), (0, 0))
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                width, height = pygame.mouse.get_pos()
                if 20 <= width <= 240 and 445 <= height <= 498:
                    screen.blit(pygame.image.load("img/winner-loading.png"), (0, 0))
                    pygame.display.update()
                    return "play again"
                elif 285 <= width <= 567 and 472 <= height <= 548:
                    pygame.quit()
                    exit()
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()


def user_lost():
    screen.blit(pygame.image.load("img/lost.png"), (0, 0))
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                width, height = pygame.mouse.get_pos()
                # continue playing
                if 20 <= width <= 274 and 324 <= height <= 475:
                    return "continue with board"
                # see answer
                elif 294 <= width <= 548 and 324 <= height <= 475:
                    return "see answer"
                # create new board
                elif 20 <= width <= 274 and 495 <= height <= 651:
                    screen.blit(pygame.image.load("img/lost-loading.png"), (0, 0))
                    pygame.display.update([15, 315, 540, 348])
                    return "play again"
                elif 294 <= width <= 548 and 495 <= height <= 651:
                    pygame.quit()
                    exit()

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()


def get_offsets(start_coords, tile):
    tile_whitespace = 60

    line_offset = 2
    if tile % 3 == 0:
        line_offset = 4

    offset_tile_start = start_coords + line_offset
    offset_tile_end = tile_whitespace + start_coords + line_offset
    return offset_tile_start, offset_tile_end


def get_coords(check_tile, focus_width, focus_height):
    width_start, width_end = check_tile.get_width_coords()
    height_start, height_end = check_tile.get_height_coords()
    if (width_start < focus_width < width_end) and (height_start < focus_height < height_end):
        return True
    else:
        return False


def toggle_notes(current_tile, n_button):
    Tile.toggle_note()
    if Tile.to_note:
        n_button.draw(pygame.image.load("img/number-button.png"))
    else:
        n_button.draw(pygame.image.load("img/note-button.png"))
    if current_tile:
        current_tile.set_focus()


def generate_playing_board():
    for row in playing_board:
        for index in row:
            yield index


def build_user_board():
    user_board = []
    count = 0
    user_row = []
    for tile in tiles:
        user_row.append(tile.get_current_number())
        if count == 8:
            user_board.append(user_row)
            user_row = []
            count = 0
            continue
        count += 1

    return user_board


def number_exist(key):
    keypad_pressed = [pygame.K_KP1, pygame.K_KP2, pygame.K_KP3,
                      pygame.K_KP4, pygame.K_KP5, pygame.K_KP6,
                      pygame.K_KP7, pygame.K_KP8, pygame.K_KP9, pygame.K_KP0]
    if key in keypad_pressed:
        return keypad_pressed.index(key) + 1

    keyboard_pressed = [pygame.K_1, pygame.K_2, pygame.K_3,
                        pygame.K_4, pygame.K_5, pygame.K_6,
                        pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0]
    if key in keyboard_pressed:
        return keyboard_pressed.index(key) + 1


def get_time_format(time_taken):
    seconds = str(time_taken % 60)
    minutes = str(int(time_taken / 60))
    return minutes.rjust(2, '0') + ":" + seconds.rjust(2, '0')


def print_timer(time_taken):
    font_t = pygame.font.Font(None, 40)
    pygame.draw.rect(screen, (228, 228, 228), [200, 580, 165, 20])
    surface = font_t.render(f"Timer {get_time_format(time_taken)}", True, (255, 0, 0), (228, 228, 228))
    screen.blit(surface, (200, 580))


def arrow_key_pressed(key, current_width, current_height):
    if key == pygame.K_RIGHT:
        current_width += 60
        return current_width, current_height
    elif key == pygame.K_LEFT:
        current_width -= 60
        return current_width, current_height
    elif key == pygame.K_UP:
        current_height -= 60
        return current_width, current_height
    elif key == pygame.K_DOWN:
        current_height += 60
        return current_width, current_height

    return False


def check_boundary(boundary_width, boundary_height):
    if boundary_width > 568:
        boundary_width = 0
        boundary_height += 60
    elif boundary_width < 0:
        boundary_width = 568
        boundary_height -= 60
    if boundary_height > 568:
        boundary_height = 0
    elif boundary_height < 0:
        boundary_height = 568

    return boundary_width, boundary_height


def confirm_choice(g_button, warning):
    g_button.clicked = True
    g_button.draw(pygame.image.load("img/gen_button_confirm.png"))
    return warning + 1


def reset_button_to_default(g_button):
    g_button.clicked = False
    g_button.draw()
    return 0


def set_tile_focus(focus_width, focus_height):
    tile_to_focus = False
    for tile in tiles:
        if get_coords(tile, focus_width, focus_height):
            tile.set_focus()
            tile_to_focus = tile
        else:
            tile.remove_focus()
    return tile_to_focus


def main_loop(time_tracker=0):
    previous_second = 0
    timer = time()
    print_timer(time_tracker)

    warning = 0
    g_button, n_button = create_buttons()

    selected_tile = False
    tile_width = tile_height = 0
    pygame.event.clear()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                width, height = pygame.mouse.get_pos()
                if g_button.is_clicked() and (625 > height or not (219 <= width <= 349)):
                    warning = reset_button_to_default(g_button)
                if 568 >= height >= 0:
                    selected_tile = set_tile_focus(width, height)
                    if selected_tile:
                        tile_width = selected_tile.get_width_coords()[0] + 1
                        tile_height = selected_tile.get_height_coords()[0] + 1
                elif 625 <= height <= 668 and width <= 128:
                    toggle_notes(selected_tile, n_button)
                elif 625 <= height <= 668 and 219 <= width <= 349:
                    warning = confirm_choice(g_button, warning)
                    if warning == 2:
                        g_button.draw(pygame.image.load("img/gen_button_loading.png"))
                        return "play again", time_tracker
                elif 625 <= height <= 668 and width >= 438:
                    if check_user_puzzle():
                        return user_won(), time_tracker
                    else:
                        return user_lost(), time_tracker

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP_MINUS:
                    toggle_notes(selected_tile, n_button)

                if not selected_tile:
                    selected_tile = tiles[0]
                    tile_width = selected_tile.get_width_coords()[0] + 1
                    tile_height = selected_tile.get_height_coords()[0] + 1
                    selected_tile.set_focus()
                    break
                selected_number = number_exist(event.key)
                if selected_number:
                    selected_tile.change_image(selected_number)

                if event.key == pygame.K_ESCAPE:
                    selected_tile.remove_focus()
                    selected_tile = None

                if new_focus_width_height := arrow_key_pressed(event.key, tile_width, tile_height):
                    tile_width, tile_height = new_focus_width_height
                    while not (selected_tile := set_tile_focus(tile_width, tile_height)):
                        tile_width, tile_height = check_boundary(tile_width, tile_height)
                        tile_width, tile_height = arrow_key_pressed(event.key, tile_width, tile_height)

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if int(time() - timer) > previous_second:
            previous_second = int(time() - timer)
            time_tracker += 1
            print_timer(time_tracker)

        pygame.display.update()


def restart_game():
    global playing_board, tiles
    Tile.to_note = False
    playing_board = generate_board()
    screen.fill((228, 228, 228))
    tiles = init_game()


def continue_board():
    Tile.to_note = False
    screen.fill((228, 228, 228))
    for tile in tiles:
        if tile.get_current_number() != 0 and not tile.is_permanent():
            tile.change_image(tile.get_current_number())
            tile.remove_focus()
        elif tile.get_current_number() == 0 and tile.has_notes():
            Tile.toggle_note()
            temp_note_list = tile.get_notes()
            tile.empty_notes()
            while temp_note_list:
                note_to_enter = temp_note_list.pop()
                tile.change_image(note_to_enter)
            tile.remove_focus()
            Tile.toggle_note()
        elif tile.is_permanent():
            tile.change_image_permanent(tile.get_current_number())
            tile.remove_focus()

    build_grid(1)
    build_border()
    pygame.display.update()


def show_answer():
    tile_generator = generate_playing_board_from_user()
    count = 0
    while 1:
        for event in pygame.event.get():
            for row in range(9):
                count += 1
                for index in range(9):
                    current_tile = next(tile_generator)
                    if current_tile.is_permanent():
                        continue
                    if users_solution[row][index] == board_solution[row][index]:
                        current_tile.tile_correct()
                    else:
                        current_tile.tile_incorrect()
                        current_tile.change_image(board_solution[row][index])
                    pygame.event.pump()
                    w = current_tile.get_width_coords()
                    h = current_tile.get_height_coords()
                    pygame.display.update([w[0], h[0], w[1], h[1]])
                    pygame.time.delay(150)
            if count == 9:
                return

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()


def wait_for_click():
    screen.blit(pygame.image.load("img/click-to-continue.png"), (2, 568))
    pygame.display.update()
    pygame.event.clear()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                return
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()



def decision_loop():
    user_selection, prev_seconds = main_loop()
    while True:
        if user_selection == "see answer":
            continue_board()
            pygame.draw.rect(screen, (228, 228, 228), [0, 569, 568, 99])
            pygame.display.update()
            show_answer()
            wait_for_click()
            user_selection = user_lost()

        if user_selection == "continue with board":
            continue_board()
            user_selection, prev_seconds = main_loop(prev_seconds)

        if user_selection == "play again":
            restart_game()
            user_selection, prev_seconds = main_loop()

        if user_selection == "quit":
            pygame.quit()
            exit()


if __name__ == '__main__':
    pygame.init()
    WIDTH = 568
    HEIGHT = 668
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sudoku")
    screen.fill((228, 228, 228))
    users_solution = []
    board_solution = []
    playing_board = opening_page()
    tiles = init_game()
    decision_loop()
