import json
import os
import machine
from ota_updater.main.ota_updater import OTAUpdater

#ota_modules = ['ota_updater', 'example_module']  # Add your own application module to this list.
ota_modules = ['esp32_example']  # Add your own application module to this list.

def load_ota_config(module_name):
	"""Load OTA Configuration from JSON file held in config directory. JSON Config file:
	{"gitrepo": 
		{"url" : "https://github.com/bensherlock/micropython-ota-updater-example-module" } 
	}"""
	ota_config = None
	config_filename = 'config/' + module_name + '_gitrepo_cfg.json'
	try:
		with open(config_filename) as json_config_file:
			ota_config = json.load(json_config_file)
	except Exception:
		pass

	return ota_config

def download_and_install_updates_if_available():
	"""Connects to the WiFi and for each module in the list checks for new releases and downloads them all. 
	Restarts the microcontroller when complete."""

	# Open Wifi
	if not OTAUpdater.using_network(ssid, password):
		# Failed to connect
		print("Unable to connect to wifi")
		return False

	# Startup Load Configuration For Each Module and check for updates, download if available, then overwrite main/
	for ota_module in ota_modules:
		print("ota_module=" + ota_module)
		ota_cfg = load_ota_config(ota_module)
		if ota_cfg:
			o = OTAUpdater(ota_cfg['gitrepo']['url'], ota_module, github_pat=pat) # where pat is the github personal access token.
			# download_updates_if_available - Checks version numbers and downloads into next/
			o.download_updates_if_available()
			# apply_pending_updates_if_available - Moves next/ into main/
			o.apply_pending_updates_if_available()            

	# Now need to reboot to make use of the updated modules
	machine.reset()

def boot():
	# Check reason for reset - only update if power on reset
	if machine.reset_cause() == machine.PWRON_RESET:
		download_and_install_updates_if_available()

	# Start the main application
	start()

def start():
	# Run the application.
	# This could be your own application included as part of your own module:
	# yourapp.main()
	try:
		from example_module.main.example_module import ExampleModuleClass
		example = ExampleModuleClass()
		example.do_something()
	except:
		pass


# Run boot()
boot()