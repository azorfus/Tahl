import mcts
import nnet

node1 = mcts.MCTSNode()
tree = mcts.MCTSTree(node1)
# tree.run_search(500)

shapes = [[4, 1],
		  [4, 1],
		  [4, 1],
		  [4, 1]];

net = nnet.Network(2, shapes)
net.forward_prop(1)
net.check()
