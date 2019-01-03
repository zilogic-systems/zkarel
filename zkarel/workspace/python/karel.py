import socket

HOST = "localhost"
PORT = 9999

class Error(Exception):
    pass

def send_command(cmd):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(cmd.encode("utf-8"), (HOST, PORT))
        s.settimeout(1)
        resp, address = s.recvfrom(4096)
        resp = resp.decode("utf-8")
        s.close()
    except socket.timeout:
        raise Error("communication failed")

    if resp[:2] == "ER":
        raise Error(resp[3:])

    elif resp[:2] == "OK":
        if len(resp[3:].strip()) != 0:
            return int(resp[3:])
        else:
            return None

    else:
        raise Error("incorrect response received")

move = lambda: send_command("move")
turn_left = lambda: send_command("turn_left")
pick_beeper = lambda: send_command("pick_beeper")
put_beeper = lambda: send_command("put_beeper")
front_is_clear = lambda: send_command("front_is_clear")
left_is_clear = lambda: send_command("left_is_clear")
right_is_clear = lambda: send_command("right_is_clear")
beeper = next_to_a_beeper = lambda: send_command("next_to_a_beeper")
facing_north = lambda: send_command("facing_north")
facing_south = lambda: send_command("facing_south")
facing_east = lambda: send_command("facing_east")
facing_west = lambda: send_command("facing_west")
any_beepers_in_beeper_bag = lambda: send_command("any_beepers_in_beeper_bag")
avenue = gpsx = lambda: send_command("avenue")
street = gpsy = lambda: send_command("street")
start = lambda: send_command("start")
stop = lambda: send_command("stop")
