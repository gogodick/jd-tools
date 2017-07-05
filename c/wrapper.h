#include <curl/curl.h>

struct MemoryStruct {
    char *memory;
    size_t size;
};

void print_cookies(CURL *curl);
void print_string(char *input, int length);
int find_string_start(char *input, char *start, char *end, int *pos, int *length);
int find_string_end(char *input, char *start, char *end, int *pos, int *length);
int jd_setup(CURL *curl, char *filename);
int jd_get(CURL *curl, struct MemoryStruct *chunk_ptr, char *url, char *referer);
int jd_post(CURL *curl, struct MemoryStruct *chunk_ptr, char *url, char *data);
int jd_post_fast(CURL *curl, struct MemoryStruct *chunk_ptr, char *url, char *data);
double get_network_time(CURL *curl);
void set_local_time(CURL *curl);
double get_local_time();
void format_local_time(int *hourp, int *minutep, int *secondp);
double compare_local_time(double target);
