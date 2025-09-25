#include "mcts.hpp"
#include <thread>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <functional>

class ThreadPool {

public:

    std::vector <std::thread> workers;
    std::mutex queue_mutex;
    std::queue <std::function <void (void)>> jobs;
    std::condition_variable cond_var;
    bool shutdown_;

    ThreadPool(int threads) {
        workers.reserve(threads);
        for(int i = 0; i < threads; i++) {
            workers.emplace_back(std::bind (&ThreadPool::thread_entry, this, i));
        }
    }

    ~ThreadPool ()
    {
        {
            // Unblock any threads and tell them to stop
            std::unique_lock <std::mutex> l (queue_mutex);

            shutdown_ = true;
            cond_var.notify_all();
        }

        // Wait for all threads to stop
        std::cerr << "Joining threads" << std::endl;
        for (auto& thread : workers)
            thread.join();
    }

    void do_job (std::function <void(void)> func)
    {
        // Place a job on the queue and unblock a thread
        std::unique_lock <std::mutex> l (queue_mutex);

        jobs.emplace (std::move(func));
        cond_var.notify_one();
    }

    protected:

    void thread_entry (int i)
    {
        std::function <void(void)> job;

        while (1)
        {
            {
                std::unique_lock <std::mutex> l (queue_mutex);

                while (!shutdown_ && jobs.empty())
                    cond_var.wait(l);

                if (jobs.empty())
                {
                    // No jobs to do and we are shutting down
                    std::cerr << "Thread " << i << " terminates" << std::endl;
                    return;
                 }

                std::cerr << "Thread " << i << " does a job" << std::endl;
                job = std::move (jobs.front());
                jobs.pop();
            }

            // Do the job without holding any locks
            job ();
        }

    }

};


class TaskScheduler {

public:
    TaskScheduler(MCTSNode* root) {
        this->root = root;
    }
    ~TaskScheduler() {}

    MCTSNode* root;

    int threaded_evaluate(int threads) {
        std::vector<std::thread> daemons;
        std::vector<MCTSTree*> mcts_trees;

        ThreadPool t_pool(threads);

        for(int t = 0; t < threads; t++) {
            mcts_trees.push_back(new MCTSTree(root->state));
            t_pool.do_job(std::bind(&MCTSTree::run_search, mcts_trees.back(), mcts_trees.back()->root, 100));
        }

        int best_index = indexof_best_child(mcts_trees);


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
