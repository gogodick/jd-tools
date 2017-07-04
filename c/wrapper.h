#include <curl/curl.h>

struct MemoryStruct {
    char *memory;
    size_t size;
};

void print_cookies(CURL *curl);
void print_string(char *input, int length);
int find_string(char *input, char *start, char *end, int *pos, int *length);
int jd_setup(CURL *curl, char *filename);
int jd_get(CURL *curl, struct MemoryStruct *chunk_ptr, char *url, char *referer);
double get_network_time(CURL *curl);
void set_local_time(CURL *curl);
double get_local_time();


