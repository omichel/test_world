#include "participant.hpp"

#include <iostream>

class Commentator : public aiwc::Participant {

public:
  Commentator(char **argv) : aiwc::Participant(argv) {}
  virtual ~Commentator() {}

  void init() override {
    // from here, you have access to game-specific constant information such as field dimensions
    // check example 'general_check-variables_cpp' to see what information are available

    // you can initialize some custom variables here
  }

  void update(aiwc::game_frame frame) override {
    if(frame.reset_reason == aiwc::GAME_START) {
      if(!frame.half_passed)
        commentate("Game has begun");
      else
        commentate("Second half has begun");
      return;
    }
    else if(frame.reset_reason == aiwc::DEADLOCK) {
      commentate("Position is reset since no one touched the ball");
      return;
    }
    else if(frame.reset_reason == aiwc::GOALKICK) {
      commentate("A goal kick of Team " + std::string(frame.ball_ownership ? "Red" : "Blue"));
    }
    else if(frame.reset_reason == aiwc::CORNERKICK) {
      commentate("A corner kick of Team " + std::string(frame.ball_ownership ? "Red" : "Blue"));
    }
    else if(frame.reset_reason == aiwc::PENALTYKICK) {
      commentate("A penalty kick of Team " + std::string(frame.ball_ownership ? "Red" : "Blue"));
    }
    else if(frame.reset_reason == aiwc::HALFTIME) {
      if(frame.score[0] > frame.score[1])
        commentate("The halftime has met. Team Red is leading the game with score " + std::to_string(frame.score[0]) + " : " + std::to_string(frame.score[1]));
      else if(frame.score[0] < frame.score[1])
        commentate("The halftime has met. Team Blue is leading the game with score " + std::to_string(frame.score[1]) + " : " + std::to_string(frame.score[0]));
      else
        commentate("The halftime has met. The game is currently a tie with score " + std::to_string(frame.score[0]) + " : " + std::to_string(frame.score[1]));
    }
    else if(frame.reset_reason == aiwc::GAME_END) {
      if(frame.score[0] > frame.score[1])
        commentate("Team Red won the game with score " + std::to_string(frame.score[0]) + " : " + std::to_string(frame.score[1]));
      else if(frame.score[0] < frame.score[1])
        commentate("Team Blue won the game with score " + std::to_string(frame.score[1]) + " : " + std::to_string(frame.score[0]));
      else
        commentate("Game ended in a tie with score "  + std::to_string(frame.score[0]) + " : " + std::to_string(frame.score[1]));
      return;
    }

    if(frame.coordinates.ball.x >= info.field[X] / 2 && std::abs(frame.coordinates.ball.y) <= info.goal[Y] / 2) {
      commentate("Team Red scored!!");
    }
    else if(frame.coordinates.ball.x <= -info.field[X] / 2 && std::abs(frame.coordinates.ball.y) <= info.goal[Y] / 2) {
      commentate("Team Blue scored!!");
    }

    // const auto& ateam0_x      = frame.coordinates.robots[ATEAM][0].x;
    // const auto& bteam0_active = frame.coordinates.robots[BTEAM][0].active;
  }

  void finish() override {

  }

private: // member variable
};

int main(int argc, char **argv) {
  Commentator *participant = new Commentator(argv);
  participant->run();
  delete participant;
  return 0;
}
