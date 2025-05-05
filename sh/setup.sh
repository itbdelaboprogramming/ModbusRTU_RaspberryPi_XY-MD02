#!/bin/bash

# Enable VNC
sudo raspi-config nonint do_vnc 0

# Silent system update & upgrade
echo "Updating system (this might take a while)..."
sudo apt-get update -qq > /dev/null
sudo apt-get upgrade -y -qq > /dev/null
echo "System updated."

# Ask for virtual environment name
echo -e "\nEnter virtual environment name:"
read venv_name

# Check if the virtual environment already exists
echo ""
if [ -d "$venv_name" ]; then
    echo "Virtual environment '$venv_name' already exists. Skipping creation."
else
    echo "Creating virtual environment '$venv_name'..."
    python3 -m venv "$venv_name"
fi

# Activate virtual environment
source "$venv_name/bin/activate"

# Setup database
echo -e "\nSetup Database"
# Install MariaDB only if not installed
if ! command -v mariadb >/dev/null; then
    echo "?? Installing MariaDB..."
    sudo apt install mariadb-server -y
    sudo mysql_secure_installation
else
    echo "? MariaDB is already installed."
fi

sudo apt install apache2 php libapache2-mod-php php-mysql -y
sudo apt install phpmyadmin -y

sudo ln -s /etc/phpmyadmin/apache.conf /etc/apache2/conf-available/phpmyadmin.conf
sudo a2enconf phpmyadmin
sudo systemctl reload apache2

# Install python package
echo -e "\nInstall required python package"
pip install pymodbus
pip install minimalmodbus
pip install pyserial
pip install paho-mqtt
pip install mysql-connector-python

# Deactivate virtual environment
deactivate