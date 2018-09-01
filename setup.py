from setuptools import setup

setup(name='rcssl',
	version='1.2',
	description='Install Let\'s Encrypt SSL on RunCloud servers the easy way.',
	author="Rehmat",
	author_email="contact@rehmat.works",
	url="https://github.com/rehmatworks/runcloud-letsencrypt",
	license="MIT",
	entry_points={
		'console_scripts': [
			'rcssl = rcssl.rcssl:main'
		],
	},
	packages=[
		'rcssl'
	],
	install_requires=[
		'python-nginx'	]
)