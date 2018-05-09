#ifndef H_RECORD_RESULT_HPP
#define H_RECORD_RESULT_HPP
#pragma once

static inline void read_host_key(char *key, size_t key_size, char *host) {
  FILE *file = fopen("../../host.txt", "r");
  if (!file) {
    // simulation not executed on the streaming server
    return;
  }
  size_t n = fscanf(file, "%1023s", host);
  fclose(file);
  char fqdn[1024];
  int start;
  if (strncmp(host, "https://", 8) == 0)
    start = 8;
  else // assuming "http://"
    start = 7;
  strncpy(fqdn, &host[start], sizeof(fqdn));
  char *colon = strchr(fqdn, ':');
  if (colon)
    *colon = '\0';
  const char *WEBOTS_HOME = getenv("WEBOTS_HOME");
  n = strlen(WEBOTS_HOME) + 1024;
  char *filename = (char *)malloc(n);
  snprintf(filename, n, "%s/resources/web/server/key/%s", WEBOTS_HOME, "localhost");
  file = fopen(filename, "r");
  if (!file) {
    fprintf(stderr, "Error: cannot open key file '%s'\n", filename);
    free(filename);
    return;
  }
  free(filename);
  n = fread(key, 1, key_size, file);
  key[n] = '\0';
  fclose(file);
  for (n = 0; n < key_size; n++) {
    if (key[n] <= ' ') {
      key[n] = '\0';
      break;
    }
  }
}

static inline void send_result_file(size_t user_id, const std::string &competition, const std::string &file_path) {
  char key[1024];
  char host[1024];
  read_host_key(key, sizeof(key), host);
  const int l = 2048;
  char *command = (char *)malloc(l);
  snprintf(command, 2048,
           "curl %s/save_result_file.php "
           "-F \"result=@%s\" "
           "-F \"userId=%zu\" -F \"competition=%s\" -F\"key=%s\"",
           host, file_path.c_str(), user_id, competition.c_str(), key);
  printf("command %s\n", command);
  FILE *file = popen(command, "r");
  if (!file) {
    fprintf(stderr, "Error: cannot run curl.\n");
    free(command);
    return;
  }
  pclose(file);
  free(command);
}

static inline void notify_game_result(const size_t *team_id, const std::array<std::size_t, 2> &score) {
  if (score[0] <= score[1])
    // no win: nothing to do
    return;

  char key[1024];
  char host[1024];
  read_host_key(key, sizeof(key), host);
  const int l = 1024;
  char *command = (char *)malloc(l);
  snprintf(command, 1024,
           "wget -qO- "
           "--post-data=\"user1Id=%zu&user2Id=%zu&key=%s\" "
           "%s/aiwc/record.php",
          team_id[0], team_id[1], key, host);
  FILE *file = popen(command, "r");
  if (!file) {
    fprintf(stderr, "Error: cannot run wget.\n");
    free(command);
    return;
  }
  pclose(file);
  free(command);
}

#endif // H_RECORD_RESULT_HPP
