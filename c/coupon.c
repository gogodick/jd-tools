#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <time.h>
#include <sys/time.h>
#include "wrapper.h"

#define COUPON_PAYLOAD_SIZE 1024
char coupon_payload[COUPON_PAYLOAD_SIZE] = {0};

int coupon_click(CURL *curl)
{
    struct MemoryStruct chunk;
    int ret = 0;

    chunk.memory = malloc(1);
    chunk.size = 0;
    ret = jd_post(curl, &chunk, "http://coupon.m.jd.com/coupons/submit.json", coupon_payload);
    if (ret != 0) {
        goto ERROR_EXIT;
    }
    print_string(chunk.memory, chunk.size);
ERROR_EXIT:
    if (NULL != chunk.memory) {
        free(chunk.memory);
        chunk.memory = NULL;
    }
    return ret;
}

int coupon_click_fast(CURL *curl)
{
    return jd_post_fast(curl, NULL, "http://coupon.m.jd.com/coupons/submit.json", coupon_payload);
}

int coupon_dig(CURL *curl, char *key, char *role_id)
{
    char payload[256] = {0};
    char sid[64] = {0};
    char codeKey[64] = {0};
    char validateCode[64] = {0};
    char couponKey[64] = {0};
    char activeId[64] = {0};
    char couponType[64] = {0};
    int pos = 0, length = 0;
    struct MemoryStruct chunk;
    int ret = 0;

    chunk.memory = malloc(1);
    chunk.size = 0;
    snprintf(payload, sizeof(payload), "key=%s&roleId=%s", key, role_id);
    ret = jd_post(curl, &chunk, "http://coupon.m.jd.com/coupons/show.action", payload);
    if (ret != 0) {
        goto ERROR_EXIT;
    }
    //print_string(chunk.memory, chunk.size);
    ret = find_string_start(chunk.memory, "input id=\"sid\" type=\"hidden\" value=\"", "\"/", &pos, &length);
    if (0 == ret) {
        memcpy(sid, &chunk.memory[pos], length);
    }
    ret = find_string_end(chunk.memory, "\"", "\" name=\"codeKey\"", &pos, &length);
    if (0 == ret) {
        memcpy(codeKey, &chunk.memory[pos], length);
    }
    ret = find_string_end(chunk.memory, "\"", "\" name=\"validateCodeSign\"", &pos, &length);
    if (0 == ret) {
        memcpy(validateCode, &chunk.memory[pos], length);
    }
    ret = find_string_end(chunk.memory, "\"", "\" name=\"couponKey\"", &pos, &length);
    if (0 == ret) {
        memcpy(couponKey, &chunk.memory[pos], length);
    }
    ret = find_string_end(chunk.memory, "\"", "\" name=\"activeId\"", &pos, &length);
    if (0 == ret) {
        memcpy(activeId, &chunk.memory[pos], length);
    }
    ret = find_string_end(chunk.memory, "\"", "\" name=\"couponType\"", &pos, &length);
    if (0 == ret) {
        memcpy(couponType, &chunk.memory[pos], length);
    }
    memset(coupon_payload, 0, COUPON_PAYLOAD_SIZE);
    snprintf(coupon_payload, COUPON_PAYLOAD_SIZE, "sid=%s&codeKey=%s&validateCode=%s&roleId=%s&key=%s&couponKey=%s&activeId=%s&couponType=%s",
        sid, codeKey, validateCode, role_id, key, couponKey, activeId, couponType);
    //print_string(coupon_payload, strlen(coupon_payload));    
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
    int hour = 0, minute = 0, process = 0;
    int ret = 0;

    if (argc < 7) {
        printf("Please specify cookie file, key, role_id, hour, minute and process\n");
        exit(1);
    }
    hour = atoi(argv[4]);
    minute = atoi(argv[5]);
    process = atoi(argv[6]);
    printf("main: %d, %d, %d\n", hour, minute, process);
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
        coupon_click_fast(curl);
        coupon_click_fast(curl);
        coupon_click_fast(curl);
        coupon_click(curl);
    } else {
        fprintf(stderr, "Curl init failed!\n");
        ret = 1;
        goto ERROR_EXIT;
    }
ERROR_EXIT:
    curl_global_cleanup();
    return ret;
}
