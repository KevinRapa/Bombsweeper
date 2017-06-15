import random
import re

#=========================================================================================
class GameController(object):
    #
    # Handles player input and ensures that the player's syntax is valid.
    # Creates and resets games as needed
    #
    
    OUTPUTS = ("You lose.", "Ok.", "You win!", "That cell is flagged")
    MAX_CELLS = 1220
    
    @staticmethod
    def createGame():
        game = GameController.__askForDifficulty()
        validInput = re.compile("(?:flag )?\d\d?(?:,|,? )\d\d?", 0 | re.I);
        delim = re.compile(",? |,")
        
        while(True):
            ans = input("Next move?\n"
                        "<x, y>: Flip a cell\n"
                        "flag <x, y>: Flag a cell\n")

            if ans and re.match(validInput, ans):
                move = re.split(delim, ans)
                
                outcome = game.makeMove(move)
            
                print(GameController.OUTPUTS[outcome])

                if (outcome == 0 or outcome == 2):
                    if input("play again? (y/n): ") == "y":
                        game = GameController.__askForDifficulty()
                    else:
                        break
            else:
                print("That isn't valid")

    #-------------------------------------------------------------------------------------
    @staticmethod
    def __askForDifficulty():
        while(True):
            ans = input("Enter difficulty 1, 2, or 3. Or, specify custom specs ([# columns], [# rows], [# bombs])")
            
            if re.match("^[123]$", ans):
                return MinesweeperGame(int(ans))
            elif re.match("\d\d?, ?\d\d?, ?\d\d?", ans):
                cols, rows, bombs = re.split(", ?", ans)

                numC, numR, numB = int(cols), int(rows), int(bombs)

                if numC * numR * numB <= 0:
                    print("You enter enter positive numbers.")
                elif numB >= numC * numR:
                    print("You must specify at least 1 empty cell!")
                elif numC * numR > GameController.MAX_CELLS:
                    print("That's too big. Max number of cells is 1,220.")
                else:
                    return MinesweeperGame(xDim = numC, yDim = numR, numBombs = numB)
            else:
                print("That isn't valid.")

#=========================================================================================         
class MinesweeperGame(object):
    def __init__(self, difficulty = None, xDim = None, yDim = None, numBombs = None):
        if difficulty:
            self.board = MinesweeperGame.createBoard(difficulty)
        else:
            self.board = Board(xDim, yDim, numBombs)
            
        print(self.board)

    #-------------------------------------------------------------------------------------
    @staticmethod
    def createBoard(difficulty):
        if difficulty == 1:
            return Board(9, 9, 10)
        elif difficulty == 2:
            return Board(16, 16, 40)
        else:
            return Board(16, 30, 99)

    #-------------------------------------------------------------------------------------
    def makeMove(self, tokenList):
        result = 1
        x, y = int(tokenList[-2]) - 1, int(tokenList[-1]) - 1

        if self.board.isValidCell(y, x) and not self.board.isFlaggedCell(y, x):
            if len(tokenList) == 3:
                self.board.flag(y, x)
            else:
                lose = self.board.flip(y, x)

                if lose:
                    result = 0
                elif self.board.won():
                    result = 2
        elif self.board.isFlaggedCell(y, x):
            result = 3

        print(self.board)
        return result

