import sys
import json
import heapq
import math  # If you want to use math.inf for infinity


def dijkstras_shortest_path(routers, src_ip, dest_ip):
    """
    This function takes a dictionary representing the network, a source
    IP, and a destination IP, and returns a list with all the routers
    along the shortest path.

    The source and destination IPs are **not** included in this path.

    Note that the source IP and destination IP will probably not be
    routers! They will be on the same subnet as the router. You'll have
    to search the routers to find the one on the same subnet as the
    source IP. Same for the destination IP. [Hint: make use of your
    find_router_for_ip() function from the last project!]

    The dictionary keys are router IPs, and the values are dictionaries
    with a bunch of information, including the routers that are directly
    connected to the key.

    This partial example shows that router `10.31.98.1` is connected to
    three other routers: `10.34.166.1`, `10.34.194.1`, and `10.34.46.1`:

    {
        "10.34.98.1": {
            "connections": {
                "10.34.166.1": {
                    "netmask": "/24",
                    "interface": "en0",
                    "ad": 70
                },
                "10.34.194.1": {
                    "netmask": "/24",
                    "interface": "en1",
                    "ad": 93
                },
                "10.34.46.1": {
                    "netmask": "/24",
                    "interface": "en2",
                    "ad": 64
                }
            },
            "netmask": "/24",
            "if_count": 3,
            "if_prefix": "en"
        },
        ...

    The "ad" (Administrative Distance) field is the edge weight for that
    connection.

    **Strong recommendation**: make functions to do subtasks within this
    function. Having it all built as a single wall of code is a recipe
    for madness.
    """

    def ipv4_to_value(ipv4_addr):
        """
        Convert a dots-and-numbers IP address to a single 32-bit numeric
        value of integer type. Returns an integer type.

        """
        value = 0

        # split the ip into a list of strings
        # left shift each octet by the appropriate number of bits
        # convert the octet to an integer
        # bitwise OR each octet together
        # return the value
        for i in range(4):
            value |= int(ipv4_addr.split('.')[i]) << (8 * (3 - i))

        return value

    def value_to_ipv4(addr):
        """
        Convert a single 32-bit numeric value of integer type to a
        dots-and-numbers IP address. Returns a string type.

        """
        ip_addr = []

        # right shift the address by the appropriate number of bits
        # bitwise AND the address with 0xff to get the BYTE
        # append the byte to the ip_addr list
        # join the ip_addr list with dots
        for i in range(4):
            octet = (addr >> (8 * (3 - i))) & 0xff
            ip_addr.append(str(octet))

        return '.'.join(ip_addr)

    def get_subnet_mask_value(slash):
        """
        Given a subnet mask in slash notation, return the value of the mask
        as a single number of integer type. The input can contain an IP
        address optionally, but that part should be discarded.

        Returns an integer type.

        """
        # split off the value after the slash
        value = int(slash.split('/')[1])

        # create a string of 1's value long and right pad it with 0's to 32 bits
        mask = '1' * value + '0' * (32 - value)

        # convert the string to an integer
        mask = int(mask, 2)

        return mask

    def ips_same_subnet(ip1, ip2, slash):
        """
        Given two dots-and-numbers IP addresses and a subnet mask in slash
        notataion, return true if the two IP addresses are on the same
        subnet.

        Returns a boolean.

        """
        # convert the ips to integers
        ip1 = ipv4_to_value(ip1)
        ip2 = ipv4_to_value(ip2)

        # get the subnet mask value
        mask = get_subnet_mask_value(slash)

        # compare the ips with the mask
        # return true or false based on the comparison
        return (ip1 & mask) == (ip2 & mask)

    def find_router_for_ip(routers, ip):
        """
        Search a dictionary of routers (keyed by router IP) to find which
        router belongs to the same subnet as the given IP.

        Return None if no routers is on the same subnet as the given IP.

        """
        # set the router to none
        router = None

        # loop through the routers
        for r in routers:
            # if the ip is on the same subnet as the router
            if ips_same_subnet(ip, r, routers[r]['netmask']):
                # set the return to the matching router
                router = r
                break

        return router

    def get_shortest_path(routers, src_router, dest_router):
        """
        Given a dictionary of routers, a source router, and a destination
        router, return the shortest path between the two routers.

        Returns a list of routers along the shortest path.

        """
        # Initialize distances
        distances = {router: math.inf for router in routers}
        distances[src_router] = 0

        # Initialize set of unvisited nodes
        unvisited = set(routers.keys())

        # Initialize dictionary of previous nodes
        previous = {router: None for router in routers}

        # Calculate the shortest path
        while unvisited:
            # Find the unvisited node with the smallest distance
            current_router = min(unvisited, key=lambda router: distances[router])

            # Break once we've reached the destination
            if current_router == dest_router:
                break

            # Mark the current node as visited
            unvisited.remove(current_router)

            # Update the distances to the neighbors of the current node
            for neighbor, dst in routers[current_router]['connections'].items():
                if neighbor not in unvisited:
                    continue
                new_distance = distances[current_router] + dst['ad']
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_router

        # Reconstruct the path from the destination to the source
        path = []
        current_router = dest_router
        while current_router is not None:
            if dest_router == src_router:
                break
            path.append(current_router)
            current_router = previous[current_router]
        path.reverse()

        return path

    # Find the routers for the source and destination IPs
    src_router = find_router_for_ip(routers, src_ip)
    dest_router = find_router_for_ip(routers, dest_ip)

    # Find the shortest path between the routers
    path = get_shortest_path(routers, src_router, dest_router)

    return path

#------------------------------
# DO NOT MODIFY BELOW THIS LINE
#------------------------------
def read_routers(file_name):
    with open(file_name) as fp:
        data = fp.read()

    return json.loads(data)

def find_routes(routers, src_dest_pairs):
    for src_ip, dest_ip in src_dest_pairs:
        path = dijkstras_shortest_path(routers, src_ip, dest_ip)
        print(f"{src_ip:>15s} -> {dest_ip:<15s}  {repr(path)}")

def usage():
    print("usage: dijkstra.py infile.json", file=sys.stderr)

def main(argv):
    try:
        router_file_name = argv[1]
    except:
        usage()
        return 1

    json_data = read_routers(router_file_name)

    routers = json_data["routers"]
    routes = json_data["src-dest"]

    find_routes(routers, routes)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
    
