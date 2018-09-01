#! /usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from .utils import RcSSL
from .helpers import *

rcssl = RcSSL()
choices = rcssl.get_app_names()
choices.append('all')
parser = argparse.ArgumentParser(prog='PROG')
parser.add_argument('-i', '--install', choices=choices, type=str, help='Install SSL certificate on an app or on all available apps. Provide the target app name or type all to install SSL on all apps.')
parser.add_argument('-u', '--uninstall', choices=choices, type=str, help='Uninstall SSL certificate from an app or from all available apps.')
parser.add_argument('-r', '--renew', help='Renew all installed SSl certificates.', action='store_const', const=True, default=False)
parser.add_argument('-a', '--autopilot', choices=['disable', 'enable'], type=str.lower, help='Enable or disable autopilot mode.')
args = parser.parse_args()

def main():
	if not is_installed('certbot'):
		print_message('Certbot is not installed, installing the libraries...', 'WARNING')
		try:
			install_certbot()
			rcssl.install_cron()
			reload_cron()
			pass
		except:
			print_message('Certbot libraries cannot be installed. Aborting!', 'FAIL')
			exit(0)

	proceed = False
	if args.install:
		target = args.install
		if target.lower() == 'all':
			apps = rcssl.get_app_names()
			if len(apps) > 0:
				for app in apps:
					if not rcssl.has_ssl(app):
						print_message('Processing app {}'.format(app), 'INFO')
						try:
							rcssl.install_ssl(app)
							print_message('Reloading nginx server', 'INFO')
							reload_nginx()
							print_message('SSL should have been installed for {}'.format(app), 'OK')
						except Exception as e:
							print_message('Error: {}'.format(str(e)), 'FAIL')
					else:
						print_message('SSL is already installed on {}. Skipping this app...'.format(app), 'WARNING')
			else:
				print_message('No apps found.', 'WARNING')
		else:
			app = rcssl.app_exists(target)
			if app:
				print_message('Attempting to install SSL on {}'.format(target.lower()), 'INFO')
				try:
					rcssl.install_ssl(target)
					print_message('Reloading nginx server', 'INFO')
					reload_nginx()
					print_message('SSL should have been installed for {}'.format(target), 'OK')
				except Exception as e:
					print_message('Error: {}'.format(str(e)), 'FAIL')
			else:
				print_message('The provided app name {} does not exist'.format(target), 'FAIL')
	elif args.uninstall:
		target = args.uninstall
		if target.lower() == 'all':
			apps = rcssl.get_app_names()
			if len(apps) > 0:
				print_message('{} apps found from where SSL will be uninstalled'.format(len(apps)), 'INFO')
				for app in apps:
					print_message('Uninstalling SSL from the app {}'.format(app), 'INFO')
					try:
						rcssl.uninstall_ssl(app)
						print_message('Reloading nginx server', 'INFO')
						reload_nginx()
						print_message('SSL should have been uninstalled from {}'.format(app), 'OK')
					except Exception as e:
						print_message('Error: {}'.format(str(e)), 'FAIL')
		else:
			app = rcssl.app_exists(target)
			if app:
				print_message('Attempting to uninstall SSL from {}'.format(target.lower()), 'INFO')
				try:
					rcssl.uninstall_ssl(target)
					print_message('Reloading nginx server', 'INFO')
					reload_nginx()
					print_message('SSL should have been uninstalled from {}'.format(target), 'OK')
				except Exception as e:
					print_message('Error: {}'.format(str(e)), 'FAIL')
			else:
				print_message('The provided app name {} does not exist'.format(target), 'FAIL')
	elif args.renew:
		try:
			rcssl.renew_ssls()
			reload_nginx()
			print_message('SSL renewals should have been succeeded.', 'OK')
		except Exception as e:
			print_message('No renewals were attempted', 'FAIL')
	elif args.autopilot:
		action  = args.autopilot
		if action == 'enable':
			try:
				rcssl.install_autopilot_cron()
				reload_cron()
				print_message('Auto-pilot CRON job has been successfully enabled.', 'OK')
			except Exception as e:
				print_message(str(e), 'FAIL')
		else:
			try:
				rcssl.uninstall_autopilot_cron()
				reload_cron()
				print_message('Auto-pilot CRON job has been successfully disabled.', 'OK')
			except Exception as e:
				print_message(str(e), 'FAIL')
	else:
		parser.print_help()