#include "participant.hpp"

class Player : public aiwc::Participant {

public:
  Player(char **argv) : aiwc::Participant(argv) {}
  virtual ~Player() {}

  void init(json info) override {
    number_of_robots = info["number_of_robots"];
    for (int i = 0; i < number_of_robots; ++i)
      max_linear_velocity.push_back(info["max_linear_velocity"][i]);
  }

  void update(json frame) override {
    std::vector<double> speeds;
    for (int i = 0; i < 2 * number_of_robots; ++i)
      speeds.push_back(max_linear_velocity[i / 2]);
    set_speeds(speeds);
  }

  void finish() override {

  }

private:
  std::vector<double> max_linear_velocity;
  int number_of_robots;
};

int main(int argc, char **argv) {
  Player *participant = new Player(argv);
  participant->run();
  delete participant;
  return 0;
}
