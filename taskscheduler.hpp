#include "mcts.hpp"
#include <thread>
#include <mutex>

class ThreadPool {

    std::vector <std::thread> workers;
    std::mutex queue_mutex;
    std::queue <std::function <void (void)>> jobs;
    std::condition_variable cond_var;
    bool shutdown_;

    ThreadPool(int threads) {
        workers.reserve(threads);
        for(int i = 0; i < threads; i++) {
            workers.emplace_back(std::thread(std::function<void()>));
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

    void doJob (std::function <void (void)> func)
    {
        // Place a job on the queu and unblock a thread
        std::unique_lock <std::mutex> l (queue_mutex);

        jobs.emplace (std::move (func));
        cond_var.notify_one();
    }

    protected:

    void threadEntry (int i)
    {
        std::function <void (void)> job;

        while (1)
        {
            {
                std::unique_lock <std::mutex> l (queue_mutex);

                while (! shutdown_ && jobs.empty())
                    cond_var.wait (l);

                if (jobs.empty ())
                {
                    // No jobs to do and we are shutting down
                    std::cerr << "Thread " << i << " terminates" << std::endl;
                    return;
                 }

                std::cerr << "Thread " << i << " does a job" << std::endl;
                job = std::move (jobs.front ());
                jobs.pop();
            }

            // Do the job without holding any locks
            job ();
        }

    }

}








/*
class TaskScheduler {

public:
    TaskScheduler(MCTSNode* root) {
        this->root = root;
    }
    ~TaskScheduler() {}

    MCTSNode* root;

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

*/