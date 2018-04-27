#ifndef H_RECORD_RESULT_HPP
#define H_RECORD_RESULT_HPP
#pragma once


static inline void notify_game_result(const size_t *team_id, const std::array<std::size_t, 2> &score) {
  /*
  char host[1024];
  FILE *file = fopen("../../host.txt", "r");
  if (!file) {
    fprintf(stderr, "Error: cannot open host file.\n");
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
    *colon = '\0';*/
  // TODO compute automatically?
  char fqdn[1024] = "localhost";
  char host[1024] = "localhost";
  const char *WEBOTS_HOME = getenv("WEBOTS_HOME");
  size_t n = strlen(WEBOTS_HOME) + 1024;
  char *filename = (char *)malloc(n);
  snprintf(filename, n, "%s/resources/web/server/key/%s", WEBOTS_HOME, fqdn);
  FILE *file = fopen(filename, "r");
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
  const int win = (score[0] > score[1]) + (score[0] < score[1]) * 2;
  const int l = 1024;
  char *command = (char *)malloc(l);
  snprintf(command, 1024,
           "wget -qO- "
           "--post-data=\"team1=%zu&team2=%zu&win=%d&key=%s\" "
           "%s/record.php",
          team_id[0], team_id[1], win, key, host);
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
