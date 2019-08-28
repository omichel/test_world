#include "participant.hpp"

class player : public Participant {

public:
  player(char **argv) : Participant(argv) {}
  virtual ~player() {}

  void init(json info) override {
    mNumberOfRobots = info["number_of_robots"];
    for (int i = 0; i < mNumberOfRobots; ++i)
      mMaxSpeed.push_back(info["max_linear_velocity"][i]);
  }

  void update(json frame) override {
    std::vector<double> speeds;
    for (int i = 0; i < 2 * mNumberOfRobots; ++i)
      speeds.push_back(mMaxSpeed[i / 2]);
    set_speeds(speeds);
  }

private:
  std::vector<double> mMaxSpeed;
  int mNumberOfRobots;
};

int main(int argc, char **argv) {
  player *participant = new player(argv);
  participant->run();
  delete participant;
  return 0;
}
