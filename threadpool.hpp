#include "mcts.hpp"
#include <thread>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <functional>

class ThreadPool {
public:

    int thread_count = 0;

    ThreadPool(int threads) : shutdown_(false) {
        thread_count = threads;
        // Launch worker threads
        for (int i = 0; i < threads; i++) {
            workers.emplace_back(&ThreadPool::thread_entry, this, i);
        }
    }

    ~ThreadPool() {
        wait_for_completion();

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
            if (shutdown_) throw std::runtime_error("ThreadPool shutting down");
            jobs.emplace([this, func]() {
                func();
                done_var.notify_one();
            });
        }
        cond_var.notify_one();
    }

    void wait_for_completion() {
        std::unique_lock<std::mutex> lock(wait_mutex);
        done_var.wait(lock, [&]() {
            return jobs.empty();
        });
    }

private:
    std::vector<std::thread> workers;
    std::queue<std::function<void()>> jobs;

    std::mutex queue_mutex;
    std::mutex wait_mutex;

    std::condition_variable cond_var;
    std::condition_variable done_var;
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
