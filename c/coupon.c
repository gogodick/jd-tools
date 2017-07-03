#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <time.h>

#include <curl/curl.h>

struct MemoryStruct {
    char *memory;
    size_t size;
};
 
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

int jd_setup(CURL *curl, char *filename)
{
    int retcode = 0;
    struct MemoryStruct chunk;

    chunk.memory = malloc(1);  /* will be grown as needed by the realloc above */ 
    chunk.size = 0;    /* no data at this point */ 
    curl_easy_setopt(curl, CURLOPT_URL, "http://home.m.jd.com/wallet/wallet.action");
    //curl_easy_setopt(curl, CURLOPT_VERBOSE, 1L);
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

int jd_get(CURL *curl, struct MemoryStruct *chunk_ptr, char *url)
{
    int retcode = 0;

    curl_easy_setopt(curl, CURLOPT_URL, url);
    //curl_easy_setopt(curl, CURLOPT_VERBOSE, 1L);
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
    printf("%lu bytes retrieved\n", (long)chunk_ptr->size);
    return 0;
}

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
        ret = jd_get(curl, &chunk, "http://home.m.jd.com/wallet/wallet.action");
        if (ret != 0) {
            ret = 1;
            goto ERROR_EXIT;
        }
        free(chunk.memory);
        chunk.memory = malloc(1);
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
