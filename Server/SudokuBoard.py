import copy
import random
from copy import deepcopy


class SudokuGenerator:
    def __init__(self):
        self.grid = [[0] * 9 for _ in range(9)]

    def is_valid(self, row, col, num):
        """Check if a number can be placed in (row, col)"""
        for i in range(9):
            if self.grid[row][i] == num or self.grid[i][col] == num:
                return False

        # Check 3x3 box
        box_x, box_y = (row // 3) * 3, (col // 3) * 3
        for i in range(3):
            for j in range(3):
                if self.grid[box_x + i][box_y + j] == num:
                    return False
        return True

    def solve(self):
        """Backtracking solver to fill or verify grid"""
        for row in range(9):
            for col in range(9):
                if self.grid[row][col] == 0:
                    for num in range(1, 10):
                        if self.is_valid(row, col, num):
                            self.grid[row][col] = num
                            if self.solve():
                                return True
                            self.grid[row][col] = 0
                    return False
        return True

    def generate_full_grid(self):
        """Create a fully filled valid Sudoku grid"""
        self.grid = [[0] * 9 for _ in range(9)]
        self.solve()
        self.shuffle_grid()

    def shuffle_grid(self):
        """Shuffle the complete Sudoku grid while keeping validity"""
        for _ in range(10):  # Apply multiple random transformations
            self.swap_rows()
            self.swap_columns()
            self.swap_row_blocks()
            self.swap_column_blocks()

    def swap_rows(self):
        """Swap two random rows within the same block"""
        block = random.randint(0, 2) * 3
        row1, row2 = random.sample(range(block, block + 3), 2)
        self.grid[row1], self.grid[row2] = self.grid[row2], self.grid[row1]

    def swap_columns(self):
        """Swap two random columns within the same block"""
        block = random.randint(0, 2) * 3
        col1, col2 = random.sample(range(block, block + 3), 2)
        for row in range(9):
            self.grid[row][col1], self.grid[row][col2] = self.grid[row][col2], self.grid[row][col1]

    def swap_row_blocks(self):
        """Swap two 3-row blocks"""
        block1, block2 = random.sample([0, 3, 6], 2)
        for i in range(3):
            self.grid[block1 + i], self.grid[block2 + i] = self.grid[block2 + i], self.grid[block1 + i]

    def swap_column_blocks(self):
        """Swap two 3-column blocks"""
        block1, block2 = random.sample([0, 3, 6], 2)
        for row in range(9):
            for i in range(3):
                col1, col2 = block1 + i, block2 + i
                self.grid[row][col1], self.grid[row][col2] = self.grid[row][col2], self.grid[row][col1]

    def count_solutions(self):
        """Check if the puzzle has a unique solution"""
        grid_copy = deepcopy(self.grid)
        return self.count_solutions_helper(grid_copy)

    def count_solutions_helper(self, grid, count=0):
        """Recursive helper to count solutions"""
        for row in range(9):
            for col in range(9):
                if grid[row][col] == 0:
                    for num in range(1, 10):
                        if self.is_valid(row, col, num):
                            grid[row][col] = num
                            count = self.count_solutions_helper(grid, count)
                            if count > 1:
                                return count
                            grid[row][col] = 0
                    return count
        return count + 1

    def remove_numbers(self, attempts=50):
        """Remove numbers while keeping a unique solution"""
        positions = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(positions)

        for row, col in positions:
            backup = self.grid[row][col]
            self.grid[row][col] = 0

            if self.count_solutions() != 1:
                self.grid[row][col] = backup
            else:
                attempts -= 1
                if attempts == 0:
                    break

    def generate_puzzle(self, difficulty="medium"):
        """Generate a shuffled Sudoku puzzle with a unique solution"""
        self.generate_full_grid()
        attempts = {"easy": 40, "medium": 50, "hard": 60}.get(difficulty, 50)
        solution_grid = copy.deepcopy(self.grid)
        self.remove_numbers(attempts)
        return solution_grid, self.grid

    @staticmethod
    def get_empty_cells(grid):
        """Get the list of empty cells in the grid"""
        return [(r, c) for r in range(9) for c in range(9) if grid[r][c] == 0]
