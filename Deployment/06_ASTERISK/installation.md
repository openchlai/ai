1. Update the System:
   - Log in to your CentOS 9 server using SSH or open a terminal.
   - Run the following command to update the system packages:

     ```
     sudo yum update -y
     ```

2. Install Dependencies:
   - Install the required dependencies for Asterisk by running the following command:

     ```
     sudo yum install -y epel-release dmidecode gcc-c++ ncurses-devel libxml2-devel make wget openssl-devel newt-devel kernel-devel sqlite-devel libuuid-devel gtk2-devel jansson-devel binutils-devel
     ```

3. Download Asterisk:
   - Change to the `/usr/src` directory:

     ```
     cd /usr/src
     ```

   - Download the latest version of Asterisk (replace `XX` with the appropriate version number):

     ```
     sudo wget http://downloads.asterisk.org/pub/telephony/asterisk/releases/asterisk-XX-current.tar.gz
     ```

   - Extract the downloaded file:

     ```
     sudo tar -zxvf asterisk-XX-current.tar.gz
     ```

4. Compile Asterisk:
   - Change to the extracted Asterisk directory:

     ```
     cd asterisk-XX*/
     ```

   - Run the following commands to configure and compile Asterisk:

     ```
     sudo contrib/scripts/get_mp3_source.sh
     sudo ./configure
     sudo make menuselect
     sudo make
     sudo make install
     ```

5. Install Additional Asterisk Modules:
   - Run the following command to install additional Asterisk modules:

     ```
     sudo make samples
     ```

6. Set Asterisk User and Group Permissions:
   - Run the following command to create the Asterisk user and group:

     ```
     sudo groupadd asterisk
     sudo useradd -r -d /var/lib/asterisk -g asterisk asterisk
     sudo usermod -aG audio,dialout asterisk
     sudo chown -R asterisk.asterisk /var/{lib,log,run,spool}/asterisk /usr/lib/asterisk /etc/asterisk
     sudo chmod -R 750 /var/{lib,log,run,spool}/asterisk /usr/lib/asterisk /etc/asterisk
     ```

7. Start Asterisk:
   - Start the Asterisk service by running the following command:

     ```
     sudo systemctl start asterisk
     ```

8. Enable Asterisk at Startup:
   - Enable the Asterisk service to start automatically on system boot:

     ```
     sudo systemctl enable asterisk
     ```

9. Configure Firewall:
   - If you have a firewall enabled, allow the necessary ports for Asterisk. For example, to allow SIP (port 5060) and IAX (port 4569), run the following commands:

     ```
     sudo firewall-cmd --permanent --add-port=5060/udp
     sudo firewall-cmd --permanent --add-port=4569/udp
     sudo firewall-cmd --reload
     ```

10. Verify Asterisk Installation:
    - Check the status of Asterisk by running the following command:

      ```
      sudo asterisk -rvvv
      ```

    - You should see the Asterisk console. Type `core show version` to confirm the version installed.

11. Now you can install Voice Apps




    ```mkdir -p /var/lib/voiceapps/bin/res```

    ```mkdir -p /var/lib/voiceapps/conf```

    ```useradd -d /var/lib/voiceapps -s /sbin/nologin voiceapps```

    ```cd /usr/src/Sacco_CRM/src/va2/lib```

    ```make```

    ```cd /usr/src/Sacco_CRM/src/va2/src```

    ```make```

    ```sudo cp asterisk.service /etc/systemd/system/.```

      ```sudo chown root:root /etc/systemd/system/asterisk.service```

      ```sudo systemctl enable asterisk```

      ```sudo systemctl start asterisk```

    ```cp /usr/src/Sacco_CRM/src/va2/bin/muu /var/lib/voiceapps/bin/.```

    ```cp /usr/src/Sacco_CRM/src/va2/bin/res/* /var/lib/voiceapps/bin/res/.```

    ```chown -R voiceapps:voiceapps /var/lib/voiceapps```

    ```cp /usr/src/Sacco_CRM/src/va2/conf/voiceapps.service /usr/lib/systemd/system/voiceapps.service```

    ```chown root:root /usr/lib/systemd/system/voiceapps.service```

    ```systemctl enable voiceapps```

    ```systemctl start voiceapps```

13. setup pjsip
    ```diff /usr/src/Sacco_CRM/src/chan_pjsip_ast_20.3.0.c /usr/src/asterisk-20.3.0/channels/chan_pjsip.c```

    ```cp /usr/src/Sacco_CRM/src/chan_pjsip_ast_20.3.0.c /usr/src/asterisk-20.3.0/channels/chan_pjsip.c```

    ```cd /usr/src/asterisk-20.3.0```

    ```make```

    ```make install```

14. download codec Opus
    
    go to root folder 

    [download code opus](<https://downloads.digium.com/pub/telephony/codec_opus/asterisk-20.0/x86-64/codec_opus-20.0_current-x86_64.tar.gz>)

      ```wget https://downloads.digium.com/pub/telephony/codec_opus/asterisk-20.0/x86-64/codec_opus-20.0_current-x86_64.tar.gz```

      [view readme](../06_ASTERISK/README)


      extract the file - tar 

      ls 
      cd codec - press tab 
      
