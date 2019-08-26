#include "participant.hpp"

class RandomWalk : public Participant {

public:
  RandomWalk(char **argv) : Participant(argv) {}
  virtual ~RandomWalk() {}

  void init(json info) override {
    mNumberOfRobots = info["number_of_robots"];
    for (int i = 0; i < mNumberOfRobots; ++i)
      mMaxSpeed.push_back(info["max_linear_velocity"][i]);
  }

  void update(json frame) override {
    std::vector<double> speeds;
    for (int i = 0; i < 2 * mNumberOfRobots; ++i)
      speeds.push_back(2.0 * mMaxSpeed[i / 2] *
                       (0.5 - (double)rand() / RAND_MAX));
    setSpeeds(speeds);
  }

private:
  std::vector<double> mMaxSpeed;
  int mNumberOfRobots;
};

int main(int argc, char **argv) {
  RandomWalk *player = new RandomWalk(argv);
  player->run();
  delete player;
  return 0;
}
