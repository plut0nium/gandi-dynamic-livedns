# gandilf.py - Gandi LiveDNS Updater :snake:

This python script allows the user to dynamically update a list of DNS records hosted by http://www.gandi.net.

The objective is to reproduce a dynamic DNS functionality, using Gandi’s newest [LiveDNS](http://doc.livedns.gandi.net/) RESTful API .

## Installation and usage

Just clone the repository (or copy the script) and edit the config file.

Then run `gandilf.py –c your_config.cfg`

The script can be run at regular interval by adding it to your crontab:
```
*/15 * * * * python /path/to/gandilf.py -c your_config.cfg
```

## Configuration

The configuration is made in an ini-like file:
```
[general]
api = https://dns.beta.gandi.net/api/v5/
api_key = YOUR_API_KEY

[example_test]
domain = example.com
name = test
type = A
ttl = 10800
value = EXTERNAL_IP

...
```

The `[general]` section contains settings that are common to all records:
* `api` the LiveDNS API endpoint URL
* `api_key` your personal API key, generated in your account page
 
Each subsequent section refers to a DNS record to be updated.
The section title (in square brackets) is for your own information only, and is not used by the script. Name it however you want.
It must contain the following keys:
* `domain` the domain name
* `name` the name of the record
* `type` the type of record
* `ttl` the TTL associated with that record (in seconds)

:information_source: Please note that the example file also contains a `value` line, but it is not used currently, all records are updated with the external IP address.

If a record requires a specific API key, it can be set by adding an `api_key` in the record section. 

## Motivation

This project was started as a hobby project, adapting existing scripts to my needs and coding habits.
I wanted to rely only on the python standard library, hence the use of `urllib` instead of `python-requests`.

## Credits

This project was inspired by similar projects, mostly:
* [Chralu/gandyn]( https://github.com/Chralu/gandyn)
* [rmarchant/gandi-ddns]( https://github.com/rmarchant/gandi-ddns)

## License

This project is licensed under the terms of the MIT license.
