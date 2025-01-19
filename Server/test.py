from SudokuBoard import SudokuBoard

def main():
    sd = SudokuBoard(3)
    for line in sd.board:
        print(line)

    print()
    print()

    for line in sd.puzzle:
        print(line)


if __name__ == '__main__':
    main()
