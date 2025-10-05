#include <iostream>
#include "threadpool.hpp"


int threaded_evaluate(MCTSNode* root, ThreadPool* t_pool) {

    root->flower();

    std::vector <MCTSTree*> mcts_trees;
    for(int i = 0; i < root->children->size(); i++) {
        mcts_trees.emplace_back(new MCTSTree(root->children->at(i)->state));
    }

    for(int i = 0; i < mcts_trees.size(); i++) {
        t_pool->do_job(std::bind(&MCTSTree::run_search, mcts_trees[i], mcts_trees[i]->root, 1000));
    }

    int max = 0;
    for(int i = 0; i < mcts_trees.size(); i++) {
        if(mcts_trees[i]->root->score > mcts_trees[max]->root->score) {
            max = i;
        }
    }

    return max;

}

int main() {
    // Start position
    chess::Board board = chess::Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");

    // Root node (no parent, initial board, no move leading to it)
    MCTSNode* root = new MCTSNode(nullptr, board, chess::Move());

    // Create a thread pool with 4 threads.
    ThreadPool t_pool(4);

    // Index of the best child
    int best_index = threaded_evaluate(root, &t_pool);

    // Get best child node from root
    if (best_index >= 0 && best_index < (int)root->children->size()) {
        MCTSNode* best_child = root->children->at(best_index);
        std::cout << "Best index: " << best_index << std::endl;
        std::cout << "Best move found: " 
                  << chess::uci::moveToUci(best_child->action) 
                  << std::endl;
    } else {
        std::cout << "No best move found!" << std::endl;
    }

    delete root; // cleanup 
    return 0;
}
