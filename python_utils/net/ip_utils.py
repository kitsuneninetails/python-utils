def make_gateway_ip(real_ip):
    # Figure out a default gw based on IP, usually
    # (IP & subnet_mask + 1)
    subnet_mask = [255, 255, 255, 255]
    if real_ip.subnet != "":
        smask = int(real_ip.subnet)
        subnet_mask = []

        current_mask = smask
        for i in range(0, 4):
            if current_mask > 8:
                subnet_mask.append(255)
            else:
                lastmask = 0
                for j in range(0, current_mask):
                    lastmask += pow(2, 8 - (j + 1))
                subnet_mask.append(lastmask)
            current_mask -= 8

    split_ip = real_ip.ip.split(".")
    gw_ip_split = []
    for ip_part in split_ip:
        gw_ip_split.append(int(ip_part) &
                           subnet_mask[len(gw_ip_split)])

    gw_ip_split[3] += 1
    gw_ip = '.'.join(map(lambda x: str(x), gw_ip_split))
    return gw_ip.strip()
