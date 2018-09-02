try:
	from shutil import which
except:
	def which(pgm):
		import os
		path = os.getenv('PATH')
		for p in path.split(os.path.pathsep):
			p = os.path.join(p,pgm)
			if os.path.exists(p) and os.access(p,os.X_OK):
				return p

class bcolors:
	HEADER = '\033[95m'
	INFO = '\033[94m'
	OK = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

def find_between(s, first, last):
	try:
		start = s.index( first ) + len( first )
		end = s.index( last, start )
		return s[start:end]
	except ValueError:
		return None

def search(value, data):
	for conf in data:
		blocks = conf.get('server')
		for block in blocks:
			found = block.get(value)
			if found:
				return found
	return None

def is_valid_domain(domain):
	import socket
	try:
		socket.gethostbyname(domain)
		return True
	except:
		return False

def ssl_installed(domain):
	import os
	if domain.startswith('www.'):
		domain = domain.replace('www.', '')
	leroot = '/etc/letsencrypt/live/'
	return bool(os.path.isdir('{}/{}'.format(leroot, domain)))

def run_cmd(cmd):
	import subprocess
	try:
		subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
		return True
	except subprocess.CalledProcessError as e:
		raise Exception(str(e))

def install_certbot():
	cmd = 'sudo apt-get update && yes | sudo apt-get install software-properties-common && yes | sudo add-apt-repository ppa:certbot/certbot && yes | sudo apt-get update && yes | sudo apt-get install certbot'
	return run_cmd(cmd)

def get_package_path(package):
	return which(package)

def is_installed(package):
	return bool(which(package) is not None)

def print_message(msg, color):
	print('{}{}{}'.format(getattr(bcolors, color), msg, bcolors.ENDC))

def write_vhost(appinfo):
	import nginx
	c = nginx.Conf()
	s = nginx.Server()
	s.add(
		nginx.Comment('SSL conf added by rcssl (https://github.com/rehmatworks/runcloud-letsencrypt)'),
		nginx.Key('listen', '443 ssl http2'),
		nginx.Key('listen', '[::]:443 ssl http2'),
		nginx.Key('server_name', ' '.join(appinfo.get('valid_domains'))),
		nginx.Key('brotli', 'on'),
		nginx.Key('brotli_static', 'off'),
		nginx.Key('brotli_min_length', '100'),
		nginx.Key('brotli_buffers', '16 8k'),
		nginx.Key('brotli_comp_level', '5'),
		nginx.Key('brotli_types', '*'),
		nginx.Key('ssl', 'on'),
		nginx.Key('ssl_certificate', appinfo.get('cert_path')),
		nginx.Key('ssl_certificate_key', appinfo.get('key_path')),
		nginx.Key('ssl_prefer_server_ciphers', 'on'),
		nginx.Key('ssl_session_timeout', '5m'),
		nginx.Key('ssl_protocols', 'TLSv1.1 TLSv1.2'),
		nginx.Key('ssl_stapling', 'on'),
		nginx.Key('ssl_stapling_verify', 'on'),
		nginx.Key('resolver', '8.8.8.8 8.8.4.4 valid=86400s'),
		nginx.Key('resolver_timeout', '5s'),
		nginx.Key('ssl_ciphers', '"ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA:ECDHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA256:DHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:!DSS"'),
		nginx.Key('ssl_ecdh_curve', 'secp384r1'),
		nginx.Key('ssl_session_cache', 'shared:SSL:10m'),
		nginx.Key('ssl_session_tickets', 'off'),
		nginx.Key('ssl_dhparam', '/etc/nginx-rc/dhparam.pem'),
		nginx.Key('include', '/etc/nginx-rc/conf.d/{}.d/main.conf'.format(appinfo.get('name')))
	)
	c.add(s)
	nginx.dumpf(c, '{}/{}-ssl.conf'.format(appinfo.get('vhostdir'), appinfo.get('name')))

def reload_nginx():
	run_cmd('sudo service nginx-rc reload')

def reload_cron():
	run_cmd('sudo service cron reload')

def is_root():
	import os
	return bool(os.geteuid() == 0)