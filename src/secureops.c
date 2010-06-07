/**
 * Secure operations that Opus needs to perform.
 *
 * Opus needs to do three operations in deployment that require elevated
 * permissions. They are implemented here in an executable that should be SUID
 * root. The code is short and to the point, so as to be clear there are no
 * security holes.
 *
 * The binary should be installed with root ownership, SUID bit set. It should
 * have opus group read and execute permission, but no other execute
 * permission. Nobody should have write permission.
 *
 * Returns: 0 if everything was okay
 *          1 if something went wrong
 *          2 if one but not all files failed to have permissions set
 */
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <pwd.h>
#include <sys/stat.h>
#include <errno.h>

int help()
{
    printf("Usage:\n");
    printf("Create a user and change permissions:\n");
    printf("    secureops -c <username> [file] ...\n");
    printf("Restart apache:\n");
    printf("    secureops -r\n");
    return 1;
}

int main(int argc, char **argv)
{
    // Set the real user id. Effective user-id ought to be good enough, but
    // some things check real user id I suppose
    setuid( geteuid() );
    
    if (argc < 2) {
        printf("Not enough arguments\n");
        return help();
    }
    if (strcmp(argv[1], "-r") == 0) {
        execl("/bin/sh", "/usr/sbin/apachectl", "/usr/sbin/apachectl", "graceful", (char *)NULL);
        return 1;
    }

    if (strcmp(argv[1], "-c") == 0) {
        if (argc < 3) {
            printf("Must specify a username with -c\n");
            return help();
        }
        char *username = argv[2];
        
        // Create username
        if (fork() == 0) {
            execl("/usr/sbin/useradd", "/usr/sbin/useradd",
                "-d", "/",
                "-M",
                "-N",
                "-s", "/bin/false",
                username,
                (char *)NULL);
            printf("Useradd failed to launch, errno: %d\n", errno);
            _exit(255);
        }
        int ret;
        wait(&ret);
        if (!WIFEXITED(ret) || WEXITSTATUS(ret)) {
            printf("Useradd failed\n");
            printf("Error code: %d\n", WEXITSTATUS(ret));
            return 1;
        }

        // Find the uid of the new user
        int uid;
        {
            struct passwd *passwd = getpwnam(username);
            if (!passwd) {
                printf("Couldn't get uid\n");
                return 1;
            }
            uid = passwd->pw_uid;
        }
        
        
        // Chown and chmod the following files
        int i;
        int count = 0;
        int failures = 0;
        for (i=3; i<argc; i++) {
            char *filename = argv[i];
            // Check for file or directory
            struct stat fileinfo;
            if (stat(filename, &fileinfo) != 0) {
                failures++;
                continue;
            }
            mode_t mode;
            if (S_ISDIR(fileinfo.st_mode)) {
                mode = 0700;
            } else {
                mode = 0600;
            }
            if (chown(filename, uid, -1) || chmod(filename, mode)) {
                failures++;
            }
            count++;
        }
        if (count == 0 || failures == 0)
            return 0;
        else if (failures == count)
            return 1;
        return 2;
    }
    printf("Bad mode\n");
    return help();
}
