from scapy.all import ARP, Ether, srp
import csv

def get_network_ips(ip_range):
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    # Create an Ethernet broadcast packet
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    # Stack the packets to send the ARP request in a broadcast Ethernet frame
    packet = ether/arp

    # Send the packet and capture the responses
    result = srp(packet, timeout=3, verbose=0)[0]

    # Create a list to store discovered IPs
    ip_list = []
    for sent, received in result:
        ip_list.append(received.psrc)  # Append only the IP addresses

    return ip_list

# Specify the IP range (for example, "192.168.1.1/24")
ip_range = "192.168.1.1/24"
ips = get_network_ips(ip_range)

# Print the IPs to a CSV file named "network_ips.csv"
with open("C:/Users/Mostafa/my shit/ROBEN/codes/pymavlink/UAV/files/network_ips.csv", mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["IP Address"])  # Write the header
    for ip in ips:
        writer.writerow([ip])

print(f"{len(ips)} IPs saved to 'network_ips.csv'")
