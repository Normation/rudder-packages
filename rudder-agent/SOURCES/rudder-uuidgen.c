#include <stdio.h>
#include <uuid/uuid.h>

int main(int argc, char *argv[]) {
        // uuid structure
        uuid_t uuid;
        // more than enough to print an uuid
        char text[100];
        // generate and print
        uuid_generate_time(uuid);
        uuid_unparse(uuid,text);
        printf("%s\n", text);
        return 0;
}

