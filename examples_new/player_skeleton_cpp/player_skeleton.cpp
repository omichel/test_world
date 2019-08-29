#include "participant.hpp"

class Player : public aiwc::Participant {

public:
  Player(char **argv) : aiwc::Participant(argv) {}
  virtual ~Player() {}

  void init() override {
    // from here, you have access to game-specific constant information such as field dimensions
    // check example 'general_check-variables_cpp' to see what information are available

    // you can initialize some custom variables here
  }

  void update(json frame) override {
    std::vector<double> speeds;
    for (unsigned int i = 0; i < 2 * info.number_of_robots; ++i)
      speeds.push_back(info.max_linear_velocity[i / 2]);
    set_speeds(speeds);
  }

  void finish() override {

  }

private: // member variable
};

int main(int argc, char **argv) {
  Player *participant = new Player(argv);
  participant->run();
  delete participant;
  return 0;
}
