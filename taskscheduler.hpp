#include "mcts.hpp"
#include <thread>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <functional>

class ThreadPool {
public:
    ThreadPool(int threads) : shutdown_(false) {
        // Launch worker threads
        for (int i = 0; i < threads; i++) {
            workers.emplace_back(&ThreadPool::thread_entry, this, i);
        }
    }

    ~ThreadPool() {
        {
            // Tell workers to shut down
            std::unique_lock<std::mutex> lock(queue_mutex);
            shutdown_ = true;
        }
        cond_var.notify_all(); // wake all workers

        for (auto& thread : workers) {
            if (thread.joinable())
                thread.join();
        }
    }

    // Submit a job to the pool
    void do_job(std::function<void()> func) {
        {
            std::unique_lock<std::mutex> lock(queue_mutex);
            jobs.emplace(std::move(func));
        }
        cond_var.notify_one(); // wake one worker
    }

private:
    std::vector<std::thread> workers;
    std::queue<std::function<void()>> jobs;

    std::mutex queue_mutex;
    std::condition_variable cond_var;
    bool shutdown_;

    void thread_entry(int id) {
        while (true) {
            std::function<void()> job;

            {
                std::unique_lock<std::mutex> lock(queue_mutex);

                // Wait until there is a job or shutdown is true
                cond_var.wait(lock, [&]() {
                    return shutdown_ || !jobs.empty();
                });

                if (shutdown_ && jobs.empty()) {
                    // Graceful exit
                    std::cerr << "Thread " << id << " exits\n";
                    return;
                }

                // Take one job
                job = std::move(jobs.front());
                jobs.pop();
            }

            // Run the job (outside the lock!)
            job();
        }
    }
};


class TaskScheduler {

public:

    MCTSNode* root;

    TaskScheduler(MCTSNode* root) {
        this->root = root;
    }
    ~TaskScheduler() {}

    int threaded_evaluate(int threads) {
        ThreadPool t_pool(threads);

        std::vector<MCTSTree*> mcts_trees;
        mcts_trees.reserve(threads);

        // Create trees
        for (int t = 0; t < threads; t++) {
            mcts_trees.push_back(new MCTSTree(root->state));
        }

        // Run them in parallel
        std::mutex done_mutex;
        std::condition_variable done_cv;
        int finished = 0;

        for (int t = 0; t < threads; t++) {
            
            /*

                [&]() {}
                [&, t]() {}
                
                These are lambda capture lists. In the first case: [&] means "capture all variables by reference".
                and hence whenever the lambda is called, it will reference the original values and modify the
                original variables.
                
                In the seecond case: [&, t] means "capture all variables by reference, except t which is captured by value".
                This is important because t is modified in the loop, and if we captured it by reference, all threads would
                see the same (last) value of t. By capturing it by value, each thread gets its own copy of t as it was when the lambda was created.

            */
            
            t_pool.do_job([&, t]() {
                mcts_trees[t]->run_search(mcts_trees[t]->root, 1000); // iterations per thread
                {
                    std::lock_guard<std::mutex> lock(done_mutex);
                    finished++;
                    done_cv.notify_one();
                }
            });
        }

        // Wait until all trees finish
        // This scope is defined for C++ RAII, so that the lock
        // is released when we leave the scope
        {
            std::unique_lock<std::mutex> lock(done_mutex);
            done_cv.wait(lock, [&]() { return finished == threads; });
        }

        // ---- MERGE RESULTS ----
        for (auto& child : *(root->children)) {
            child->visits = 0;
            child->score  = 0;
        }

        for (auto tree : mcts_trees) {
            for (size_t i = 0; i < root->children->size(); i++) {
                root->children->at(i)->visits += tree->root->children->at(i)->visits;
                root->children->at(i)->score  += tree->root->children->at(i)->score;
            }
        }

        // Pick best child by merged stats
        int best_index = 0;
        double best_score = -1e9;
        for (size_t i = 0; i < root->children->size(); i++) {
            if (root->children->at(i)->visits > best_score) {
                best_score = root->children->at(i)->visits; 
                best_index = i;
            }
        }

        clean_up(mcts_trees);
        return best_index;
    }


    void clean_up(std::vector<MCTSTree*> mcts_trees) {
        for(auto tree : mcts_trees) {
            delete tree;
        }
    }

    int indexof_best_child(const std::vector<MCTSTree*>& mcts_trees) {
        if (mcts_trees.empty()) return -1;

        int best_index = 0;
        MCTSNode* best = mcts_trees[0]->root;

        for (size_t i = 1; i < mcts_trees.size(); ++i) {
            if (mcts_trees[i]->root->score > best->score) {
                best = mcts_trees[i]->root;
                best_index = i;
            }
        }

        return best_index;
    }

};
