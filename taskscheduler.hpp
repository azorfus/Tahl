#include "mcts.hpp"


class TaskScheduler {

public:
    TaskScheduler(MCTSNode* root) {
        this->root = root;
    }
    ~TaskScheduler() {}

    MCTSNode* root;

    void summon_threads(int threads) {
        std::vector<std::thread> daemons;
        std::vector<std::unique_ptr<MCTSTree>> mcts_trees;

        for(int t = 0; t < threads; t++) {
            mcts_trees.push_back(std::make_unique<MCTSTree>(root->state));
            daemons.push_back(std::thread(&MCTSTree::run_search,
                              mcts_trees.back().get(), 100 /*The number of iterations each thread*/ ));
        }

        for(auto &daemon : daemons) {
            if(daemon.joinable()) daemon.join();
        }

        // Combine results from all threads
        
        
    }
}