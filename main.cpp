#include <iostream>
#include "threadpool.hpp"

int main() {
    // Start position
    chess::Board board = chess::Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
    // chess::Board board = chess::Board("5r2/8/1R6/ppk3p1/2N3P1/P4b2/1K6/5B2 w - - 0 1");

    // Root node (no parent, initial board, no move leading to it)
    MCTSNode* root = new MCTSNode(nullptr, board, chess::Move());

    TaskScheduler threader(root, 4);

    int best_index = threader.threaded_evaluate();

    // Get best child node from root
    if (best_index >= 0 && best_index < (int)root->children.size()) {
        MCTSNode* best_child = root->children[best_index];
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
