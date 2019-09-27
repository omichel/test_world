#include "participant.hpp"

#include <iostream>

class RandomWalk : public aiwc::Participant {

public:
  RandomWalk(char **argv) : aiwc::Participant(argv) {}
  virtual ~RandomWalk() {}

  void init() override {
    // from here, you have access to game-specific constant information such as field dimensions
    // check example 'general_check-variables_cpp' to see what information are available

    // you can initialize some custom variables here
  }

  void update(aiwc::game_frame frame) override {
    std::vector<double> speeds;
    for (unsigned int i = 0; i < 2 * info.number_of_robots; ++i)
      speeds.push_back(2.0 * info.max_linear_velocity[i / 2] *
                       (0.5 - (double)rand() / RAND_MAX));
    set_speeds(speeds);
  }

  void finish(aiwc::game_frame frame) override {

  }

private: // member variable
};

int main(int argc, char **argv) {
  RandomWalk *player = new RandomWalk(argv);
  player->run();
  delete player;
  return 0;
}
