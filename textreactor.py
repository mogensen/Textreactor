#!/usr/bin/env python
# coding=utf-8

import sys
import os
import optparse
import urllib
import urllib2
import md5


# ================ Option Parser ===============
# Handles options that are required
# ==============================================
strREQUIRED = 'required'

class OptionWithDefault(optparse.Option):
    ATTRS = optparse.Option.ATTRS + [strREQUIRED]
    
    def __init__(self, *opts, **attrs):
        if attrs.get(strREQUIRED, False):
            attrs['help'] = '(Required) ' + attrs.get('help', "")
        optparse.Option.__init__(self, *opts, **attrs)

class OptionParser(optparse.OptionParser):
    def __init__(self, **kwargs):
        kwargs['option_class'] = OptionWithDefault
        optparse.OptionParser.__init__(self, **kwargs)
    
    def check_values(self, values, args):
        for option in self.option_list:
            if hasattr(option, strREQUIRED) and option.required:
                if not getattr(values, option.dest):
                    self.error("option %s is required" % (str(option)))
        return optparse.OptionParser.check_values(self, values, args)             


errorValues = {
	'0.0'   : "Beskeden er afleveret til gatewayen og afventer bekræftigelse af aflevering til telefonen.",
	'0.1'   : "Beskeden er afleveret til gatewayen, men der var ikke forbindelse til leverandøren. Beskeden er lagt i kø og vil blive afsendt, når forbindelsen er genoprettet.",
	'0.2'   : "Beskeden er afleveret til gatewayen, men der var ikke forbindelse til leverandøren. Beskeden er termineret.",
	'0.3'   : "Beskeden blev termineret.",
	'0.4'   : "Beskeden er afleveret til gatewayen og afventer tidsbestemt udsendelse",
	'1.0'   : "'username'-parameteren kan ikke være tom.",
	'1.1'   : "'username'-parameteren er for lang.",
	'1.2'   : "'password'-parameteren kan ikke være tom.",
	'1.3'   : "'password'-parameteren er for lang.",
	'1.4'   : "Kombinationen af brugernavn og password blev ikke genkendt.",
	'1.5'   : "Brugeren er blokeret.",
	'2.0'   : "'dialcode'-parameteren kan ikke være tom.",
	'2.1'   : "'dialcode'-parameteren må kun indeholde heltal.",
	'2.2'   : "'dialcode'-parameteren specificerer en destination, der ikke er understøttet.",
	'2.3'   : "'recipient'-parameteren kan ikke være tom.",
	'2.4'   : "'recipient'-parameteren må kun indeholde heltal.",
	'2.5'   : "'recipient'-parameteren er for lang.",
	'2.6'   : "'text'-parameteren kan ikke være tom.",
	'2.7'   : "'text'-parameteren er for lang.",
	'2.8'   : "'text'-parameteren indeholder ulovlige tegn.",
	'2.9'   : "'from'-parameteren er for lang.",
	'2.10'  : "'from'-parameteren indeholder ulovlige tegn.",
	'2.11'  : "'callback'-parameteren er for lang.",
	'2.12'  : "'retry'-parameteren indeholder ikke en gyldig værdi.",
	'2.13'  : "'timestamp'-parameteren er ugyldig.",
	'3.0'   : "Brugeren har ikke dækning for sms'en",
	'4.0'   : "Siden 'callback'-parameteren specificerede var ikke tilgængelig.",
	'5.0'   : "SMSC-fejl",
	'6.0'   : "Beskedens gyldighedsperiode på 7 døgn udløb.",
	'127.0' : "Beskeden er bekræftet afleveret til telefonen."}


def main(argv):                         

	## Read the options from cmd
	parser = OptionParser()
	parser.add_option("-r", "--receiver", 	type="int", 	dest="rec",		help="sends SMS to REC", required=True)
	parser.add_option("-m", "--message", 	type="string",	dest="msg",		help="SMS content", required=True)
	parser.add_option("-d", "--dialcode", 	type="int",		dest="dialcode",help="the country code for the receiver. See http://www.textreactor.com/documentation.php#appendixdialcodes", default="45")
	parser.add_option("-f", "--from", 		type="string",	dest="sender", 	help="the text set at the receivers phone", default="Frederik")
	parser.add_option("-q", "--quiet", 		 				dest="verbose", help="don't print status messages to stdout", default=True, action="store_false")
	(options, args) = parser.parse_args()

	## Get the password and username from the osx keychain
	username = (os.popen("keychain -u -s textreactor").read())[:-1]
	password = (os.popen("keychain -p -s textreactor").read())[:-1]

	## md5 the password before sending it..
	password = md5.new(password).hexdigest()

	## Encode the url
	params = urllib.urlencode({
		'username'  : username,
		'password'  : password,
		'dialcode'  : options.dialcode,
		'recipient' : options.rec,
		'text'      : options.msg,
		'from'      : options.sender,
		})

	## Do the GET request
	response = urllib2.urlopen("http://api.textreactor.com/legacy/sms.php?" + params)
	html = response.read()

	## Check for errors
	if html[:-1] != "0.0":
		msg = html[:-1] + " - " + errorValues[html[:-1]];
		sys.stderr.write("%s: error: %s\n" % (os.path.basename(sys.argv[0]), msg))
		sys.exit(2)
	else:
		print html[:-1] + " - " + errorValues[html[:-1]]
		sys.exit(0)

if __name__ == "__main__":
	main(sys.argv[1:])
