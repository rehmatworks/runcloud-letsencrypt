import glob, os
import nginx
import argparse
import re
from .helpers import *

class RcSSL():
	def __init__(self):
		self.ngroot = '/etc/nginx-rc/conf.d'
		self.leroot = '/etc/letsencrypt/live'
		self.acmeroot = '/opt/RunCloud/letsencrypt'
		self.renewcron = '/etc/cron.d/rcsslrenew'
		self.autopilotcron = '/etc/cron.d/rcsslautopilot'
		self.appdictcount = 8

	def app_conf_file(self, appname):
		return '{}/{}.conf'.format(self.ngroot, appname)

	def app_main_conf_file(self, appname):
		return '{}/{}.d/main.conf'.format(self.ngroot, appname)

	def app_exists(self, appname):
		return bool(os.path.exists(self.app_conf_file(appname)))

	def get_app_info(self, appname):
		info = {}
		if self.app_exists(appname):
			# parse main conf to get app info
			main_conf = self.app_main_conf_file(appname)
			with open(main_conf, 'r') as conf:
				conf_data = conf.read()
				domains_str = find_between(conf_data, 'server_name', ';')
				if domains_str:
					domains = domains_str.split()
					valid_domains = []
					invalid_domains = []
					for domain in domains:
						if is_valid_domain(domain):
							valid_domains.append(domain)
						else:
							invalid_domains.append(domain)
					info['name'] = appname
					info['valid_domains'] = valid_domains
					info['invalid_domains'] = invalid_domains	
				info['root'] = '{}/'.format(find_between(conf_data, 'root', ';'))
				info['username'] = find_between(conf_data, '/home/', '/')
				info['vhostdir'] = self.ngroot
				if len(domains) > 0:
					info['cert_path'] = '{}/{}/fullchain.pem'.format(self.leroot, domains[0])
					info['key_path'] = '{}/{}/privkey.pem'.format(self.leroot, domains[0])
		return info

	def get_app_names(self):
		apps = []
		for conf_file in glob.glob(self.ngroot+'/*.conf'):
			if not '-ssl.conf' in conf_file:
				with open(conf_file, 'r') as conf:
					apps.append(find_between(conf.read(), 'conf.d/', '.d'))
		return apps

	def get_le_ssl(self, appinfo):
		domainsstr = ''
		domains = appinfo.get('valid_domains')
		for domain in domains:
			domainsstr += ' -d {}'.format(domain)		
		cmd = "certbot certonly --webroot -w {} --register-unsafely-without-email --agree-tos --force-renewal --fullchain-path={} --key-path={} {}".format(self.acmeroot, appinfo.get('cert_path'), appinfo.get('key_path'), domainsstr)
		try:
			run_cmd(cmd)
		except:
			raise

	def install_ssl(self, app):
		appinfo = self.get_app_info(app)
		if len(appinfo) == self.appdictcount:
			domains = appinfo.get('valid_domains')
			if len(domains) > 0:
				print_message('{} valid domains found. Attempting to obtain SSL certificate from Let\'s Encrypt'.format(len(domains)), 'OK')
				try:
					self.get_le_ssl(appinfo)
					if os.path.exists(appinfo.get('cert_path')) and os.path.exists(appinfo.get('key_path')):
						write_vhost(appinfo)
					else:
						raise Exception('Something went wrong. Cert and key files were not found.')
				except Exception as e:
					raise Exception('SSL certificate cannot be obtained for {}. The most obvious reasons are that any of your domains aren\'t pointed to your server or SSL limit is reached.'.format(app))
			else:
				raise Exception('No valid domains found for the app {}'.format(app))
		else:
			raise Exception('The app {} cannot be processed. Maybe it\'s configuration files have been edited and broken'.format(app))

	def uninstall_ssl(self, app):
		appinfo = self.get_app_info(app)
		if len(appinfo) == self.appdictcount:
			run_cmd('certbot delete --cert-name {}'.format(appinfo.get('valid_domains')[0]))
			os.remove('{}/{}-ssl.conf'.format(appinfo.get('vhostdir'), appinfo.get('name')))
		else:
			raise Exception('Provided app name seems to be invalid.')

	def install_cron(self):
		with open(self.renewcron, 'w') as f:
			f.write('0 0 * * * root {} -r > /dev/null 2>&1\n'.format(get_package_path('rcssl')))

	def install_autopilot_cron(self):
		if not os.path.exists(self.autopilotcron):
			with open(self.autopilotcron, 'w') as f:
				f.write('0 * * * * root {} -i all > /dev/null 2>&1\n'.format(get_package_path('rcssl')))
		else:
			raise Exception('Auto-pilot CRON job is already enabled')

	def uninstall_autopilot_cron(self):
		if os.path.exists(self.autopilotcron):
			os.remove(self.autopilotcron)
		else:
			raise Exception('Auto-pilot CRON job is not enabled.')

	def renew_ssls(self):
		cmd = 'certbot renew --webroot-path {}'.format(self.acmeroot)
		run_cmd(cmd)

	def has_ssl(self, app):
		appinfo = self.get_app_info(app)
		sslvhost = '{}/{}-ssl.conf'.format(appinfo.get('vhostdir'), appinfo.get('name'))
		return bool(len(appinfo) == self.appdictcount and os.path.exists(sslvhost))