#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <time.h>
#include <sys/time.h>
#include "wrapper.h"

int coupon_click(CURL *curl, int verbose)
{
    struct MemoryStruct chunk;
    int ret = 0;

    chunk.memory = malloc(1);
    chunk.size = 0;
    ret = jd_post(curl, &chunk, "http://coupon.m.jd.com/coupons/submit.json", NULL);
    if (ret != 0) {
        goto ERROR_EXIT;
    }
    if(verbose != 0) {
        print_string(chunk.memory, chunk.size);
    }
ERROR_EXIT:
    if (NULL != chunk.memory) {
        free(chunk.memory);
        chunk.memory = NULL;
    }
    return ret;
}

int coupon_dig(CURL *curl, char *key, char *role_id)
{
    char payload[256] = {0};
    int pos = 0, length = 0;
    struct MemoryStruct chunk;
    int ret = 0;

    chunk.memory = malloc(1);
    chunk.size = 0;
    strcat(payload, "key=");
    strcat(payload, key);
    strcat(payload, "&roleId=");
    strcat(payload, role_id);
    ret = jd_post(curl, &chunk, "http://coupon.m.jd.com/coupons/show.action", payload);
    if (ret != 0) {
        goto ERROR_EXIT;
    }
    //print_string(chunk.memory, chunk.size);
    ret = find_string_end(chunk.memory, "value=\"", "\" name=\"couponKey\"", &pos, &length);
ERROR_EXIT:
    if (NULL != chunk.memory) {
        free(chunk.memory);
        chunk.memory = NULL;
    }
    return ret;
}

int main(int argc, char* argv[]) 
{
    CURL *curl;
    int ret = 0;

    if (argc < 4) {
        printf("Please specify cookie file, key and role_id\n");
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
        ret = coupon_dig(curl, argv[2], argv[3]);
        if (ret != 0) {
            ret = 1;
            goto ERROR_EXIT;
        }
        set_local_time(curl);
        coupon_click(curl, 1);
    } else {
        fprintf(stderr, "Curl init failed!\n");
        ret = 1;
        goto ERROR_EXIT;
    }
ERROR_EXIT:
    curl_global_cleanup();
    return ret;
}
