import mcts

node1 = mcts.MCTSNode()
tree = mcts.MCTSTree(node1)
tree.run_search(500)
print(tree.root.state)
