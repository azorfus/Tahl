import chess
import math
import random
import time
from tqdm import tqdm

exploitation_parameter = 1.414
iterations = 10000
iteration_depth = 100

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

		self.untried_actions = list(self.actions_to_try(state))
		self.terminal = self.is_terminal(state)
		self.turn = self.state.turn == chess.Color

	def actions_to_try(self, state):
		return state.legal_moves

	def is_terminal(self, state_t, claim_draw_t=True):
		# claim_draw is a built-in parameter for the chess.Board.outcome() function
		outcome = state_t.outcome(claim_draw=claim_draw_t)
		if outcome is not None:
			return True

		return False	

	def is_fully_expanded(self):
		return (self.is_terminal(self.state) or len(self.untried_actions) == 0)
	
	def flower(self):
		while self.untried_actions != []:
			self._expand()
	
	def evaluate(self, given_state):
		if given_state.is_checkmate():
			if given_state.turn == chess.WHITE:
				return -1
			else:
				return 1
		return 0

	def best_child(self, c):
		if len(self.children) == 0:
			return None

		ucb = 0.0
		m = -1.0

		best = self.children[0]

		for child in self.children:
			q = (child.score/child.simulations if child.simulations != 0 else 0)
			ucb = (c * math.sqrt(math.log(self.simulations/child.simulations)) if child.simulations != 0 else 0)

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
		move = self.untried_actions.pop()

		new_state = self.state
		new_state.push(move)
		
		child = MCTSNode(parent=self, state=new_state, action=move)
		self.children = self.children.append(child)

	def _rollout(self):
		sim_state = self.state.copy()
		t = 0
		while not self.is_terminal(sim_state) and t < iteration_depth:
			legal_moves = self.actions_to_try(sim_state)
			move = random.choice(list(legal_moves))
			sim_state.push(move)
			t = t + 1

		score = self.evaluate(sim_state)
		return score

	def _backpropagate(self, result):
		self.score += result
		self.simulations += 1
		# pointer = self
		# while pointer.parent is not None:
		# 	pointer.simulations += 1
		# 	pointer.score += result
		# 	pointer = pointer.parent

		# pointer.simulations += 1
		# pointer.score += result
		
class MCTSTree:
	root = None

	def __init__(self, node):
		self.root = MCTSNode(state=node.state)
	
	def run_search(self, iterations):
		result = 0.0
		for i in tqdm(range(0, iterations)):
			# print("Starting iteration:", i)
			walker = MCTSNode(parent=None, state=self.root.state.copy(), action=None)

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
	tree.root.best_child(exploitation_parameter)
	tree.root.state.turn
