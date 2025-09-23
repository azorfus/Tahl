#include "mcts.hpp"


class TaskScheduler {

public:
    TaskScheduler(MCTSNode* root) {
        this->root = root;
    }
    ~TaskScheduler() {}

    MCTSNode* root;

    /* I don't think this version is correct 
    void summon_threads(int threads) {
        std::vector<std::thread> daemons;
        std::vector<std::unique_ptr<MCTSTree>> mcts_trees;

        for(int t = 0; t < threads; t++) {
            mcts_trees.push_back(std::make_unique<MCTSTree>(root->state));
            daemons.push_back(std::thread(&MCTSTree::run_search,
                              mcts_trees.back().get(), 100));
        }

        for(auto &daemon : daemons) {
            if(daemon.joinable()) daemon.join();
        }

        // Combine results from all threads
        
        
    }
    */

    MCTSNode* threaded_evaluate(int threads) {
        std::vector<std::thread> daemons;
        std::vector<MCTSTree*> mcts_trees;

        for(int t = 0; t < threads; t++) {
            mcts_trees.push_back(new MCTSTree(root->children->at(t)->state));
            daemons.push_back(std::thread(&MCTSTree::run_search,
                              mcts_trees.back(), 100));
        }

        for(auto &daemon : daemons) {
            if(daemon.joinable()) daemon.join();
        }

        MCTSNode* best = best_child(mcts_trees);

        clean_up(mcts_trees);
        
        return best;
        
    }

    void clean_up(std::vector<MCTSTree*> mcts_trees) {
        for(auto tree : mcts_trees) {
            delete tree;
        }
    }

    MCTSNode* best_child(std::vector<MCTSTree*> mcts_trees) {
        MCTSNode* best = mcts_trees[0]->root;

        for(auto tree : mcts_trees) {
            if(best->score < tree->root->score) {
                best = tree->root;
            }
        }

        return best;
    }
};