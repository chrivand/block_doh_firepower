# Block known DNS over HTTPS servers with Cisco Firepower Threat Defense

**THIS IS A SAMPLE PROOF OF CONCEPT SCRIPT**

Pulls DoH domains and resolves them to IP addresses. Then it creates a Network Group Object in Firepower to be blocked (or something else).

Please contact me, Christopher Van Der Made <chrivand@cisco.com>, if you have any questions or remarks. If you find any bugs, please report them to me, and I will correct them (or do a pull request).

## Installation

These instructions will enable you to download the script and run it, so that the output can be used in Firepower as Group Objects. What do you need to get started? Please find a list of tasks below:

1. You need the IP address (or domain name) of the FMC, the username and password. These will be requested by the script the first time it is run. It is recommended to create a separate FMC login account for API usage, otherwise the admin will be logged out during every API calls. Add the IP/Domain of FMC, the username and password to the config.json file. If you do not add anything, you will be promted to fill this in when executing the script. 

2. In the FMC, go to System > Configuration > REST API Preferences to make sure that the REST API is enabled on the FMC.

3. A Network Group object will be created automatically during the first run of the script.

4. It is also recommended to download an SSL certificate from FMC and put it in the same folder as the scripts. This will be used to securely connect to FMC. In the **config_file.json file**, set the *"SSL_VERIFY"* parameter to *true*, and then set *"SSL_CERT"* to be the path to the FMC's certificate.

5. If you do not have the needed Python libraries set up, you will get an error when executing the script. You will need to install the *"requirements.txt"* file like this (make sure you are in the same directory as the cloned files live):

```
pip install -r requirements.txt
```

6. After this is complete you need to execute the script (make sure you are in the same directory as the cloned files live):

```
python3.6 doh_ip_resolving.py
```

7. Optionally you can let this script run periodically, by setting *"SERVICE"* to *true* in the **config.json** file. In line 244 of the **doh_ip_resolving.py** the time-period is set, per default it is set to an hour (Microsoft recommends you check the version daily, or at the most, hourly):

```
intervalScheduler(WebServiceParser, 3600) #set to 1 hour
```

8. Finally, if you want to automatically deploy the policies, you can set *"AUTO_DEPLOY"* to *true* in the **config_file.json** file. **Be very careful with this, as unfinished policies might be deployed by doing so.**

More detailed instructions will follow.
