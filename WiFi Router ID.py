import pandas as pd
import requests
import json

# Read the CSV file containing WiFi device information
df = pd.read_csv('wpa2.csv')


def lookup_mac_vendor(mac_address):
    """
    Look up the vendor information for a MAC address using the IEEE OUI database.

    Args:
        mac_address (str): MAC address in any format

    Returns:
        str: Vendor information if found, otherwise error message
    """
    # Format the MAC address to xx:xx:xx format (first 3 bytes)
    mac_parts = mac_address.split(':')
    if len(mac_parts) >= 3:
        oui = f"{mac_parts[0]}:{mac_parts[1]}:{mac_parts[2]}:00:00:00"
    else:
        # Handle case where MAC address might be in a different format
        mac_clean = ''.join(c for c in mac_address if c.isalnum()).upper()
        if len(mac_clean) >= 6:
            oui = f"{mac_clean[0:2]}:{mac_clean[2:4]}:{mac_clean[4:6]}:00:00:00"
        else:
            return "Invalid MAC address format"

    try:
        # Use the maclookup.app API
        api_key = "GET YOUR OWN API KEY FROM BELOW LINK"  # Replace with your actual API key if needed
        url = f"https://api.maclookup.app/v2/macs/{oui}?apiKey={api_key}"

        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            # Parse the JSON response
            data = json.loads(response.text)
            if "company" in data and data["company"]:
                return data["company"]
            elif "blockDetails" in data and data["blockDetails"] and "company" in data["blockDetails"]:
                return data["blockDetails"]["company"]
            else:
                return "Vendor information not available"
        else:
            return f"API request failed: {response.status_code}"
    except Exception as e:
        return f"Error looking up vendor: {str(e)}"


# Process each MAC address in the dataframe
print("Looking up vendor information for MAC addresses...")
vendors = []

for mac in df['BSSID']:
    vendor_info = lookup_mac_vendor(mac)
    vendors.append(vendor_info)
    print(f"MAC: {mac} - Vendor: {vendor_info}")

# Add vendor information to the dataframe
df['Vendor'] = vendors

# Save the updated dataframe to a new CSV file
df.to_csv('device.csv', index=False)
print("\nVendor information saved to 'device_vendors.csv'")
