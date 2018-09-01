# RunCloud Let's Encrypt Automation
Install Let's Encrypt SSL on RunCloud.io servers

### Support Me
If you have found my work useful, then consider ordering your next Digital Ocean server using my referral link. Signing up using this link will give you $10 as well as it will earn me $25 credit. I will use the earned credit to deploy servers involved in my open-source projects' testing. 

### Installation
```bash
pip install rcssl
```

### Usage
```bash
usage: PROG [-h] [-i {all}] [-u {all}] [-r] [-a {disable,enable}]

optional arguments:
  -h, --help            show this help message and exit
  -i, --install
                        Install SSL certificate on an app or on all available
                        apps. Provide the target app name or type all to
                        install SSL on all apps.
  -u, --uninstall
                        Uninstall SSL certificate from an app or from all
                        available apps.
  -r, --renew           Renew all installed SSl certificates.
  -a {disable,enable}, --autopilot {disable,enable}
                        Enable or disable auto-pilot mode.
```

### Examples
To install SSL on all available apps:
```bash
rcssl -i all
```
And to install SSL on a specific app:
```bash
rcssl -i appname
```

Autopilot mode automatically retrieves and installs SSL certificates on your new apps without needing you to sign in and run the install command.

To enable autopilot mode:
```bash
rcssl -a enable

```
and to disable autopilot mode
```bash
rcssl -a disable
```
To uninstall SSL certificate from all apps:
```bash
rcssl -u all
```

And to uninstall SSL certificate from a specific app:
```bash
rcssl -u appname
```
