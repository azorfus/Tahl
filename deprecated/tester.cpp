#include <iostream>
#include <chrono>
#include "threadpool.hpp"

void work(int id) {
    std::cout << "Thread "<< id << ": Doing work... \n";
    std::this_thread::sleep_for (std::chrono::seconds(1));
}

int main() {
    ThreadPool t_pool(12);
    std::mutex done_mutex;
    std::condition_variable done_cv;
    int finished_threads = 0;

    for(int i = 0; i < 100; i++) {

        t_pool.do_job([&, i](){

                work(1000 + i);

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
        done_cv.wait(lock, [&]() { return finished_threads == t_pool.thread_count; }); 
    }

    return 0;
}