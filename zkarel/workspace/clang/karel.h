#ifndef KAREL_H
#define KAREL_H

#include <sys/socket.h>
#include <sys/select.h>
#include <netinet/in.h>
#include <netinet/ip.h> /* superset of previous */
#include <arpa/inet.h>
#include <unistd.h>

#include <stdio.h>
#include <errno.h>
#include <error.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>

#define KAREL_PORT 9999

static inline int karel_send_command(const char *cmd)
{
	int fd;
	int ret;
	char resp[1024];
	fd_set readfds;
	struct timeval timeout;
	struct sockaddr_in dest_addr = { AF_INET, htons(KAREL_PORT), inet_addr("127.0.0.1") };

	fd = socket(PF_INET, SOCK_DGRAM, 0);
	if (fd == -1)
		error(1, errno, "error creating UDP socket");

	ret = sendto(fd, cmd, strlen(cmd), 0, (struct sockaddr *) &dest_addr, sizeof(dest_addr));
	if (ret == -1)
		error(1, errno, "error sending command");

	FD_ZERO(&readfds);
	FD_SET(fd, &readfds);

	timeout.tv_sec = 5;
	timeout.tv_usec = 0;

	ret = select(fd + 1, &readfds, NULL, NULL, &timeout);
	if (ret == -1 && errno != EAGAIN)
		error(1, errno, "error waiting for response");

	if (!FD_ISSET(fd, &readfds))
		error(1, errno, "timeout waiting for response");

	ret = recv(fd, resp, sizeof(resp), 0);
	if (ret == -1)
		error(1, errno, "error receiving response");

	if (ret == 1024)
		error(1, errno, "response too large");
	
	close(fd);

	if (resp[0] == 'E' & resp[1] == 'R') {
		error(1, errno, "error executing command: %s", cmd);

	} else if (resp[0] == 'O' & resp[1] == 'K') {
		resp[ret] = '\0';
		
		if (strlen(&resp[3]) != 0)
			return atoi(&resp[3]);
		else
			return 0;

	} else {
		error(1, errno, "invalid response received");
	}
}

static inline void move()
{
	karel_send_command("move");
}

static inline void turn_left()
{
	karel_send_command("turn_left");
}

static inline void pick_beeper()
{
	karel_send_command("pick_beeper");
}

static inline void put_beeper()
{
	karel_send_command("put_beeper");
}

static inline bool front_is_clear()
{
	return karel_send_command("front_is_clear");
}

static inline bool left_is_clear()
{
	return karel_send_command("left_is_clear");
}

static inline bool right_is_clear()
{
	return karel_send_command("right_is_clear");
}

static inline bool next_to_a_beeper()
{
	return karel_send_command("next_to_a_beeper");
}

static inline bool beeper() { return next_to_a_beeper(); }

static inline bool facing_north()
{
	return karel_send_command("facing_north");
}

static inline bool facing_south()
{
	return karel_send_command("facing_south");
}

static inline bool facing_east()
{
	return karel_send_command("facing_east");
}

static inline bool facing_west()
{
	return karel_send_command("facing_west");
}

static inline bool any_beepers_in_beeper_bag()
{
	return karel_send_command("any_beepers_in_beeper_bag");
}

static inline int avenue()
{
	return karel_send_command("avenue");
}

static inline int gpsx() { return avenue(); }

static inline int street()
{
	return karel_send_command("street");
}

static inline int gpsy() { return street(); }

static inline void start()
{
	karel_send_command("start");
}

static inline void stop()
{
	karel_send_command("stop");
}

#define repeat(n)  int i ## __LINE__ = n; while ((i ## __LINE__)--)


#endif /* KAREL_H */
