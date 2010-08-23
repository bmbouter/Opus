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
#include <signal.h>

int help()
{
    printf("Usage:\n");
    printf("Create a user and change permissions:\n");
    printf("    secureops -c <username> [file] ...\n");
    printf("Restart apache:\n");
    printf("    secureops -r\n");
    printf("Delete a user from the system:\n");
    printf("    secureops -d <username>\n");
    printf("Creates a new RabbitMQ user/vhost and writes to stdout the password:\n");
    printf("    secureops -e <username>\n");
    printf("Delete a RabbitMQ user and vhost:\n");
    printf("    secureops -b <username>\n");
    printf("Supervisord operations:\n");
    printf("    secureops -s <username> <projectdir> <operation>\n");
    printf(" where <operation> is one of:\n");
    printf("    -S to start supervisord\n");
    printf("    -T to send SIGTERM to supervisord\n");
    printf("    -H to send SIGHUP to supervisord\n");
    return 1;
}


/**
 * Generates a random password and puts it in the given buffer
 */
void getpwd(char *buffer, int length)
{
    FILE *urandom = fopen("/dev/urandom", "r");
    int i = 0;
    while (i < length) {
        int c = fgetc(urandom);
        if (c == EOF) {
            fprintf(stderr, "EOF on read from urandom?\n");
            exit(1);
        }
        char ch = (char)c;
        if ((ch >= '0' && ch <= '9') ||
            (ch >= 'A' && ch <= 'Z') ||
            (ch >= 'a' && ch <= 'z')) {
            buffer[i] = ch;
            i++;
        }
    }
    fclose(urandom);
}

