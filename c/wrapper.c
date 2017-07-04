#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <time.h>
#include <sys/time.h>
#include "wrapper.h"

double time_diff = 0.0;
 
static size_t WriteMemoryCallback(void *contents, size_t size, size_t nmemb, void *userp)
{
    size_t realsize = size * nmemb;
    struct MemoryStruct *mem = (struct MemoryStruct *)userp;

    mem->memory = realloc(mem->memory, mem->size + realsize + 1);
    if(mem->memory == NULL) {
        /* out of memory! */ 
        printf("not enough memory (realloc returned NULL)\n");
        return 0;
    }
    memcpy(&(mem->memory[mem->size]), contents, realsize);
    mem->size += realsize;
    mem->memory[mem->size] = 0;
    return realsize;
}

void print_cookies(CURL *curl) 
{
    CURLcode res;
    struct curl_slist *cookies;
    struct curl_slist *nc;
    int i;

    printf("Cookies, curl knows:\n");
    res = curl_easy_getinfo(curl, CURLINFO_COOKIELIST, &cookies);
    if (res != CURLE_OK) {
        fprintf(stderr, "Curl curl_easy_getinfo failed: %s\n",
                curl_easy_strerror(res));
        return;
    }
    nc = cookies;
    i = 1;
    while (nc) {
        printf("[%d]: %s\n", i, nc->data);
        nc = nc->next;
        i++;
    }
    if (i == 1) {
        printf("(none)\n");
    }
    curl_slist_free_all(cookies);
    return;
}

void print_string(char *input, int length)
{
    int i;
    for(i = 0; i < length; i++) {
        printf("%c", input[i]);
    }
    printf("\n");
    return;
}

int find_string_start(char *input, char *start, char *end, int *pos, int *length)
{
    int i;
    int input_length = strlen(input);
    int start_length = strlen(start);
    int end_length = strlen(end);

    *pos = -1;
    *length = -1;
    for (i = 0; i < input_length; i++) {
        if (memcmp(&input[i], start, start_length) == 0) {
            *pos = i + start_length;
            break;
        }
    }
    if (*pos == -1) {
        fprintf(stderr, "Can't find start %s!\n", start);
        return 1;
    }
    for (; i < input_length; i++) {
        if (memcmp(&input[i], end, end_length) == 0) {
            *length = i - *pos;
            break;
        }
    }
    if (*length <= 0) {
        fprintf(stderr, "Can't find end %s!\n", end);
        return 1;
    }
    //print_string(&input[*pos], *length);
    return 0;
}

int find_string_end(char *input, char *start, char *end, int *pos, int *length)
{
    int i;
    int input_length = strlen(input);
    int start_length = strlen(start);
    int end_length = strlen(end);
    int end_pos = -1, start_pos = -1;
 
    for (i = 0; i < input_length; i++) {
        if (memcmp(&input[i], end, end_length) == 0) {
            end_pos = i;
            break;
        }
    }
    if (end_pos == -1) {
        fprintf(stderr, "Can't find end %s!\n", end);
        return 1;
    }
    for (i = (end_pos - start_length); i > 0; i--) {
        if (memcmp(&input[i], start, start_length) == 0) {
            start_pos = i;
            break;
        }
    }
    if (start_pos == -1) {
        fprintf(stderr, "Can't find start %s!\n", start);
        return 1;
    }
    *pos = start_pos + start_length;
    *length = end_pos - (start_pos + start_length);
    //print_string(&input[*pos], *length);
    return 0;
}

int jd_setup(CURL *curl, char *filename)
{
    int retcode = 0;
    struct MemoryStruct chunk;

    chunk.memory = malloc(1);  /* will be grown as needed by the realloc above */ 
    chunk.size = 0;    /* no data at this point */ 
    curl_easy_setopt(curl, CURLOPT_URL, "http://home.m.jd.com/wallet/wallet.action");
    curl_easy_setopt(curl, CURLOPT_VERBOSE, 0);
    /* send all data to this function  */ 
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteMemoryCallback);
    /* we pass our 'chunk' struct to the callback function */ 
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&chunk);
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1);
    /* start cookie engine */
    curl_easy_setopt(curl, CURLOPT_COOKIEFILE, filename);
    curl_easy_perform(curl);
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE , &retcode);
    free(chunk.memory);
    if (retcode != 200) {
        fprintf(stderr, "Response code is %d!\n", retcode);
        return -1;
    }
    printf("%lu bytes retrieved\n", (long)chunk.size);
    return 0;
}

int jd_get(CURL *curl, struct MemoryStruct *chunk_ptr, char *url, char *referer)
{
    int retcode = 0;

    curl_easy_setopt(curl, CURLOPT_URL, url);
    if (referer != NULL) {
        curl_easy_setopt(curl, CURLOPT_REFERER, referer);
    }
    curl_easy_setopt(curl, CURLOPT_VERBOSE, 0);
    /* send all data to this function  */ 
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteMemoryCallback);
    /* we pass our 'chunk' struct to the callback function */ 
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)chunk_ptr);
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1);
    curl_easy_perform(curl);
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE , &retcode);
    if (retcode != 200) {
        fprintf(stderr, "Response code is %d!\n", retcode);
        return -1;
    }
    return 0;
}

int jd_post(CURL *curl, struct MemoryStruct *chunk_ptr, char *url, char *data)
{
    int retcode = 0;

    curl_easy_setopt(curl, CURLOPT_URL, url);
    if (data != NULL) {
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data);
    }
    curl_easy_setopt(curl, CURLOPT_VERBOSE, 0);
    /* send all data to this function  */ 
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteMemoryCallback);
    /* we pass our 'chunk' struct to the callback function */ 
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)chunk_ptr);
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1);
    curl_easy_perform(curl);
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE , &retcode);
    if (retcode != 200) {
        fprintf(stderr, "Response code is %d!\n", retcode);
        return -1;
    }
    return 0;
}

double get_network_time(CURL *curl)
{
    struct MemoryStruct chunk;
    double nt = -1.0;
    int ret = 0;
    int pos = 0, length = 0;
    
    chunk.memory = malloc(1);
    chunk.size = 0;
    ret = jd_get(curl, &chunk, "http://a.jd.com/ajax/queryServerData.html", "http://a.jd.com");
    if (ret != 0) {
        goto ERROR_EXIT;
    }
    ret = find_string_start(chunk.memory, "{\"serverTime\":", "}", &pos, &length);
    if (ret != 0) {
        goto ERROR_EXIT;
    }
    nt = (double)atoll(&chunk.memory[pos])/1000.0;
ERROR_EXIT:
    if (NULL != chunk.memory) {
        free(chunk.memory);
        chunk.memory = NULL;
    }
    return nt;
}

void set_local_time(CURL *curl)
{
    int i = 0;
    struct timeval tv;
    double lt, nt;

    for (i = 0; i < 3; i++) {
        nt = get_network_time(curl);
        gettimeofday(&tv,NULL);
        lt = tv.tv_sec + (double)tv.tv_usec/1000000.0;
        if (nt > 0) {
            break;
        }
    }
    if (nt < 0) {
        fprintf(stderr, "Can't get network time!!!\n");
        return;
    }
    time_diff = nt - lt;
    printf("System time difference is %lf\n", time_diff);
    return;
}

double get_local_time()
{
    struct timeval tv;
    double lt;
    gettimeofday(&tv,NULL);
    lt = tv.tv_sec + (double)tv.tv_usec/1000000.0;
    return lt + time_diff;
}
