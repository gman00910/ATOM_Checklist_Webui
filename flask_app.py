from flask import Flask, render_template, request, redirect, url_for
import main_script  # Import your existing script

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("results.html")  # This must match the HTML file name exactly.


# Home page that shows summary statistics and allows users to modify settings
@app.route('/')
def index():
    # Generate summary stats using the functions in the main script
    summary_stats = {
        "Computer Name": main_script.get_computer_name(),
        "Windows Activation Status": main_script.check_windows_activation(),
        "Task Scheduler Status": main_script.check_task_scheduler_status(),
        "DHCP Status": main_script.check_dhcp_status(),
        "Time Zone": main_script.get_time_zone(),
        "Display Info": main_script.get_display_info(),
        "ARS Version": main_script.get_ars_version(),
        "Boot Drive Version": main_script.find_boot_drive_version_file(),
        "ARS Shortcut": main_script.check_ars_shortcut()
    }

    return render_template('index.html', summary_stats=summary_stats)

# Route to handle settings changefrom flask import Flask, render_template, request
import subprocess
import os
import socket
from datetime import datetime
import shutil

app = Flask(__name__)

# Same helper functions as described earlier...
# Drive summary and change functions (these remain the same as before)

# Routes for Flask
@app.route('/')
def index():
    # Gather all the system info for display
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
    # Receive which setting the user wants to change and display the relevant input form
    setting = request.form.get('setting')
    return render_template('change_setting.html', setting=setting)

# Each route handles the changes for respective settings
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


if __name__ == '__main__':
    app.run(debug=True)

@app.route('/change/<option>', methods=['GET', 'POST'])
def change_setting(option):
    if request.method == 'POST':
        if option == "Computer Name":
            new_name = request.form['new_value']
            result = main_script.set_pc_name(new_name)
        elif option == "Time Zone":
            new_time_zone = request.form['new_value']
            result = main_script.change_time_zone(new_time_zone)
        elif option == "Display Info":
            resolution = request.form['resolution']
            refresh_rate = request.form['refresh_rate']
            result = main_script.change_display_resolution(resolution, refresh_rate)
        # Add more conditions as needed
        else:
            result = "Option not found."
        
        return redirect(url_for('index'))
    
    return render_template('change_setting.html', option=option)

if __name__ == '__main__':
    app.run(debug=True)