int main(int argc, char **argv)
{
    // Set the real user id. Effective user-id ought to be good enough, but
    // some things check real user id I suppose
    setuid( geteuid() );
    
    /*
     * Restart Apache
     */
    if (argc < 2) {
        printf("Not enough arguments\n");
        return help();
    }
    if (strcmp(argv[1], "-r") == 0) {
        execl("/bin/sh", "/usr/sbin/apachectl", "/usr/sbin/apachectl", "graceful", (char *)NULL);
        return 1;
    }

    /*
     * Delete a user
     */
    if (strcmp(argv[1], "-d") == 0) {
        char *username = argv[2];
        // Check that the user starts with "opus" and is at least 5 characters
        // long
        if (strlen(username) < 5) {
            printf("Bad username");
            return 1;
        }
        if (strncmp(username, "opus", 4) != 0) {
            printf("Won't delete that user");
            return 1;
        }
        execl("/usr/sbin/userdel", "/usr/sbin/userdel",
                username,
                (char *)NULL
             );
        printf("Launching of userdel failed. %d\n", errno);
        return 255;
    }

    /*
     * Create a user + set permissions on files
     */
    if (strcmp(argv[1], "-c") == 0) {
        if (argc < 3) {
            printf("Must specify a username with -c\n");
            return help();
        }
        char *username = argv[2];
        
        // Create username
        if (fork() == 0) {
            execl("/usr/sbin/useradd", "/usr/sbin/useradd",
                "-d", "/nonexistant",
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
                count++;
                printf("Could not stat %s\n", filename);
                continue;
            }
            mode_t mode;
            if (S_ISDIR(fileinfo.st_mode)) {
                mode = 0770;
            } else {
                mode = 0660;
            }
            if (chown(filename, uid, -1) || chmod(filename, mode)) {
                failures++;
                printf("Couldn't chown or chmod %s\n", filename);
            }
            count++;
        }
        if (count == 0 || failures == 0)
            return 0;
        else if (failures == count) {
            printf("Failed to chmod and chown files\n");
            return 1;
        }
        printf("Some files failed to set permissions\n");
        return 2;
    }

    /*
     * Create a rabbitmq vhost and user, and set a random password
     */
    if (strcmp(argv[1], "-e") == 0) {
        if (argc < 3) {
            printf("Must specify a username with -e\n");
            return help();
        }
        char *username = argv[2];

        {
            // Create a vhost
            if (fork() == 0) {
                execl("/usr/sbin/rabbitmqctl", "/usr/sbin/rabbitmqctl",
                        "-q",
                        "add_vhost",
                        username,
                        (char *)NULL);
                printf("rabbitmqctl failed to launch, errno: %d\n", errno);
                _exit(255);
            }
            int ret;
            wait(&ret);
            if (!WIFEXITED(ret) || WEXITSTATUS(ret)) {
                printf("rabbitmqctl add_vhost failed\n");
                printf("Error code: %d\n", WEXITSTATUS(ret));
                return 1;
            }
        }

        // Generate a password
        char password[31];
        getpwd(password, 30);
        password[30] = 0;

        {
            // Create a user
            if (fork() == 0) {
                execl("/usr/sbin/rabbitmqctl", "/usr/sbin/rabbitmqctl",
                        "-q",
                        "add_user",
                        username,
                        password,
                        (char *)NULL);
                printf("rabbitmqctl failed to launch, errno: %d\n", errno);
                _exit(255);
            }
            int ret;
            wait(&ret);
            if (!WIFEXITED(ret) || WEXITSTATUS(ret)) {
                printf("rabbitmqctl add_user failed\n");
                printf("Error code: %d\n", WEXITSTATUS(ret));
                return 1;
            }
        }

        {
            // Set permissions
            if (fork() == 0) {
                execl("/usr/sbin/rabbitmqctl", "/usr/sbin/rabbitmqctl",
                        "-q",
                        "set_permissions",
                        "-p", username,
                        username,
                        "", ".*", ".*",
                        (char *)NULL);
                printf("rabbitmqctl failed to launch, errno: %d\n", errno);
                _exit(255);
            }
            int ret;
            wait(&ret);
            if (!WIFEXITED(ret) || WEXITSTATUS(ret)) {
                printf("rabbitmqctl set_permissions failed\n");
                printf("Error code: %d\n", WEXITSTATUS(ret));
                return 1;
            }
        }

        printf("%s", password);

        return 0;
    }

    /*
     * Deletes a rabbitmq user and vhost
     */
    if (strcmp(argv[1], "-b") == 0) {
        if (argc < 3) {
            printf("Must specify a username with -b\n");
            return help();
        }
        char *username = argv[2];

        if (strlen(username) < 5) {
            printf("Bad username");
            return 1;
        }
        if (strncmp(username, "opus", 4) != 0) {
            printf("Won't delete that user");
            return 1;
        }

        {
            // Delete the vhost
            if (fork() == 0) {
                execl("/usr/sbin/rabbitmqctl", "/usr/sbin/rabbitmqctl",
                        "-q",
                        "delete_vhost",
                        username,
                        (char *)NULL);
                printf("rabbitmqctl failed to launch, errno: %d\n", errno);
                _exit(255);
            }
            int ret;
            wait(&ret);
            if (!WIFEXITED(ret) || WEXITSTATUS(ret)) {
                printf("rabbitmqctl delete_vhost failed\n");
                printf("Error code: %d\n", WEXITSTATUS(ret));
                if (WEXITSTATUS(ret) != 2) {
                    // If returns 2, the vhost didn't exist. We should just
                    // move on to delete the user
                    return WEXITSTATUS(ret);
                }
            }
        }
        {
            // Delete the user
            if (fork() == 0) {
                execl("/usr/sbin/rabbitmqctl", "/usr/sbin/rabbitmqctl",
                        "-q",
                        "delete_user",
                        username,
                        (char *)NULL);
                printf("rabbitmqctl failed to launch, errno: %d\n", errno);
                _exit(255);
            }
            int ret;
            wait(&ret);
            if (!WIFEXITED(ret) || WEXITSTATUS(ret)) {
                printf("rabbitmqctl delete_user failed\n");
                printf("Error code: %d\n", WEXITSTATUS(ret));
                return WEXITSTATUS(ret);
            }
        }

        return 0;

    }

    /*
     * Supervisord operations
     */
    if (strcmp(argv[1], "-s") == 0) {
        if (argc < 5) {
            printf("Not enough arguments\n");
            return help();
        }

        char *username = argv[2];
        if (strlen(username) < 5) {
            printf("Bad username");
            return 1;
        }
        if (strncmp(username, "opus", 4) != 0) {
            printf("Won't change to that user");
            return 1;
        }

        // Drop permissions to that user, to ensure we won't kill anything that
        // we shouldn't be able to.
        int uid;
        {
            struct passwd *passwd = getpwnam(username);
            if (!passwd) {
                printf("Couldn't get uid\n");
                return 1;
            }
            uid = passwd->pw_uid;
        }
        if (setgid(99) == -1) {
            perror("setgid");
            return 1;
        }
        if (setuid(uid) == -1) {
            perror("setuid");
            return 1;
        }

        char *projectdir = argv[3];

        if (strcmp(argv[4], "-S") == 0) {
            // Starts up the supervisord process
            char pathaddition[] = "/supervisord.conf";
            int pathadditionlen = strlen(pathaddition);

            int pdlen = strlen(projectdir);

            char confpath[pdlen + pathadditionlen + 1];
            strncpy(confpath, projectdir, pdlen);
            strncpy(confpath+pdlen, pathaddition, pathadditionlen);
            confpath[pdlen+pathadditionlen] = 0;

            if (fork() == 0) {
                execlp("supervisord", "supervisord",
                        "-c", confpath,
                        (char *)NULL);
                printf("supervisord couldn't launch. %d\n", errno);
                _exit(255);
            }
            int ret;
            wait(&ret);
            if (!WIFEXITED(ret) || WEXITSTATUS(ret)) {
                printf("Failed to launch supervisord\n");
                printf("Error code: %d\n", WEXITSTATUS(ret));
                return 1;
            }
            return 0;
        }

        // Both remaining options have to know the pid. Read it from the pid file
        int pid;
        {
            char pathaddition[] = "/run/supervisord.pid";
            int pathadditionlen = strlen(pathaddition);

            int pdlen = strlen(projectdir);

            char pidpath[pdlen + pathadditionlen + 1];
            strncpy(pidpath, projectdir, pdlen);
            strncpy(pidpath+pdlen, pathaddition, pathadditionlen);
            pidpath[pdlen+pathadditionlen] = 0;

            FILE *pidfile = fopen(pidpath, "r");
            if (!pidfile) {
                printf("Could not open the pid file\n");
                return 1;
            }
            char pidstring[10];
            fread(pidstring, 1, 9, pidfile);
            pidstring[9] = 0;
            errno = 0;
            pid = strtol(pidstring, NULL, 10);
            if (errno != 0) {
                printf("PID file didn't seem to contain a number\n");
                return 1;
            }
        }

        int ret;
        if (strcmp(argv[4], "-T") == 0) {
            // Send a sigterm to the process
            ret = kill(pid, 15);
        }
        else if (strcmp(argv[4], "-H") == 0) {
            // Send a sighup to the process
            ret = kill(pid, 1);
        }
        else {
            printf("Unknown secureops option\n");
            return help();
        }
        if (ret == -1) {
            printf("Sending of signal failed. pid was %d. errno: %d", pid, errno);
            return 1;
        }
        return 0;
    }

    printf("Bad mode\n");
    return help();
}
