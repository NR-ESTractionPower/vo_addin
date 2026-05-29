# VISION OSLO Extension Tool Entering Script:
import os
import importlib.metadata
import subprocess
import importlib.util
import time
import urllib.request
import urllib.error
import json
import platform
import site
import sys

## VISION OSLO Extension Tool Entering Script:
# V1: Jieming Ye: (2024) Initial version
# V2: Jieming Ye: (2025.06.06) Update to fix the bug of version comparion issue around number larger than 10.
# V3: Jieming Ye: (2025.08.11) Update to fix new machine python not installed with PIP & Certifi in root folder. 
# V4: Jieming Ye: (2025.08.19) Update to fix the issue when connecting to Docking Station with multiple Ethernet IP.
# V5: Jieming Ye: (2025.10.16) Update to ensure V3 updates happens for new machine that start from home network.
# V6: Jieming Ye: (2026.02.23) Update to cover the scenario where importlib user path not in sys.path by default after python version change.

class Colors:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RESET = '\033[0m'

def internet_check():
    '''Check if a handshake with internet can be established or not. To decide if an upgrade is possible or not'''

    # check connected network to see if it is NR network or not
    if check_restricted_network():
        os.system("")
        print(f"{Colors.YELLOW}WARNING:NETWORK RAIL INTERNAL NETWORK DETECTED. ABORT INTERNET CONNECTION ATTEMPT.{Colors.RESET}")
        return False

    try:
        # Send a HEAD request using requests with a timeout of 5 seconds
        response = urllib.request.urlopen("https://pypi.org/", timeout=5)
        print("INTERNET CONNECTION BUILT SUCCESFULLY...")
        return True

    except urllib.error.URLError as e:
        if "CERTIFICATE_VERIFY_FAILED" in str(e):
            try:
                import certifi
                os.environ["SSL_CERT_FILE"] = certifi.where()
                response = urllib.request.urlopen("https://pypi.org/", timeout=5)
                print("INTERNET CONNECTION BUILT SUCCESFULLY...")
                return True
            except ImportError: # certificate not found, which means it not installed (only happen for newly python installation)
                if first_time_setup_try_import_certificate():
                    response = urllib.request.urlopen("https://pypi.org/", timeout=5)
                    print("INTERNET CONNECTION BUILT SUCCESFULLY...")
                    return True
                # reaching here means first time setup failed
                pass
            except Exception as e:
                print(f"{Colors.RED}ERROR:{e}{Colors.RESET}")
                pass
        
        # code reaching here means the attempt to sorting out the issue failed.
        os.system("")
        print(f"{Colors.YELLOW}ERROR:{e}")
        print(f"ERROR:INTERNET CONNECTION POOL. CHECK YOUR INTERNET CONNECTION.{Colors.RESET}")
        return False
    
    except Exception as e:
        os.system("")
        print(f"{Colors.YELLOW}ERROR: UNEXPECTED CONNECTION ERROR: {e}{Colors.RESET}")
        return False

