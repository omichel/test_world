#ifndef PARTICIPANT_HPP
#define PARTICIPANT_HPP

#include "json.hpp"

using namespace nlohmann;

class Participant {

public:
  Participant(char **argv);
  virtual ~Participant();

  void setSpeeds(std::vector<double> speeds);
  void run();

  // These methods should be overrriden
  virtual void init(json info);
  virtual bool check_frame(json frame);
  virtual void update(json frame);
  virtual void finish();

private:
  void sendToServer(std::string message, std::string arguments = "");
  json receive();

  std::string mKey;
  std::string mData;
  int mConnFd;
};

#endif // PARTICIPANT_HPP
