######################################################################
# Do not add any print statements to this file
######################################################################

import random
import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG

pp.infotext = 'name="pbrain-pyrandom", author="Jan Stransky", version="1.0", country="Czech Republic", www="https://github.com/stranskyjan/pbrain-pyrandom"'

MAX_BOARD = 100
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]


######################################################################
# Helper Functions
######################################################################

def is_free(x, y):
	return x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] == 0

def is_connected(x, y):
	for i in range(0, 3):
		for j in range(0, 3):
			if x + i - 1 >= 0 and x + i - 1 < pp.width and y + j - 1 >= 0 and y + j - 1 < pp.height:
				# print(x + i - 1, ' ', y + j - 1, ' ', board[x + i - 1][y + j - 1])
				if board[x + i - 1][y + j - 1] > 0:
					return True
	return False

def position_val(x, y):
	if x < 0 or x >= pp.width or y < 0 or y >= pp.height:
		return -1
	return board[x][y]

def position_val_oppo(x, y):
	if x < 0 or x >= pp.width or y < 0 or y >= pp.height:
		return -1
	return 3 - board[x][y] if board[x][y] in [1, 2] else board[x][y]

def list_contains(l1, l2):
	for i in range(0, len(l1) - len(l2) + 1):
		j = 0
		while j < len(l2):
			if l1[i+j] != l2[j]:
				break
			j += 1
		if j == len(l2):
			return True

	return False

def get_best_move():
	logDebug("Get best move")
	logDebug(format_board(board))
	# determine the list of valid moves
	validMoves = []
	for x in range(0, pp.width):
		for y in range(0, pp.height):
			if is_free(x, y) and is_connected(x, y):
				validMoves.append((x, y))
	logDebug(str(validMoves))
	if not validMoves:
		logDebug("no valid moves")
		# assume this is because no piece on board
		return pp.width // 2, pp.height // 2
		# pp.pipeOut("DEBUG {} coordinates didn't hit an empty field")

	# winning patterns
	fiveLine = [1, 1, 1, 1, 1]
	fourLine = [0, 1, 1, 1, 1, 0]

	# strong patterns
	fourLineBlocked = [ [2, 1, 1, 1, 1], [1, 1, 1, 1, 2] ]
	threeLine = [
		[0, 1, 1, 1, 0],
		[0, 1, 1, 0, 1, 0], [0, 1, 0, 1, 1, 0]
	]

	bestMove = None
	possibleMoves = []
	for x, y in validMoves:
		logDebug(str(x) + ", " + str(y))
		board[x][y] = 1
		allPatterns = []
		# horizontal line
		allPatterns.append([position_val(x, y+i-4) for i in range(0, 9)])
		# vertical line
		allPatterns.append([position_val(x+i-4, y) for i in range(0, 9)])
		# diagonal line \
		allPatterns.append([position_val(x+i-4, y+i-4) for i in range(0, 9)])
		# diagonal line /
		allPatterns.append([position_val(x+i-4, y-i+4) for i in range(0, 9)])
		board[x][y] = 0 
		logDebug(format_list(allPatterns))
	
		for pattern in allPatterns:
			if list_contains(pattern, fiveLine):
				return (x, y)
			elif list_contains(pattern, fourLine):
				bestMove = (x, y)
			else:
				for line in threeLine + fourLineBlocked:
					if list_contains(pattern, line):
						possibleMoves.append((x, y))
						break

	# check if we need to block an opponent's move
	blockMove = None
	logDebug("Block patterns")
	logDebug(format_board(board))
	for x in range(0, pp.width):
		for y in range(0, pp.height):
			if is_free(x, y):
				logDebug(str(x) + ", " + str(y))
				board[x][y] = 2
				allPatterns = []
				# horizontal line
				allPatterns.append([position_val_oppo(x, y+i-4) for i in range(0, 9)])
				# vertical line
				allPatterns.append([position_val_oppo(x+i-4, y) for i in range(0, 9)])
				# diagonal line \
				allPatterns.append([position_val_oppo(x+i-4, y+i-4) for i in range(0, 9)])
				# diagonal line /
				allPatterns.append([position_val_oppo(x+i-4, y-i+4) for i in range(0, 9)])
				board[x][y] = 0
				logDebug(format_list(allPatterns))

				for pattern in allPatterns:
					if list_contains(pattern, fiveLine):
						return (x, y)
					elif list_contains(pattern, fourLine):
						blockMove = (x, y)

	logDebug(str(bestMove))
	logDebug(str(blockMove))
	logDebug(str(possibleMoves))
	if bestMove:
		return bestMove
	elif blockMove:
		return blockMove
	elif possibleMoves:
		return possibleMoves[0]
	else:
		return validMoves[random.randint(0, len(validMoves))]