def check_restricted_network():
    '''Return TRUE if connected to the NR Office Environment'''
    # (TODO) JY: NR Network WIFI and Ethernet seems to use the same 10.176 default gateway
    # which means the WIFI and ethernet Checking could be combined.
    # However, there is no solid evidence for that yet.
    system = platform.system()
    try:
        if system == "Windows":
            # WIFI Network Check
            # The reason for this check seperate as most people could use WIFI for NR connection?
            result = subprocess.run(["netsh", "wlan", "show", "interfaces"],
                                    capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines():
                if "SSID" in line and "BSSID" not in line:
                    ssid = line.split(":", 1)[1].strip()
                    if ssid == "14":
                        print("NR CORP WIFI 14 DETECTED.")
                        return True
                    else:
                        break
            # Ehternet Network Check
            block = False
            result = subprocess.run(["ipconfig", "/all"],
                                    capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines():
                if "adapter" in line.lower() and "Ethernet" in line:
                    block = True
                if block:
                    # skip the check if the ethernet cable is not used
                    if "media disconnected" in line.lower():
                        # this means the current ethernet adapter is not used. Could using other adapter
                        block = False # reset the block indicator
                        continue # continue to the next line
                    type = line.split(":", 1)[0].strip().lower()
                    if "default gateway" in type:
                        gatewayip = line.split(":", 1)[1].strip()
                        if gatewayip.startswith("10.176."): # This IP is only used for small private network
                            print("NR CORP ETHERNET CONNECTION DETECTED.")
                            return True
                        else:
                            # this caters the scearnio when default gateway could be empty in some configuration
                            block = False # reset the block indicator
                            continue # continue to the next line
        else: # not ready for other operating system yet
            return False
    except Exception as e:
        print(f"{Colors.RED}ERROR:{e}{Colors.RESET}")
        return False
    # reaching here meaning Not connected to WIFI14 and not connecting to private 10.176 network
    return False

def ensure_pip_installation():
    '''This is to ensure pip is installed before any installation. Only required for new machine'''
    # try to ensure the pip is installed. 
    try:
        subprocess.run(['python', '-m', 'ensurepip'], check=True)
        time.sleep(1)  # Wait for 1 seconds after installation
        return True

    except Exception as e:
        os.system("")
        print(f"{Colors.RED}ERROR:{e}{Colors.RESET}")
        return False

def first_time_setup_try_import_certificate():
    '''This is only be called for the first time after the Python installed and no other packages installed at all.'''
    # ensure pip is installed
    if not ensure_pip_installation():
        return False
    
    # if ensure certifi is installed
    try:
        subprocess.run(['python', '-m', 'pip', 'install', 'certifi'], check=True)
        time.sleep(1)  # Wait for 1 seconds after installation    
    except Exception as e:
        os.system("")
        print(f"{Colors.RED}ERROR:{e}{Colors.RESET}")
        return False
    
    # retry importing certif after certifi get installed
    try:
        import certifi
        os.environ["SSL_CERT_FILE"] = certifi.where()
        return True
        
    except Exception as e:
        os.system("")
        print(f"{Colors.RED}ERROR:{e}{Colors.RESET}")
        return False
    
def get_latest_version(package_name):
    '''Get the lastest python package number from PYPI org'''
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = urllib.request.urlopen(url)
        if response.getcode() == 200:
            data = json.load(response)
            latest_version = data["info"]["version"]
            return latest_version
        else:
            return False
    
    except urllib.error.URLError as e:
        os.system("")
        print(f"{Colors.YELLOW}ERROR:{e}")
        print(f"ERROR:INTERNET CONNECTION POOL. CHECK YOUR INTERNET CONNECTION.{Colors.RESET}")
        return False
    
    except Exception as e:
        os.system("")
        print(f"{Colors.YELLOW}ERROR: UNEXPECTED CONNECTION ERROR: {e}{Colors.RESET}")
        return False

def install_package(package_name):
    try:
        subprocess.run(['python', '-m', 'pip', 'install','--upgrade', package_name], check=True)     
    except Exception as e:
        os.system("")
        print(f"{Colors.RED}ERROR: Error occurred while installing {package_name}: {e}{Colors.RESET}")

def version_tuple(version_string):
    return tuple(map(int,version_string.split(".")))

def check_and_import_package(package_name):

    connection = internet_check()

    if connection == False:
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            os.system("")
            print(f"{Colors.RED}ERROR: {package_name} IS NOT INSTALLED.")
            print(f"ERROR: CHECK CONNECTION AND REQUIRE RESTART THE PROCESS...{Colors.RESET}")
            return False
        else:
            # reaching here means the connection is not established but a package has already been installed previously
            installed_version = importlib.metadata.version(package_name)
            print(f"INSTALLED VERSION OF {package_name}: {installed_version}")
            return True
    
    else:
        try:
            # Check if the package is installed
            spec = importlib.util.find_spec(package_name)
            if spec is None:
                print(f"{package_name} IS NOT INSTALLED. INSTALLING BEGIN...")
                # ensure pip is installed
                if not ensure_pip_installation():
                    return False
                install_package(package_name)
                if site.ENABLE_USER_SITE: # if user site is allowed in python (has to be allowed under NR)
                    user_site = site.getusersitepackages()
                    if user_site not in sys.path:
                        print(f"NEW PYTHON VERSION. USER PATH ADDED TO THE PYTHON PATH...")
                        sys.path.insert(0, user_site)
                        importlib.invalidate_caches()
            
            # Check if the package is installed
            installed_version = importlib.metadata.version(package_name)
            print(f"INSTALLED VERSION OF {package_name}: {installed_version}")

            # Check the latest version available
            latest_version = get_latest_version(package_name)
            if latest_version == False:
                return True
            else:
                print(f"LATEST VERSION OF {package_name}: {latest_version}")

            if version_tuple(latest_version) > version_tuple(installed_version):
                print(f"UPDATING {package_name} TO THE LATEST VERSION. UPGRADING BEGIN...")
                install_package(package_name)
                print(f"{package_name} INSTALLATION COMPLETED. PROCESSING...")
                time.sleep(1)  # Wait for 1 seconds after installation

                importlib.invalidate_caches() # clean the caches before the next time searching
                installed_version = importlib.metadata.version(package_name)
                if latest_version > installed_version:
                    os.system("")
                    print(f"{Colors.RED}ERROR IN INSTALLATION: SOURCE CODE MANAGEMENT ISSUE.")
                    print(f"PLEASE REQUIRE RESTART THE PROCESS...{Colors.RESET}")
                    return False
                else:
                    return True
            else:
                os.system("")
                print(f"{Colors.GREEN}{package_name} IS UP-TO-DATE.{Colors.RESET}")
                return True
            
        except Exception as e:
            os.system("")
            print(f"{Colors.RED}ERROR: Error occurred while importing {package_name}: {e}{Colors.RESET}")
            return False


# Example usage
if __name__ == "__main__":
    print(f"{Colors.GREEN}VISION OSLO EXTENSION TOOL LOADING PROGRAM (V6:2026.02.23){Colors.RESET}")
    if check_and_import_package("vision_oslo_extension"):
        print("\nPACKAGE CHECKING COMPLETED. ENTERING APPLICATION...\n")
        from vision_oslo_extension import master
        master.main()
    else:
        os.system("")
        input(f"{Colors.RED}ERROR: CHECK ERROR INFORMATION ABOVE.{Colors.RESET}")

    
