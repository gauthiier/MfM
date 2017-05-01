import argparse, json, os
from sys import stdin, stdout

def check_config(t):

	file = t + '/config.in'
	if os.path.isfile(file):
		with open(file) as config_file:
			config = json.load(config_file)
		return config
	return None

def query_yes_no(question, default="yes"):

    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

if __name__ == "__main__":

	p = argparse.ArgumentParser()
	p.add_argument('type', nargs=1, choices=['rx', 'tx'])
	args = p.parse_args()

	conf = {}
	conf['type'] = vars(args)['type'][0]

	configure = True

	print ">> mfm configuration program <<"

	existing_config = check_config(conf['type'])
	if existing_config:

		print "current configuration --- " + conf['type'] + ": \n"
		print json.dumps(existing_config, indent=4, sort_keys=False)

		configure = query_yes_no("overwrite current configuration?")
		if not configure:
			conf = existing_config


	if configure:

		# host
		stdout.write("host: ")
		conf['host'] = stdin.readline().rstrip('\n')

		# port
		stdout.write("port: ")
		conf['port'] = stdin.readline().rstrip('\n')

		# mnt
		stdout.write("mount: ")
		conf['mnt'] = stdin.readline().rstrip('\n')
		if conf['mnt'][0] != '/':
			conf['mnt'] = '/' + conf['mnt']

		# server
		stdout.write("server: ")
		conf['server'] = stdin.readline().rstrip('\n')

		# if the program transmits
		if conf['type'] == 'tx':

			# username
			stdout.write("username: ")
			conf['usr'] = stdin.readline().rstrip('\n')

			# password
			stdout.write("password: ")
			conf['pwd'] = stdin.readline().rstrip('\n')

		# name
		conf['name'] = conf['type'] + '-' + conf['mnt'].replace('/', '')

		print "\n>>> configuration"

		conf_str = json.dumps(conf, indent=4, sort_keys=False)
		print conf_str

		if query_yes_no("configure current installation?"):

			with open(conf['type'] + '/config.in', 'w') as config_file:
				config_file.write(conf_str)

	if query_yes_no("configure supervisord (linux)?", default="no"):

		tmp_conf = "." + conf['name'] + '.conf' 
		with open(tmp_conf, 'w') as supervisord_config_file:
			supervisord_config_file.write("[program:" + conf['name'] + "]" + "\n")
			supervisord_config_file.write("directory=" + os.getcwd() + "/" + conf['type'] + "\n")
			supervisord_config_file.write("command=python " + conf['type'] + "monitor.py" + "\n")
			supervisord_config_file.write("autorestart=true" + "\n")
			supervisord_config_file.write("stderr_logfile=/var/log/" + conf['name'] + ".err.log"+ "\n")
			supervisord_config_file.write("stdout_logfile=/var/log/" + conf['name'] + ".out.log"+ "\n")

		os.system('sudo cp ' + tmp_conf + ' /etc/supervisor/conf.d/' + conf['name'] + '.conf')
		os.remove(tmp_conf)

		print "\n* note: please check the config  > supervisorctl reread\n"






