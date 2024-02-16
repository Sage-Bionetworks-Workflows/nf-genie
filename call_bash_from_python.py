import os
import subprocess

# Get the directory of the Python script

# Call the Bash script and pass the directory as an argument
bash_script_path = '/home/ec2-user/test_bash/your_script.sh'
subprocess.call([bash_script_path])

