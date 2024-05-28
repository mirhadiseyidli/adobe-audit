### To get started first install packages (only missing ones)
```
python3 -m pip install okta
python3 -m pip install aiohttp
python3 -m pip install json
python3 -m pip install asyncio
```

### Go to 1Password and download the JSON file from Adobe Audit API Credentials in IT Vault

Run the command:
```
python3 audit_users_adobe.py
```

### You will see the output on the Terminal also get a CSV file to check if you don't like the terminal