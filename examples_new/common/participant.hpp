#ifndef PARTICIPANT_HPP
#define PARTICIPANT_HPP

#include "json.hpp"

using namespace nlohmann;

class Participant {

public:
  Participant(char **argv);
  virtual ~Participant();

  void set_speeds(std::vector<double> speeds);
  void run();

  // These methods should be overrriden
  virtual void init(json info);
  virtual bool check_frame(json frame);
  virtual void update(json frame);
  virtual void finish();

private:
  void send_to_server(std::string message, std::string arguments = "");
  json receive();

  std::string key;
  std::string datapath;
  int conn_fd;
};

#endif // PARTICIPANT_HPP
