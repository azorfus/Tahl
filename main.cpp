#include <iostream>
#include "threadpool.hpp"


int threaded_evaluate(MCTSNode* root, ThreadPool* t_pool) {

    root->flower();

    std::mutex done_mutex;
    std::condition_variable done_cv;
    int finished_threads = 0;

    std::vector < std::shared_ptr<MCTSTree> > mcts_trees;
    for(int i = 0; i < root->children.size(); i++) {
        mcts_trees.emplace_back(std::make_shared<MCTSTree>(root->children[i]->state));
    }

    for(int i = 0; i < mcts_trees.size(); i++) {
        /*
            t_pool->do_job(std::bind(&MCTSTree::run_search, mcts_trees[i], mcts_trees[i]->root, 1000));

            Not ideal for waiting for the jobs to finish in our case. 
            Instead of writing an external explicit function to lock mutex
            and wait for completion of work, We could just use Lambda functions as shown.
        */

        /* 
            The following lambda does two things with the same thread execution, runs the search
            and then runs the scoped code to wait for the entire lambda to finish.
        */
        
        t_pool->do_job([&, i](){

            mcts_trees[i]->run_search(mcts_trees[i]->root, 1000);

            {
                std::lock_guard <std::mutex> lock(done_mutex);
                finished_threads = finished_threads + 1;
                done_cv.notify_one();
            }

        });
    }

    // Wait until all threads are finished 
    { 
        std::unique_lock<std::mutex> lock(done_mutex); 
        done_cv.wait(lock, [&]() { return finished_threads == t_pool->thread_count; }); 
    }

    int max = 0;
    for(int i = 0; i < mcts_trees.size(); i++) {
        std::cout << "Child " << i << " Score: " << mcts_trees[i]->root->score << std::endl;
        if(mcts_trees[i]->root->score > mcts_trees[max]->root->score) {
            max = i;
        }
    }

    return max;

}

int main() {
    // Start position
    chess::Board board = chess::Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
    // chess::Board board = chess::Board("5r2/8/1R6/ppk3p1/2N3P1/P4b2/1K6/5B2 w - - 0 1");

    // Root node (no parent, initial board, no move leading to it)
    MCTSNode* root = new MCTSNode(nullptr, board, chess::Move());

    // Create a thread pool with 8 threads.
    ThreadPool t_pool(8);

    // Index of the best child
    int best_index = threaded_evaluate(root, &t_pool);

    // Get best child node from root
    if (best_index >= 0 && best_index < (int)root->children.size()) {
        std::shared_ptr<MCTSNode> best_child = root->children[best_index];
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
