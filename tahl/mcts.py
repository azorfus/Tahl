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

	parent = MCTSNode()

	def __init__(self, parent=None, state=None, action=None):
		self.parent = parent
		self.state = state
		self.action = action

		untried_actions = actions_to_try(state)
		terminal = is_terminal(state)
		turn = state.turn() == chess.Color.WHITE

	def actions_to_try(state):
		return state.legal_moves()

	def is_terminal(state, claim_draw=True):
		outcome = state.outcome(claim_draw)
		
		if outcome != None:
			return True

		return False	
	
	def is_fully_expanded(self):
		return (self.is_terminal() and self.untried_actions.empty())
	
	def flower(self):
		while self.untried_actions != []:
			self._expand()
	
	def _expand(self):
		temp_actions = self.untried_actions[1:]
		move = self.untried_actions[0]
		self.untried_actions = temp_actions

		new_state = self.state
		new_state.push(move)
		
		child = MCTSNode(self, new_state)
		self.children = self.children.append(child)

	def _rollout():
		sim_state = state

		while self.is_terminal(sim_state) != True:
			legal_moves = actions_to_try(sim_state)
			move = legal_moves[randint(0, len(legal_moves) - 1)]
			sim_state.push(move)
		
