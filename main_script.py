from flask import Flask, render_template, request
import subprocess
import os
import socket
from datetime import datetime
import shutil

app = Flask(__name__)

########### TO RUN ##########
#run 'python app.py' in cmd prompt
#Visit http://127.0.0.1:5000/


######################## Misc. #########################################################
# Check if the script is running with admin privileges
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Run the script with admin privileges if necessary
def run_as_admin():
    if not is_admin():
        print("Attempting to restart script with admin privileges...")
        try:
            # Request admin privileges
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
            exit(0)
        except Exception as e:
            print(f"Failed to restart with admin privileges: {e}")
            print("Please close this script and reopen it with admin privileges manually.")

# Function to get the current date in the format MMDDYYYY for backup naming
def get_current_date():
    return datetime.now().strftime("%m%d%Y")

####################### Drive Summary Functions ##########################
# Option 0: Name of the computer
def get_computer_name():
    return socket.gethostname()

# Option 1: Check if Windows is activated
def check_windows_activation():
    try:
        result = subprocess.check_output("slmgr /xpr", shell=True).decode()
        if "The machine is permanently activated" in result:
            return "Windows is activated."
        else:
            return "Windows is NOT activated."
    except:
        return "Couldn't check activation status."

# Option 2: Check if ARS.exe is enabled in Task Scheduler
def check_task_scheduler_status():
    try:
        result = subprocess.check_output("schtasks /query /tn ars.exe", shell=True).decode()
        if "Running" in result:
            return "ARS.exe is enabled in Task Scheduler."
        else:
            return "ARS.exe is NOT enabled in Task Scheduler."
    except:
        return "Couldn't find ARS.exe in Task Scheduler"

# Option 3: Check if DHCP is enabled
def check_dhcp_status():
    try:
        result = subprocess.check_output("netsh interface ip show config", shell=True).decode()
        if "DHCP enabled: Yes" in result:
            return "DHCP is enabled."
        else:
            return "DHCP is NOT enabled."
    except:
        return "Couldn't check DHCP status."

# Option 4: Get the current time zone
def get_time_zone():
    return str(datetime.now().astimezone().tzinfo)

# Option 5: Get display resolution and refresh rate
def get_display_info():
    try:
        resolution_result = subprocess.check_output("wmic path Win32_VideoController get VideoModeDescription", shell=True).decode()
        resolution_lines = resolution_result.strip().split("\n")
        resolution = resolution_lines[1].strip() if len(resolution_lines) > 1 else "Couldn't retrieve resolution."

        refresh_rate_result = subprocess.check_output("wmic path Win32_VideoController get CurrentRefreshRate", shell=True).decode()
        refresh_rate_lines = refresh_rate_result.strip().split("\n")
        refresh_rate = refresh_rate_lines[1].strip() if len(refresh_rate_lines) > 1 else "Couldn't retrieve refresh rate."

        return f"Resolution: {resolution}, Refresh rate: {refresh_rate} Hz"
    except Exception as e:
        return str(e)

# Option 6: Get ars.exe file version
def get_ars_version():
    try:
        ars_path = "D:\\ARS\\bin\\ars.exe"
        result = subprocess.check_output(f'powershell "(Get-Command {ars_path}).FileVersionInfo.ProductVersion"', shell=True).decode()
        return result.strip()
    except:
        return "ARS.exe file not found."

# Option 7: Search for Boot Drive Version file in Documents folders
def find_boot_drive_version_file():
    root_dir = "C:\\Users"
    filename = "Boot Drive Version.txt"

    for user_folder in os.listdir(root_dir):
        user_docs_path = os.path.join(root_dir, user_folder, "Documents")
        if os.path.isdir(user_docs_path):
            for root, dirs, files in os.walk(user_docs_path):
                if filename in files:
                    file_path = os.path.join(root, filename)
                    try:
                        with open(file_path, 'r') as f:
                            version = f.read().strip()
                            return f"The Boot drive version is: {version}"
                    except Exception as e:
                        return f"Error reading file: {str(e)}"
    return "Boot Drive Version file not found."

# Option 8: Check if ars.exe shortcut exists on the desktop
def check_ars_shortcut():
    shortcut_path = "C:\\Users\\Public\\Desktop\\ars.exe.lnk"
    return os.path.exists(shortcut_path)

