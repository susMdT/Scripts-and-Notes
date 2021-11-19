#!/bin/bash

echo -e "\n\nUpdating Apt Packages and upgrading latest patches\n"
sudo apt update -y && sudo apt upgrade -y && sudo apt install curl -y #clear

echo -e "\n\nInstalling Apache2 Web server\n"
sudo apt install apache2 apache2-doc apache2-utils libexpat1 ssl-cert -y #prefork for managing processes/threading apache things

echo -e "\n\nInstalling PHP & Requirements\n"
sudo apt install libapache2-mod-php7.4 php7.4 php7.4-common php7.4-curl php7.4-dev php7.4-gd php7.4-mysql libmcrypt-dev -y #this is missing  mcrypt, find a way to do this

echo -e "\n\nInstalling MySQL\n"
sudo apt install mysql-server mysql-client -y

echo -e "\n\nPermissions for /var/www\n"
sudo chown -R www-data:www-data /var/www
echo -e "\n\n Permissions have been set\n"

echo -e "\n\nEnabling Modules\n"
sudo a2enmod rewrite
sudo yes '' | pecl install mcrypt && echo "extension=mcrypt.so" > /etc/php/7.4/mods-available/mcrypt.ini && phpenmod mcrypt

echo -e "\n\nRestarting Apache\n"
sudo service apache2 restart #or systemctl restart apache2

echo -e "\n\nLAMP Installation Completed"

exit 0
