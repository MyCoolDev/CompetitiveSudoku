import random
import copy


class SudokuBoard:
    def __init__(self, base):
        self.base = base
        self.board = self.generate_grid(self.base)
        self.puzzle = self.create_puzzle(copy.deepcopy(self.board))

    @staticmethod
    def generate_grid(base: int):
        side = base * base

        # pattern for a baseline valid solution
        def pattern(r, c): return (base * (r % base) + r // base + c) % side

        # randomize rows, columns and numbers (of valid base pattern)
        from random import sample
        def shuffle(s): return sample(s, len(s))

        rBase = range(base)
        rows = [g * base + r for g in shuffle(rBase) for r in shuffle(rBase)]
        cols = [g * base + c for g in shuffle(rBase) for c in shuffle(rBase)]
        nums = shuffle(range(1, base * base + 1))

        # produce board using randomized baseline pattern
        board = [[nums[pattern(r, c)] for c in cols] for r in rows]

        return board

    def create_puzzle(self, board):
        side = self.base ** 2
        squares = side * side
        empties = squares * 3 // 4
        for p in random.sample(range(squares), empties):
            board[p // side][p % side] = 0

        return board
