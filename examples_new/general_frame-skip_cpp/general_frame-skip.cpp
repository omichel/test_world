#include "participant.hpp"

#include <condition_variable>
#include <iostream>
#include <mutex>
#include <random>
#include <thread>

class FrameSkip : public aiwc::Participant {

public:
  FrameSkip(char **argv) : aiwc::Participant(argv) {}
  virtual ~FrameSkip() {}

  void init() override {
    // initialize a thread that will do the main job of data analysis, decision making, etc.
    behavior_thread = std::thread([&]() { frame_skip(); });
  }

  void update(aiwc::game_frame frame) override {
    std::unique_lock<std::mutex> lck(frames.m);
    // whenever a frame is received from the server, the frame is pushed into a queue
    frames.q.push_back(frame);
    lck.unlock();
    frames.cv.notify_one();
  }

  void frame_skip()
  {
    // this function runs in the behavior thread to do operations
    for(;;) {
      std::unique_lock<std::mutex> lck(frames.m);
      // wait until some data appears in the queue
      frames.cv.wait(lck, [&]() { return !frames.q.empty(); });

      std::vector<aiwc::game_frame> local_queue;
      // take the data into a local queue and empty the shared queue
      local_queue.swap(frames.q);
      lck.unlock();

      // you can ignore all frames but the most recent one,
      // or keep only resetting frames,
      // or do whatever you want.

      // this example keeps only the most recent frame.
      choose_behavior_which_takes_really_long_time(local_queue.back());

      if(local_queue.back().reset_reason == aiwc::GAME_END) {
        break;
      }
    }
  }

  void choose_behavior_which_takes_really_long_time(const aiwc::game_frame& frame)
  {
    if(frame.reset_reason == aiwc::GAME_END) {
      return;
    }

    // heavy operations
    std::this_thread::sleep_for(std::chrono::seconds(3));

    // now send data to the server.
    std::cout << "Long operation ended." << std::endl;
  }

  void finish() override {

  }

  private: // member variable
    std::thread behavior_thread;

    struct {
      std::vector<aiwc::game_frame> q;
      std::mutex m;
      std::condition_variable cv;
    } frames;
};

int main(int argc, char **argv) {
  FrameSkip *participant = new FrameSkip(argv);
  participant->run();
  delete participant;
  return 0;
}
