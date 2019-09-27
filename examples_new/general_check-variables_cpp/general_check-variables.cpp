#include "participant.hpp"

#include <iostream>

class CheckVariables : public aiwc::Participant {

public:
  CheckVariables(char **argv) : aiwc::Participant(argv) {}
  virtual ~CheckVariables() {}

  void init() override {
    // from here, you have access to game-specific constant information such as field dimensions

    // Print received constant variables to the console
    std::cout << "======================================================" << std::endl;
    std::cout << "Game Time: " << info.game_time << " seconds" << std::endl;
    std::cout << "# of robots: " << info.number_of_robots << " robots" << std::endl;
    std::cout << "======================================================" << std::endl;
    std::cout << "Field Dimensions: " << info.field[X] << " m long, " << info.field[Y] << " m wide" << std::endl;
    std::cout << "Goal Dimensions: " << info.goal[X] << " m deep, " << info.goal[Y] << " m wide" << std::endl;
    std::cout << "Penalty Area Dimensions: " << info.penalty_area[X] << " m long, " << info.penalty_area[Y] << " m wide" << std::endl;
    std::cout << "Goal Area Dimensions: " << info.goal_area[X] << " m long, " << info.goal_area[Y] << " m wide" << std::endl;
    std::cout << "Image Resolution: " << info.resolution[X] << " x " << info.resolution[Y] << std::endl;
    std::cout << "======================================================" << std::endl;
    std::cout << "Ball Radius: " << info.ball_radius << " m" << std::endl;
    std::cout << "Ball Mass: " << info.ball_mass << " kg" << std::endl;
    std::cout << "======================================================" << std::endl;
    for (unsigned int i = 0; i < info.number_of_robots; i++) {
      std::cout << "Robot " << i << ":" << std::endl;
      std::cout << "  size: " << info.robot_size[i] << " m x " << info.robot_size[i] << " m" << std::endl;
      std::cout << "  height: " << info.robot_height[i] << " m" << std::endl;
      std::cout << "  axle length: " << info.axle_length[i] << " m" << std::endl;
      std::cout << "  body mass: " << info.robot_body_mass[i] << " kg" << std::endl;
      std::cout << "  wheel radius: " << info.wheel_radius[i] << " m" << std::endl;
      std::cout << "  wheel mass: " << info.wheel_mass[i] << " kg" << std::endl;
      std::cout << "  max linear velocity: " << info.max_linear_velocity[i] << " m/s" << std::endl;
      std::cout << "  max torque: " << info.max_torque[i] << " N*m" << std::endl;
      std::cout << "  codeword: " << info.codewords[i] << std::endl;
      std::cout << "======================================================" << std::endl;
    }
  }

  void update(aiwc::game_frame frame) override {
    if(frame.reset_reason == aiwc::GAME_START) {
      std::cout << "Game started : " << frame.time << std::endl;
    }
    if(frame.reset_reason == aiwc::SCORE_MYTEAM) {
      std::cout << "My team scored : " << frame.time << std::endl;
      std::cout << "Current Score: [" << frame.score[MYTEAM] << ", " << frame.score[OPPONENT] << "]" << std::endl;
    }
    else if(frame.reset_reason == aiwc::SCORE_OPPONENT) {
      std::cout << "Opponent scored : " << frame.time << std::endl;
      std::cout << "Current Score: [" << frame.score[MYTEAM] << ", " << frame.score[OPPONENT] << "]" << std::endl;
    }
    else if(frame.reset_reason == aiwc::HALFTIME) {
      std::cout << "Halftime" << std::endl;
    }
    else if(frame.reset_reason == aiwc::EPISODE_END) {
      std::cout << "Episode ended" << std::endl;
    }
    else if(frame.reset_reason == aiwc::GAME_END) {
      // game is finished. finish() will be called after you return.
      // now you have about 30 seconds before this process is killed.
      std::cout << "Game ended : " << frame.time << std::endl;
      return;
    }

    std::cout << "Halftime passed? " << frame.half_passed << std::endl;

    if(frame.game_state == aiwc::STATE_KICKOFF)
      std::cout << "Kickoff [My kickoff? " << frame.ball_ownership << "]" << std::endl;
    else if(frame.game_state == aiwc::STATE_GOALKICK)
      std::cout << "Goalkick [My goalkick? " << frame.ball_ownership << "]" << std::endl;
    else if(frame.game_state == aiwc::STATE_CORNERKICK)
      std::cout << "Cornerkick [My cornerkick? " << frame.ball_ownership << "]" << std::endl;
    else if(frame.game_state == aiwc::STATE_PENALTYKICK)
      std::cout << "Penaltykick [My penaltykick? " << frame.ball_ownership << "]" << std::endl;

    const auto& myteam   = frame.coordinates.robots[MYTEAM];
    // const auto& opponent = frame.coordinates.robots[OPPONENT];
    const auto& ball     = frame.coordinates.ball;

    std::cout << "======================================================" << std::endl;
    std::cout << "Ball: (" << ball.x << ", " << ball.y << ")" << std::endl;
    std::cout << "======================================================" << std::endl;

    // Try replace 'myteam' with 'opponent' to check opponent robots' state
    for (unsigned int i = 0; i < info.number_of_robots; i++) {
      std::cout << "Robot " << i << ":" << std::endl;
      std::cout << "  position: (" << myteam[i].x << ", " << myteam[i].y << ")" << std::endl;
      std::cout << "  orientation: " << myteam[i].th << std::endl;
      std::cout << "  activeness: " << myteam[i].active << std::endl;
      std::cout << "  touch: " << myteam[i].touch << std::endl;
      std::cout << "======================================================" << std::endl;
    }

    std::vector<double> speeds;
    for (unsigned int i = 0; i < 2 * info.number_of_robots; ++i)
      speeds.push_back(0);
    set_speeds(speeds);
  }

  void finish(aiwc::game_frame frame) override {

  }

private: // member variable
};

int main(int argc, char **argv) {
  CheckVariables *participant = new CheckVariables(argv);
  participant->run();
  delete participant;
  return 0;
}