############################## FLASK ROUTES ###############################
@app.route("/")
def home():
    # This will pass the data to the results.html template
    return render_template("results.html", 
                           computer_name=get_computer_name(), 
                           windows_activation=check_windows_activation(),
                           task_scheduler_status=check_task_scheduler_status(),
                           dhcp_status=check_dhcp_status(),
                           display_resolution=get_display_info())

####################### Change Settings Functions ########################
# Change PC name
def set_pc_name(new_name):
    try:
        subprocess.call(f'wmic computersystem where name="%computername%" call rename name="{new_name}"', shell=True)
        return f"PC name changed to {new_name}. Please restart for changes to take effect."
    except Exception as e:
        return f"Failed to set PC name: {str(e)}"

# Change Time Zone
def change_time_zone(new_time_zone):
    try:
        subprocess.call(f'tzutil /s "{new_time_zone}"', shell=True)
        return f"Time zone changed to {new_time_zone}."
    except Exception as e:
        return f"Failed to change time zone: {str(e)}"

# Change Display Resolution and Refresh Rate
def change_display_resolution(resolution, refresh_rate):
    try:
        subprocess.call(f'displaycpl /s {resolution} /f {refresh_rate}', shell=True)
        return f"Display resolution set to {resolution} and refresh rate set to {refresh_rate}."
    except Exception as e:
        return f"Failed to change display resolution and refresh rate: {str(e)}"

# Add ARS shortcut to Desktop
def add_ars_shortcut():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut_path = os.path.join(desktop_path, "ars.exe.lnk")
    ars_exe_path = "C:\\Program Files\\ARS\\ars.exe"

    if os.path.exists(ars_exe_path):
        try:
            shutil.copy(ars_exe_path, shortcut_path)
            return "ARS shortcut added to desktop."
        except Exception as e:
            return f"Failed to add ARS shortcut: {str(e)}"
    else:
        return "ARS.exe not found. Please ensure it is installed."

# Update ARS boot drive version
def update_ars_boot_drive(drive_letter):
    external_drive_path = drive_letter.strip() + "UpdateARS"
    ars_bin_new = os.path.join(external_drive_path, "bin")
    ars_bin_old = "D:\\ARS\\bin"

    if not os.path.exists(ars_bin_new):
        return f"UpdateARS bin folder not found in {external_drive_path}."

    try:
        backup_bin = f"{ars_bin_old}_backup_{get_current_date()}"
        shutil.copytree(ars_bin_old, backup_bin)

        shutil.copytree(ars_bin_new, ars_bin_old, dirs_exist_ok=True)
        return "ARS boot drive version updated successfully."
    except Exception as e:
        return f"Failed to update ARS boot drive version: {str(e)}"


############################### Flask Routes ###############################
@app.route('/')
def index():
    data = {
        'computer_name': get_computer_name(),
        'windows_activation': check_windows_activation(),
        'task_scheduler_status': check_task_scheduler_status(),
        'dhcp_status': check_dhcp_status(),
        'time_zone': get_time_zone(),
        'display_info': get_display_info(),
        'ars_version': get_ars_version(),
        'boot_drive_version': find_boot_drive_version_file(),
        'ars_shortcut': check_ars_shortcut()
    }
    return render_template('index.html', data=data)

@app.route('/change_setting', methods=['POST'])
def change_setting():
    setting = request.form.get('setting')
    return render_template('change_setting.html', setting=setting)

@app.route('/change/computer_name', methods=['POST'])
def change_computer_name():
    new_name = request.form.get('new_value')
    result = set_pc_name(new_name)
    return render_template('result.html', result=result)

@app.route('/change/time_zone', methods=['POST'])
def change_time_zone_route():
    new_time_zone = request.form.get('new_value')
    result = change_time_zone(new_time_zone)
    return render_template('result.html', result=result)

@app.route('/change/display_info', methods=['POST'])
def change_display_info():
    resolution = request.form.get('resolution')
    refresh_rate = request.form.get('refresh_rate')
    result = change_display_resolution(resolution, refresh_rate)
    return render_template('result.html', result=result)

@app.route('/change/ars_shortcut', methods=['POST'])
def change_ars_shortcut():
    result = add_ars_shortcut()
    return render_template('result.html', result=result)

@app.route('/change/boot_drive_version', methods=['POST'])
def change_boot_drive_version():
    drive_letter = request.form.get('drive_letter')
    result = update_ars_boot_drive(drive_letter)
    return render_template('result.html', result=result)


#################### Run Flask Application ####################
if __name__ == '__main__':
    app.run(debug=True)
