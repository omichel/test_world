#include "participant.hpp"

#include <fstream>
#include <iostream>

class Reporter : public aiwc::Participant {

public:
  Reporter(char **argv) : aiwc::Participant(argv) {}
  virtual ~Reporter() {}

  void init() override {
    // from here, you have access to game-specific constant information such as field dimensions
    // check example 'general_check-variables_cpp' to see what information are available

    // you can initialize some custom variables here
  }

  void update(aiwc::game_frame frame) override {


  }

  void finish(aiwc::game_frame frame) override {

    // NOTICE:
    // you can send as many reports as you want, but ONLY THE LAST ONE will be preserved for the evaluation.
    std::vector<std::string> paragraphs;

    if(frame.score[0] > frame.score[1]) {
    paragraphs.emplace_back("Team Red won the game with score "
                        + std::to_string(frame.score[0]) + ":" + std::to_string(frame.score[1]) + ". ");
    }
    else if(frame.score[0] < frame.score[1]) {
    paragraphs.emplace_back("Team Blue team won the game with score "
                        + std::to_string(frame.score[0]) + ":" + std::to_string(frame.score[1]) + ". ");
    }
    else {
    paragraphs.emplace_back("The game ended in a tie with score "
                        + std::to_string(frame.score[0]) + ":" + std::to_string(frame.score[1]) + ". ");
    }

    paragraphs.emplace_back("It was really a great match!");

    // each element of report is a paragraph.
    report(paragraphs);

  }

private: // member variable
};

int main(int argc, char **argv) {
  Reporter *participant = new Reporter(argv);
  participant->run();
  delete participant;
  return 0;
}