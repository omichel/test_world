#include "participant.hpp"

class RandomWalk : public aiwc::Participant {

public:
  RandomWalk(char **argv) : aiwc::Participant(argv) {}
  virtual ~RandomWalk() {}

  void init(json info) override {
    number_of_robots = info["number_of_robots"];
    for (int i = 0; i < number_of_robots; ++i)
      max_linear_velocity.push_back(info["max_linear_velocity"][i]);
  }

  void update(json frame) override {
    std::vector<double> speeds;
    for (int i = 0; i < 2 * number_of_robots; ++i)
      speeds.push_back(2.0 * max_linear_velocity[i / 2] *
                       (0.5 - (double)rand() / RAND_MAX));
    set_speeds(speeds);
  }

  void finish() override {

  }

private:
  std::vector<double> max_linear_velocity;
  int number_of_robots;
};

int main(int argc, char **argv) {
  RandomWalk *player = new RandomWalk(argv);
  player->run();
  delete player;
  return 0;
}
