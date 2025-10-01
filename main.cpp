#include <iostream>
#include "taskscheduler.hpp"

/*
int main(){
    chess::Board board = chess::Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
    MCTSTree *tree = new MCTSTree(board);

    std::cout<<board;
    bool turn=true;

    while (!board.isInsufficientMaterial() && !board.isRepetition() && !board.isHalfMoveDraw() && !(board.getHalfMoveDrawType().first==chess::GameResultReason::CHECKMATE) && !(board.getHalfMoveDrawType().first==chess::GameResultReason::STALEMATE)){
        if (turn){
            chess::Move best = tree->run_search(num_iterations);
            board.makeMove(best);
            std::cout<<board;
            turn = false;
            delete tree;
        }
        else{
            std::string s; std::cin>>s;
            board.makeMove(chess::uci::uciToMove(board, s));
            std::cout<<board;
            MCTSTree *tree = new MCTSTree(board);
            turn = true;
        }
    }
}
*/
/*
int main() {
    chess::Board board = chess::Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
    MCTSNode* root = new MCTSNode(nullptr, board, chess::Move());
    TaskScheduler scheduler(root);

    // MCTSNode* best = scheduler.threaded_evaluate(4);
    int best_index = scheduler.threaded_evaluate(4);
    std::cout << "Best index: " << best_index << std::endl;
    // std::cout << "Best move found: " << chess::uci::moveToUci(best->action) << std::endl;
} */

int main() {
    // Start position
    chess::Board board = chess::Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");

    // Root node (no parent, initial board, no move leading to it)
    MCTSNode* root = new MCTSNode(nullptr, board, chess::Move());

    // Expand root so it has children before we start parallel search
    root->expand();

    // Scheduler for running threaded MCTS
    TaskScheduler scheduler(root);

    // Run search with 4 threads
    int best_index = scheduler.threaded_evaluate(4);

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

    delete root; // cleanup (depending on your node ownership model)
    return 0;
}