#=========================================================================================   
class Board(object):
    #
    # An array of cells. This class takes syntactically
    # valid player input and handles the array
    #

    # Index pairs for adjacent cells.
    ADJS = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (1, -1), (-1, 1))
    
    def __init__(self, xDim, yDim, bombs):
        self.cells = []
        self.xDim = xDim
        self.yDim = yDim
        numCells = xDim * yDim
        self.freeCells = numCells - bombs
        
        l = []

        for b in range(0, bombs):
            # Adds all the bomb cells to the list
            l.append(Cell(True))

        for c in range(0, numCells - bombs):
            # Adds the rest of the cells to the list
            l.append(Cell(False))

        random.shuffle(l) # Mixes the list up

        for j in range(0, yDim):
            # Distributes the list into the array
            row = []
            
            for i in range(0, xDim):
                row.append(l.pop())
                
            self.cells.append(row)

        for j in range(0, yDim):
            # These loops set the numbers for each cell next to one or more bombs
            for i in range(0, xDim):
                cell = self.cells[j][i]

                if not cell.isBomb():
                    numBombs = 0

                    def tryBomb(self, j, i):
                        # Returns 1 if the adjacent cell exists and is a bomb
                        if j < 0 or i < 0:
                            return 0
                        try:
                            if self.cells[j][i].isBomb():
                                return 1
                            else:
                                return 0
                        except:
                            return 0

                    for pair in Board.ADJS:
                        x, y = pair[0], pair[1]
                        numBombs += tryBomb(self, j + y, i + x)

                    if numBombs:
                        cell.setType(str(numBombs))

    #-------------------------------------------------------------------------------------
    def __str__(self):
        """Prints the board."""
        
        result = ""
        i = 1

        for i in range(1, self.xDim + 1):
            result += str(i) + ("" if i > 9 else " ")

        result += "\n"
        i = 1
        
        for row in self.cells:
            for cll in row:
                result += str(cll) + " "
                    
            result += " " + str(i) + "\n"
            i += 1
            
        return result

    #-------------------------------------------------------------------------------------
    def isFlaggedCell(self, y, x):
        return self.cells[y][x].isFlagged()

    #-------------------------------------------------------------------------------------
    def isValidCell(self, y, x):
        try:
            if not self.cells[y][x].isFlipped():
                return True
            else:
                print("That cell is flipped.")
                return False
        except:
            print("That isn't valid.")
            return False

    #-------------------------------------------------------------------------------------
    def flag(self, j, i):
        """Flags a cell so it can't be flipped"""
        self.cells[j][i].flag()

    #-------------------------------------------------------------------------------------
    def flip(self, j, i):
        """
        Flips a cell. When it is flipped, if it's not a bomb, adjacent cells are flipped
        recursively. Once a cell with a number is flipped or the cell is a bomb, it stops.
        """
        
        cell = self.cells[j][i]
        
        cell.flip()

        if cell.isBomb():
              return True

        self.freeCells -= 1
        
        if not cell.isEmpty():
              return False

        def notBombOrFlipped(self, j, i):
            # Checks if any adjacent cells are empty, flips them
            if j < 0 or i < 0:
                return False
            try:
                if not self.cells[j][i].isBomb() and not self.cells[j][i].isFlipped():
                    return True
                else:
                    return False
            except:
                return False

        for pair in Board.ADJS:
            x, y = pair[0], pair[1]
            
            if notBombOrFlipped(self, j + y, i + x):
                self.flip(j + y, i + x)

        return False

    #-------------------------------------------------------------------------------------
    def won(self):
        """Returns true if there are no non-bomb cells left."""
        return not self.freeCells
              
#=========================================================================================
class Cell(object):
    BOMB = "B"
    EMPTY = " "
    FLAG = "F"
    FACE_DOWN = "x"
    
    def __init__(self, isBomb):
        self.__isFaceUp = False
        self.__isFlagged = False
        
        if isBomb:
            self.__type = Cell.BOMB
        else:
            self.__type = Cell.EMPTY

    def setType(self, number):
        self.__type = number

    def isBomb(self):
        return self.__type == Cell.BOMB

    def flip(self):
        self.__isFaceUp = True

    def flag(self):
        self.__isFlagged = not self.__isFlagged

    def isMarked(self):
        return self.__type == Cell.FLAG

    def isFlagged(self):
        return self.__isFlagged
    
    def isFlipped(self):
        return self.__isFaceUp

    def isEmpty(self):
        return self.__type == Cell.EMPTY
        
    def __str__(self):
        if self.__isFaceUp:
            return self.__type
        elif self.__isFlagged:
            return Cell.FLAG
        else:
            return Cell.FACE_DOWN

#=========================================================================================           

GameController.createGame()
        
