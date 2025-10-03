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
    ThreadPool* pool;

    TaskScheduler(MCTSNode* root, ThreadPool* pool) {
        this->root = root;
        this->pool = pool;
    }
    ~TaskScheduler() {}

    int threaded_evaluate() {
        std::vector<MCTSTree*> mcts_trees;
        mcts_trees.reserve(threads);

        ThreadPool pool(threads);

        std::mutex mtx;


        
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
