#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <time.h>
#include <sys/time.h>
#include "wrapper.h"



int main(int argc, char* argv[]) 
{
    CURL *curl;
    int ret = 0;
    struct MemoryStruct chunk;

    if (argc < 2) {
        printf("Please specify cookie file...\n");
        exit(1);
    }
    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();
    if (curl) {
        ret = jd_setup(curl, argv[1]);
        if (ret != 0) {
            ret = 1;
            goto ERROR_EXIT;
        }
        chunk.memory = malloc(1);
        chunk.size = 0;
        set_local_time(curl);
        set_local_time(curl);
        set_local_time(curl);
        set_local_time(curl);
        set_local_time(curl);
        set_local_time(curl);
        set_local_time(curl);
        set_local_time(curl);
        set_local_time(curl);
        set_local_time(curl);
    } else {
        fprintf(stderr, "Curl init failed!\n");
        ret = 1;
        goto ERROR_EXIT;
    }
ERROR_EXIT:
    if (NULL != chunk.memory) {
        free(chunk.memory);
        chunk.memory = NULL;
    }
    curl_global_cleanup();
    return ret;
}
