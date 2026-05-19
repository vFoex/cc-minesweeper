from enum import Enum
import random
from typing import List, Tuple


class MineseeperGridCase:

    def __init__(self,
                 index: Tuple[int, int],
                 is_mine: bool,
                 number_of_close_mines: int = 0) -> None:
        self.index = index
        self.is_mine = is_mine
        self.number_of_close_mines = number_of_close_mines
        self.is_flagged = False
        self.is_discovered = False

    def flag(self) -> None:
        self.is_flagged = True

    def unflag(self) -> None:
        self.is_flagged = False

    def __str__(self) -> str:
        if self.is_flagged:
            return 'F'
        if self.is_mine:
            return 'X'
        if self.is_discovered:
            return f'O-{self.number_of_close_mines}'
        return str(self.number_of_close_mines)


class MinesweeperGrid:
    """
    Class of the minesweeper greed
    A greed of the game is a 16x30 grid
    A greed start with 99 mines randomly placed
    """

    GRID_HEIGHT = 16
    GRID_WIDTH = 30
    GRID_START_MINES_NUMBER = 99

    def __init__(self, width: int = 30, height: int = 16, mines: int = 99):
        self.grid_width = width
        self.grid_height = height
        self.grid_start_mines_number = mines
        self.number_of_flags_left = mines
        self.number_of_well_placed_flags = 0
        self.cases = [[MineseeperGridCase([x, y], False)
                      for x in range(self.grid_width)]
                      for y in range(self.grid_height)]
        
    def init_mines(self, safe_case_index: Tuple[int, int]) -> None:
        """
        The goal of this method is to defi

        Args:
            safe_case_index (Tuple[int, int]): _description_
        """
        non_available_indexs = [safe_case_index] + \
            self.get_adjacent_cases_index(safe_case_index)
        self.place_mines(non_available_indexs)
        self.discover(safe_case_index)

    def flag(self, index: Tuple[int, int]) -> None:
        if self.cases[index[1]][index[0]].is_discovered:
            return

        if not self.cases[index[1]][index[0]].is_flagged:
            if self.number_of_flags_left == 0:
                raise ValueError('No more flags left')
            self.cases[index[1]][index[0]].is_flagged = True
            self.number_of_flags_left -= 1
            if self.cases[index[1]][index[0]].is_mine:
                self.number_of_well_placed_flags += 1
        else:
            self.cases[index[1]][index[0]].is_flagged = False
            self.number_of_flags_left += 1
            if self.cases[index[1]][index[0]].is_mine:
                self.number_of_well_placed_flags -= 1

    def discover(self, index: Tuple[int, int]) -> bool:

        case = self.get_case_by_index(index)

        self.cases[index[1]][index[0]].is_discovered = True

        if case.is_mine:
            return False

        for neighbor_case in self.get_adjacent_cases(index):
            if not neighbor_case.is_mine and not neighbor_case.is_discovered:
                if neighbor_case.number_of_close_mines == 0:
                    self.discover(neighbor_case.index)
                elif self.cases[index[1]][index[0]].number_of_close_mines == 0:
                    self.cases[neighbor_case.index[1]][neighbor_case.index[0]].is_discovered = True

        return True

    def get_adjacent_cases_index(self,
                                 index: Tuple[int, int]
                                 ) -> List[Tuple[int, int]]:
        x = index[0]
        y = index[1]

        adj_help = [[-1, -1], [0, -1], [1, -1], [-1, 0],
                    [1, 0],  [-1, 1], [0, 1], [1, 1]]

        if x == 0:
            adj_help = filter(lambda i: i[0] != -1, adj_help)
        elif x == self.grid_width - 1:
            adj_help = filter(lambda i: i[0] != 1, adj_help)

        if y == 0:
            adj_help = filter(lambda i: i[1] != -1, adj_help)
        elif y == self.grid_height - 1:
            adj_help = filter(lambda i: i[1] != 1, adj_help)

        res = []
        for i in adj_help:
            res.append((x + i[0], y + i[1]))

        return res

    def get_adjacent_cases(self,
                           index: Tuple[int, int]) -> List[MineseeperGridCase]:  
        adjacent_indexs = self.get_adjacent_cases_index(index)
        adjacent_cases: List[MineseeperGridCase] = []

        for i in adjacent_indexs:
            adjacent_cases.append(self.get_case_by_index(i))

        return adjacent_cases

    def place_mines(self, non_available_indexs: List[Tuple[int, int]]) -> None:

        all_indexs = [[x, y] 
                      for x in range(self.grid_width)
                      for y in range(self.grid_height)]

        all_indexs_available = list(
            filter(lambda i: i not in non_available_indexs, all_indexs)
            )

        mines_indexs = random.sample(all_indexs_available,
                                      k=self.grid_start_mines_number)

        for index in mines_indexs:
            self.cases[index[1]][index[0]].is_mine = True

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                adj_cases = self.get_adjacent_cases([x, y])
                count = 0
                for adj_case in adj_cases:
                    if adj_case.is_mine:
                        count += 1
                self.cases[y][x].number_of_close_mines = count

    def get_case_by_index(self, 
                          index: Tuple[int, int]) -> MineseeperGridCase:
        try:
            if self.cases is None:
                return None
            return self.cases[index[1]][index[0]]
        except Exception:
            raise ValueError(f"Error getting case for index : {index}")

    def __str__(self) -> str:
        grid_str = ''
        for y in range(self.grid_height):
            row = '|'
            for x in range(self.grid_width):
                row += f" {self.cases[y][x]} |"
            grid_str += f"{row}\n"
        return grid_str


class SelectCaseMode(Enum):
    DISCOVER = 'discover'
    FLAG = 'flag'


class GameStatus(Enum):
    WON = 'won'
    LOST = 'lost'
    ON_GOING = 'on_going'


class Game:
    """
    Main class of the minesweeper game
    """

    def __init__(self, width: int = 30, height: int = 16, mines: int = 99) -> None:
        self.grid = MinesweeperGrid(width, height, mines)
        self.lost = False
        self.grid_initialised = False

    def supposed_mines_left(self) -> int:
        return self.grid.number_of_flags_left
    
    def flags_placed(self) -> int:
        return self.grid.grid_start_mines_number - self.grid.number_of_flags_left
 
    def select_case(self, index: Tuple[int, int],
                    mode: SelectCaseMode = SelectCaseMode.DISCOVER) -> None:

        if mode == SelectCaseMode.FLAG:
            self.grid.flag(index)
        else:
            if not self.grid_initialised:
                self.grid.init_mines(index)
                self.grid_initialised = True
                return

            res = self.grid.discover(index)
            if not res:
                self.lost = True

    def check_game_status(self) -> GameStatus:

        if self.lost:
            return GameStatus.LOST

        non_mine_cases = 0
        discovered_non_mine_cases = 0
        for row in self.grid.cases:
            for case in row:
                if not case.is_mine:
                    non_mine_cases += 1
                    if case.is_discovered:
                        discovered_non_mine_cases += 1

        if discovered_non_mine_cases == non_mine_cases:
            return GameStatus.WON

        return GameStatus.ON_GOING
