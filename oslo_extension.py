import os
import importlib.metadata
import subprocess
import importlib.util
import time
import urllib.request
import urllib.error
import json

class Colors:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RESET = '\033[0m'

def internet_check():
    try:
        # Send a HEAD request using requests with a timeout of 5 seconds
        response = urllib.request.urlopen("https://pypi.org/", timeout=5)
        print("INTERNET CONNECTION BUILT SUCCESFULLY...")
        return True

    except urllib.error.URLError as e:
        os.system("")
        print(f"{Colors.YELLOW}ERROR:{e}")
        print(f"ERROR:INTERNET CONNECTION POOL. CHECK YOUR INTERNET CONNECTION.{Colors.RESET}")
        return False
    
    except Exception as e:
        os.system("")
        print(f"{Colors.YELLOW}ERROR: UNEXPECTED CONNECTION ERROR: {e}{Colors.RESET}")
        return False

def get_latest_version(package_name):
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
            installed_version = importlib.metadata.version(package_name)
            print(f"INSTALLED VERSION OF {package_name}: {installed_version}")
            return True
    
    else:
        try:
            # Check if the package is installed
            spec = importlib.util.find_spec(package_name)
            if spec is None:
                print(f"{package_name} IS NOT INSTALLED. INSTALLING BEGIN...")
                install_package(package_name)
            
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

                time.sleep(10)  # Wait for 10 seconds after installation

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
            return True


# Example usage
if __name__ == "__main__":
    if check_and_import_package("vision_oslo_extension"):
        print("\nPACKAGE CHECKING COMPLETED. ENTERING APPLICATION...\n")
        from vision_oslo_extension import master
        master.main()
    else:
        os.system("")
        input(f"{Colors.RED}ERROR: CHECK ERROR INFORMATION ABOVE.{Colors.RESET}")

    
