#ifndef H_RECORD_RESULT_HPP
#define H_RECORD_RESULT_HPP
#pragma once


static inline void notify_game_result(const size_t *team_id, const std::array<std::size_t, 2> &score) {
  if (score[0] <= score[1])
    // no win: nothing to do
    return;

  char host[1024];
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
  snprintf(filename, n, "%s/resources/web/server/key/%s", WEBOTS_HOME, fqdn);
  file = fopen(filename, "r");
  if (!file) {
    fprintf(stderr, "Error: cannot open key file '%s'\n", filename);
    free(filename);
    return;
  }
  free(filename);
  char key[1024];
  n = fread(key, 1, sizeof(key), file);
  key[n] = '\0';
  fclose(file);
  for (n = 0; n < sizeof(key); n++) {
    if (key[n] <= ' ') {
      key[n] = '\0';
      break;
    }
  }
  const int l = 1024;
  char *command = (char *)malloc(l);
  snprintf(command, 1024,
           "wget -qO- "
           "--post-data=\"user1Id=%zu&user2Id=%zu&key=%s\" "
           "%s/record.php",
          team_id[0], team_id[1], key, host);
  file = popen(command, "r");
  if (!file) {
    fprintf(stderr, "Error: cannot run wget.\n");
    free(command);
    return;
  }
  pclose(file);
  free(command);
}

#endif // H_RECORD_RESULT_HPP
