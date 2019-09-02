#ifndef PARTICIPANT_HPP
#define PARTICIPANT_HPP

#include "json.hpp"

using namespace nlohmann;

namespace aiwc {

  struct robot_coordinate
  {
    double x;
    double y;
    double th;
    bool active;
    bool touch;
  };

  struct ball_coordinate
  {
    double x;
    double y;
  };

  struct aiwc_coordinates
  {
    std::array<std::vector<robot_coordinate>, 2> robots;
    ball_coordinate ball;
  };

  struct game_info
  {
    std::array<double, 2> field;        // [x, y]
    std::array<double, 2> goal;         // [x, y]
    std::array<double, 2> penalty_area; // [x, y]
    std::array<double, 2> goal_area;    // [x, y]

    double ball_radius;         // m
    double ball_mass;           // kg

    std::array<double, 5> robot_size;          // [m, m, m, m, m]
    std::array<double, 5> robot_height;        // [m, m, m, m, m]
    std::array<double, 5> axle_length;         // [m, m, m, m, m]
    std::array<double, 5> robot_body_mass;     // [kg, kg, kg, kg, kg]

    std::array<double, 5> wheel_radius;        // [m, m, m, m, m]
    std::array<double, 5> wheel_mass;          // [kg, kg, kg, kg, kg]

    std::array<double, 5> max_linear_velocity; // [m/s, m/s, m/s, m/s, m/s]
    std::array<double, 5> max_torque;          // [N*m, N*m, N*m, N*m, N*m]

    std::array<std::size_t, 2> resolution; // [x, y]
    std::size_t number_of_robots;
    std::vector<std::size_t> codewords;
    double game_time;
  };

  enum reset_reason {
    NONE           = 0,
    GAME_START     = 1,
    SCORE_MYTEAM   = 2,
    SCORE_OPPONENT = 3,
    GAME_END       = 4,
    DEADLOCK       = 5,
    GOALKICK       = 6,
    CORNERKICK     = 7,
    PENALTYKICK    = 8,
    HALFTIME       = 9,
    EPISODE_END    = 10,

    // aliases
    SCORE_ATEAM = SCORE_MYTEAM,
    SCORE_BTEAM = SCORE_OPPONENT,
  };

  enum game_state {
    STATE_DEFAULT = 0,
    STATE_KICKOFF = 1,
    STATE_GOALKICK = 2,
    STATE_CORNERKICK = 3,
    STATE_PENALTYKICK = 4,
  };

  struct subimage
  {
    std::size_t x;
    std::size_t y;
    std::size_t w;
    std::size_t h;

    std::string base64;
  };

  struct frame
  {
    double time;
    std::array<std::size_t, 2> score; // [my team, opponent] for player, [a team, b team] for commentator
    std::size_t reset_reason;
    std::size_t game_state;
    bool ball_ownership;
    bool half_passed;

    std::vector<subimage> subimages;

    aiwc_coordinates coordinates;
  };

  class Participant {

  public:
    Participant(char **argv);
    virtual ~Participant();

    void set_speeds(std::vector<double> speeds);
    void run();

    // These methods should be overrriden
    virtual void init();
    virtual bool check_frame(json frame);
    virtual void update(json frame);
    virtual void finish();

    aiwc::game_info info;

  private:
    void send_to_server(std::string message, std::string arguments = "");
    json receive();
    void parse_game_info(json raw_info);

    std::string key;
    std::string datapath;
    int conn_fd;
  };

} // namespace aiwc

#endif // PARTICIPANT_HPP