def format_board(board):
	return format_list(r[0:pp.height] for r in board[0:pp.width])


def format_list(board):
	return '\n'.join([' '.join(str(s) for s in row) for row in board])

######################################################################
# The Brain
######################################################################

def brain_init():
	logDebug("Braininit")	
	logDebug("Brain restart")
	if pp.width < 5 or pp.height < 5:
		pp.pipeOut("ERROR size of the board")
		return
	if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
		pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
		return
	pp.pipeOut("OK")

def brain_restart():
	logDebug("Brain restart")
	for x in range(pp.width):
		for y in range(pp.height):
			board[x][y] = 0
	pp.pipeOut("OK")

def brain_my(x, y):
	logDebug("Brain my")
	if is_free(x,y):
		board[x][y] = 1
	else:
		pp.pipeOut("ERROR my move [{},{}]".format(x, y))

def brain_opponents(x, y):
	logDebug("Brain opponent")
	if is_free(x,y):
		board[x][y] = 2
	else:
		pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))

def brain_block(x, y):
	logDebug("Brain block")
	if is_free(x,y):
		board[x][y] = 3
	else:
		pp.pipeOut("ERROR winning move [{},{}]".format(x, y))

def brain_takeback(x, y):
	logDebug("Brain takeback")
	if x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] != 0:
		board[x][y] = 0
		return 0
	return 2

def brain_turn():
	logDebug("Brain turn")
	if pp.terminateAI:
		return
	x, y = get_best_move()
	logDebug("Best move: " + str(x) + " " + str(y))
	pp.do_mymove(x, y)	

def brain_end():
	pass

def brain_about():
	pp.pipeOut(pp.infotext)

if DEBUG_EVAL:
	import win32gui
	def brain_eval(x, y):
		# TODO check if it works as expected
		wnd = win32gui.GetForegroundWindow()
		dc = win32gui.GetDC(wnd)
		rc = win32gui.GetClientRect(wnd)
		c = str(board[x][y])
		win32gui.ExtTextOut(dc, rc[2]-15, 3, 0, None, c, ())
		win32gui.ReleaseDC(wnd, dc)

######################################################################
# A possible way how to debug brains.
# To test it, just "uncomment" it (delete enclosing """)
######################################################################
# define a file for logging ...
DEBUG_LOGFILE = "G:\My Drive\Tech\Reinforcement Learning\Gomoku\log\pbrain-naive.log"
# ...and clear it initially
with open(DEBUG_LOGFILE,"w") as f:
	pass

# define a function for writing messages to the file
def logDebug(msg):
	with open(DEBUG_LOGFILE,"a") as f:
		f.write(msg+"\n")
		f.flush()

# define a function to get exception traceback
def logTraceBack():
	import traceback
	with open(DEBUG_LOGFILE,"a") as f:
		traceback.print_exc(file=f)
		f.flush()
	raise

# use logDebug wherever
# use try-except (with logTraceBack in except branch) to get exception info
# an example of problematic function
"""
def brain_turn():
	logDebug("some message 1")
	try:
		logDebug("some message 2")
		1. / 0. # some code raising an exception
		logDebug("some message 3") # not logged, as it is after error
	except:
		logTraceBack()
"""
######################################################################

# "overwrites" functions in pisqpipe module
pp.brain_init = brain_init
pp.brain_restart = brain_restart
pp.brain_my = brain_my
pp.brain_opponents = brain_opponents
pp.brain_block = brain_block
pp.brain_takeback = brain_takeback
pp.brain_turn = brain_turn
pp.brain_end = brain_end
pp.brain_about = brain_about
if DEBUG_EVAL:
	pp.brain_eval = brain_eval


DEBUG = False
def main():
	if DEBUG:
		pp.width = 7
		pp.height = 6
		global board
		board =[
			[0, 0, 0, 0, 0, 0],
			[0, 1, 0, 0, 0, 0],
			[0, 0, 2, 0, 0, 0],
			[0, 0, 1, 2, 0, 0],
			[1, 1, 2, 2, 0, 0],
			[0, 2, 0, 1, 2, 0],
			[0, 0, 0, 0, 0, 0]
		]
		print(format_board(board))
		# print(list_contains([-1, -1, -1, 0, 1, 1, 1, 1, 0], [0, 1, 1, 1, 1, 0]))
		print(get_best_move())
	else:
		pp.main()

if __name__ == "__main__":
	main()
