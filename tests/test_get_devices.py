import subprocess
import re
import serial.tools.list_ports

x = serial.tools.list_ports.comports()
for port in x:
    print(port.name)
    print(port.hwid)


def get_com_ports_with_devcon():
    # Run devcon to get the list of all COM ports
    devcon_command = ["devcon", "hwids", "COM*"]

    try:
        # Run the devcon command and capture the output
        result = subprocess.run(devcon_command, capture_output=True, text=True, check=True)
        output = result.stdout

        # Print the raw output for debugging
        # print("Raw devcon output:\n")
        # print(output)

        # Dictionary to store port details
        ports = {}

        # Updated regex pattern to match both standard COM ports and virtual ones like com0com
        # This will capture entries like:
        # COM9
        # com0com - serial port emulator CNCA0 (COM9)
        # com0com\port (hardware id)
        port_pattern = re.compile(r"(COM[0-9A-Za-z]+|COM0COM\\PORT\\\S+)\s+Name:\s+(.*?)\s+Hardware IDs:\s+([^\n]+)")

        matches = port_pattern.findall(output)
        for match in matches:
            com_name = match[0]
            description = match[1]
            hwids = match[2].split('\n')

            port_info = {
                "Port Name": com_name,
                "Description": description,
                "Hardware IDs": hwids
            }
            ports[com_name] = port_info

        return ports

    except subprocess.CalledProcessError as e:
        print(f"Error running devcon: {e}")
        return {}


def main():
    # Retrieve and print all COM ports and their details
    com_ports = get_com_ports_with_devcon()
    first_cnc = [port for port in com_ports if "CNCA0" in com_ports[port]["Description"]]
    print(first_cnc)
    print("Detected COM Ports:\n")
    for port, info in com_ports.items():
        # Use re.search instead of re.match
        result = re.search(r'COM\d+', com_ports[port]["Description"])

        # Check if a match is found
        if result:
            print(result.group())  # prints the matched string
        else:
            print("No match found")
        print(f"Port: {port}")
        for key, value in info.items():
            if isinstance(value, list):
                print(f"  {key}:")
                for item in value:
                    print(f"    {item}")
            else:
                print(f"  {key}: {value}")
        print("-" * 30)

if __name__ == "__main__":
    main()