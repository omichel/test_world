#include "participant.hpp"

#include <iostream>

#ifdef _WIN32
#include <winsock.h>
#else
#include <arpa/inet.h>  /* definition of inet_ntoa */
#include <sys/socket.h>
#include <unistd.h> /* definition of close */
#endif

namespace aiwc {

  Participant::Participant(char **argv) {
    int port = std::stoi(argv[2], nullptr);
    key = argv[3];
    datapath = argv[4];

    #ifdef _WIN32
      /* initialize the socket api */
      WSADATA info;

      int rc = WSAStartup(MAKEWORD(1, 1), &info); /* Winsock 1.1 */
      if (rc != 0) {
        std::cerr << "Cannot initialize Winsock" << std::endl;
        exit(0);
      }
    #endif

    struct sockaddr_in server_addr = {0};

    // assign IP, PORT
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr(argv[1]);
    server_addr.sin_port = htons(port);

    // create the socket
    conn_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (conn_fd == -1) {
      std::cout << "socket creation failed..." << std::endl;
      exit(0);
    }

    // connect the client socket to server socket
    if (connect(conn_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) !=
        0) {
      std::cerr << "Connection with the server failed" << std::endl;
      exit(0);
    }
  }

  Participant::~Participant() {
  #ifdef _WIN32
    closesocket(conn_fd);
  #else
    if (shutdown(conn_fd, SHUT_RDWR) == -1 || close(conn_fd) == -1)
      std::cerr << "Failed to shutdown connection with the server" << std::endl;
  #endif
  }

  void Participant::send_to_server(std::string message, std::string arguments) {
    std::string toSend = "aiwc." + message + "(\"" + key + "\"";
    if (arguments.size() > 0)
      toSend += ", " + arguments;
    toSend += ")";
    const char *toSendString = toSend.c_str();
    send(conn_fd, toSendString, strlen(toSendString) * sizeof(char), 0);
  }

  json Participant::receive() {
    std::string completeBuffer;
    do {
      char buffer[4097];
      memset(buffer, '\0', sizeof(buffer));
      recv(conn_fd, buffer, sizeof(buffer) - 1, 0);
      completeBuffer += buffer;
    } while (completeBuffer.back() != '}');
    return json::parse(completeBuffer.c_str());
  }

  void Participant::parse_game_info(json raw_info) {
    info.field = raw_info["field"];
    info.goal = raw_info["goal"];
    info.penalty_area = raw_info["penalty_area"];
    info.goal_area = raw_info["goal_area"];

    info.ball_radius = raw_info["ball_radius"];
    info.ball_mass = raw_info["ball_mass"];

    info.robot_size = raw_info["robot_size"];
    info.robot_height = raw_info["robot_height"];
    info.axle_length= raw_info["axle_length"];
    info.robot_body_mass= raw_info["robot_body_mass"];
    info.wheel_radius = raw_info["wheel_radius"];
    info.wheel_mass= raw_info["wheel_mass"];
    info.max_linear_velocity= raw_info["max_linear_velocity"];
    info.max_torque = raw_info["max_torque"];

    info.resolution = raw_info["resolution"];
    info.number_of_robots = raw_info["number_of_robots"];
    info.codewords = raw_info["codewords"];
    info.game_time = raw_info["game_time"];
  }

  aiwc::game_frame Participant::parse_frame(json raw_frame) {
    aiwc::game_frame frame;

    frame.time = raw_frame["time"];
    frame.score = raw_frame["score"];
    frame.reset_reason = raw_frame["reset_reason"];
    frame.game_state = raw_frame["game_state"];
    frame.ball_ownership = raw_frame["ball_ownership"];
    frame.half_passed = raw_frame["half_passed"];

    // subimages
    for (unsigned int i = 0; i < raw_frame["subimages"].size(); i++) {
      aiwc::subimage subimage = {
        raw_frame["subimages"][i][0],
        raw_frame["subimages"][i][1],
        raw_frame["subimages"][i][2],
        raw_frame["subimages"][i][3],
        raw_frame["subimages"][i][4]
      };
      frame.subimages.push_back(subimage);
    }

    // each team
    for (int i = 0; i < 2; i++) {
      // each robot
      for (int j = 0; j < 5; j++) {
        // robot coordinate
        frame.coordinates.robots[i][j].x = raw_frame["coordinates"][i][j][X];
        frame.coordinates.robots[i][j].y = raw_frame["coordinates"][i][j][Y];
        frame.coordinates.robots[i][j].th = raw_frame["coordinates"][i][j][TH];
        frame.coordinates.robots[i][j].active = raw_frame["coordinates"][i][j][ACTIVE];
        frame.coordinates.robots[i][j].touch = raw_frame["coordinates"][i][j][TOUCH];
      }
    }

    // ball coordinate
    frame.coordinates.ball.x = raw_frame["coordinates"][2][X];
    frame.coordinates.ball.y = raw_frame["coordinates"][2][Y];

    return frame;
  }

  void Participant::set_speeds(std::vector<double>& speeds) {
    std::string arguments = "";
    for (unsigned i = 0; i < speeds.size(); i++)
      arguments += std::to_string(speeds[i]) + ", ";
    arguments = arguments.substr(0, arguments.size() - 2);
    send_to_server("set_speeds", arguments);
  }

  void Participant::commentate(const std::string& comment) {
    send_to_server("commentate", "\"" + comment + "\"");
  }

  void Participant::report(const std::vector<std::string>& rep) {

  }

  bool Participant::check_frame(json raw_frame) {
    if (raw_frame.find("reset_reason") != raw_frame.end() &&
        raw_frame["reset_reason"] == GAME_END)
      return false;
    return true;
  }

  void Participant::init() { std::cout << "init() method called... " << std::endl; }

  void Participant::update(aiwc::game_frame frame) { std::cout << "update() method called..." << std::endl; }

  void Participant::finish() { std::cout << "finish() method called..." << std::endl; }

  void Participant::run() {
    send_to_server("get_info");

    // parse the received json into game_info format
    parse_game_info(receive());

    init();

    send_to_server("ready");

    while (true) {
      json raw_frame = receive();
      if (!raw_frame.empty()) {
        if (check_frame(raw_frame)) { // return false if we need to quit
          // parse the received json into game_frame format
          auto frame = parse_frame(raw_frame);
          update(frame);
        }
        else
          break;
      } else
        break;
    }

    finish();
    return;
  }

} // namespace aiwc
