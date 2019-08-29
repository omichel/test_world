#include "participant.hpp"

#include "game.hpp"

#include <stdio.h>

#ifdef _WIN32
#include <winsock.h>
#else
#include <arpa/inet.h>  /* definition of inet_ntoa */
#include <sys/socket.h>
#include <unistd.h> /* definition of close */
#endif

Participant::Participant(char **argv) {
  int port = std::stoi(argv[2], nullptr);
  key = argv[3];
  datapath = argv[4];

  #ifdef _WIN32
    /* initialize the socket api */
    WSADATA info;

    int rc = WSAStartup(MAKEWORD(1, 1), &info); /* Winsock 1.1 */
    if (rc != 0) {
      fprintf(stderr, "Cannot initialize Winsock\n");
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
    printf("socket creation failed...\n");
    exit(0);
  }

  // connect the client socket to server socket
  if (connect(conn_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) !=
      0) {
    fprintf(stderr, "Connection with the server failed\n");
    exit(0);
  }
}

Participant::~Participant() {
#ifdef _WIN32
  closesocket(conn_fd);
#else
  if (shutdown(conn_fd, SHUT_RDWR) == -1 || close(conn_fd) == -1)
    fprintf(stderr, "Failed to shutdown connection with the server\n");
#endif
}

void Participant::send_to_server(std::string message, std::string arguments) {
  std::string toSend = "aiwc." + message + "(\"" + key + "\"";
  if (arguments.size() > 0)
    toSend += ", " + arguments;
  toSend += ")";
  const char *toSendString = toSend.c_str();
  send(conn_fd, (void *)toSendString, strlen(toSendString) * sizeof(char), 0);
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

void Participant::set_speeds(std::vector<double> speeds) {
  std::string arguments = "";
  for (unsigned i = 0; i < speeds.size(); i++)
    arguments += std::to_string(speeds[i]) + ", ";
  arguments = arguments.substr(0, arguments.size() - 2);
  send_to_server("set_speeds", arguments);
}

bool Participant::check_frame(json frame) {
  if (frame.find("reset_reason") != frame.end() &&
      frame["reset_reason"] == RESET_GAME_END)
    return false;
  return true;
}

void Participant::init(json info) { printf("init() method called...\n"); }

void Participant::update(json frame) { printf("update() method called...\n"); }

void Participant::finish() { printf("finish() method called...\n"); }

void Participant::run() {
  send_to_server("get_info");
  init(receive());
  send_to_server("ready");

  while (true) {
    json frame = receive();
    if (!frame.empty()) {
      if (check_frame(frame)) // return false if we need to quit
        update(frame);
      else
        break;
    } else
      break;
  }

  finish();
  return;
}
