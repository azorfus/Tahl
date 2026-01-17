import chess
import random

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

	def is_terminal(self, state, claim_draw_t=True):
		# claim_draw is a built-in parameter for the chess.Board.outcome() function
		outcome = self.state.outcome(claim_draw=claim_draw_t)
		
		if outcome != None:
			return True

		return False	

	def is_fully_expanded(self):
		return (self.is_terminal() and self.untried_actions.empty())
	
	def flower(self):
		while self.untried_actions != []:
			self._expand()
	
	def evaluate(self, given_state):
		return 10

	def _expand(self):
		temp_actions = self.untried_actions[1:]
		move = self.untried_actions[0]
		self.untried_actions = temp_actions

		new_state = self.state
		new_state.push(move)
		
		child = MCTSNode(self, new_state)
		self.children = self.children.append(child)

	def _rollout(self):
		sim_state = self.state

		while self.is_terminal(sim_state) != True:
			legal_moves = self.actions_to_try(sim_state)
			move = legal_moves[randint(0, len(legal_moves) - 1)]
			sim_state.push(move)

		score = self.evaluate(sim_state)
		return score

	def _backpropagate(self, result):
		pointer = self
		while pointer != None:
			pointer.simulations += 1
			pointer.score += result
			pointer = pointer.parent
		
class MCTSTree:

