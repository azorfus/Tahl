import chess
import math
import random
from tqdm import tqdm

exploitation_parameter = 1.414
iterations = 2

class MCTSNode:

	terminal = False
	turn = True # True for white, False for black
	simulations = 0
	score = 0.0
	chosen = False
	id = 0

	visits = 0

	children = []
	state = chess.Board()
	action = None
	untried_actions = []

	parent = None

	def __init__(self, parent=None, state=chess.Board(), action=None):
		self.parent = parent
		self.state = state
		self.action = action

		untried_actions = self.actions_to_try(state)
		terminal = self.is_terminal(state)
		turn = self.state.turn == chess.Color

	def actions_to_try(self, state):
		return state.legal_moves

	def is_terminal(self, claim_draw_t=True):
		# claim_draw is a built-in parameter for the chess.Board.outcome() function
		outcome = self.state.outcome(claim_draw=claim_draw_t)
		
		if outcome != None:
			return True

		return False	

	def is_fully_expanded(self):
		return (self.is_terminal() or len(self.untried_actions) == 0)
	
	def flower(self):
		while self.untried_actions != []:
			self._expand()
	
	def evaluate(self, given_state):
		return 10

	def best_child(self, c):
		if len(self.children) == 0:
			return None

		ucb = 0.0
		m = -1.0

		best = self.children[0]

		for child in self.children:
			q = child.score/child.simulations
			ucb = c * math.sqrt(math.log(self.simulations/child.simulations))

			if self.turn:
				ucb = ucb + q
			else:
				ucb = ucb - q

			if ucb > m:
				m = ucb
				best = child

		print(best.state)
		return best
		

	def _expand(self):
		temp_actions = self.untried_actions[1:]
		move = self.untried_actions[0]
		self.untried_actions = temp_actions

		new_state = self.state
		new_state.push(move)
		
		child = MCTSNode(parent=self, state=new_state, action=move)
		self.children = self.children.append(child)

	def _rollout(self):
		sim_state = self.state

		while self.is_terminal(sim_state) != True:
			legal_moves = self.actions_to_try(sim_state)
			move = random.choice(list(legal_moves))
			sim_state.push(move)

		score = self.evaluate(sim_state)
		return score

	def _backpropagate(self, result):
		pointer = self
		while pointer.parent is not None:
			pointer.simulations += 1
			pointer.score += result
			pointer = pointer.parent

		pointer.simulations += 1
		pointer.score += result
		
class MCTSTree:
	root = None

	def __init__(self, state):
		self.root = MCTSNode(state=state)
	
	def run_search(self, iterations):
		result = 0.0
		for i in tqdm(range(0, iterations)):
			# print("Starting iteration:", i)
			walker = self.root

			# Selection
			while not(walker.is_terminal(walker.state)) and walker.is_fully_expanded():
				# print("Stuck here")
				conservation = walker
				walker = walker.best_child(exploitation_parameter)
				if walker == None:
					walker = conservation
					break

			# Expansion
			if not walker.is_terminal(walker.state) and not(walker.is_fully_expanded()):
				walker._expand()

			# Rollout
			result = walker._rollout()

			# Backpropagate
			walker._backpropagate(result)

		self.score = result

if __name__ == "__main__":
	board = chess.Board()
	tree = MCTSTree(board)
	tree.run_search(iterations)
	print(tree.root.state)
	tree.root.best_child(exploitation_parameter)
