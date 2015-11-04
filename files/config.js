exports.config = {
    "mongo": "mongodb://127.0.0.1:27017/ircanywhere",
    /* -- required
     * -- string
     * -- usage: The mongodb database url */

    "oplog": "mongodb://127.0.0.1:27017/local",
    /* -- required
     * -- string
     * -- usage: The mongodb oplog url - Note you may not have this available on shared mongohq and similar hosts */

    "url": "http://{{site_host}}:{{site_port}}/",
    /* -- required
     * -- string 
     * -- usage: The http url of the web server you're running behind */

    "port": {{site_port}},
    /* -- required
     * -- number
     * -- usage: The port to listen on */

    "secure": false,
    /* -- required
     * -- boolean
     * -- usage: Whether to setup the http server with SSL or not. Certificates will be required in
     private/certs/key.pem and private/certs/cert.pem */

    "enableRegistrations": true,
    /* -- required
     * -- boolean 
     * -- usage: Whether to enable registrations or not */

    "forkProcess": true,
    /* -- required
     * -- boolean 
     * -- usage: Whether to fork a seperate process for irc connections, this will allow connections to stay
     online when the main application closes. It'll also probably speed things up. It's recommended 
     to only ever set this to false when developing */

    "retryWait": 10,
    /* -- number
     * -- usage: How many seconds to wait between reconnect attemps, default is 10 */

    "retryCount": 10,
    /* -- number
     * -- usage: How many times to retry connecting if disconnected, default is 10. Set to negative to
     keep retrying and 0 to disable */

    "ircServer": {
	"enable": true,
	/* -- required
	 * -- boolean
	 * -- usage: Whether to enable the IRC server or not. The IRC server allows you to connect from other
	 clients to ircanywhere. */

	"port": 6667
	/* -- number
	 * -- usage: The port to run the IRC server on, 6667 is the default IRC service port. */

	/* TODO: SSL */
    },

    "identd": {
	"enable": true,
	/* -- required
	 * -- boolean 
	 * -- usage: Whether to enable the integrated identd server or not. This is recommended to ensure that
	 server owners can validate your users, and often it increases i:line limits on some networks */

	"port": 113
	/* -- number 
	 * -- usage: The port to run the identd server on, 113 is the ident service port, however you can run it on
	 any port you wish, you would need to forward 113 to this port. If you omit it or leave it as 113 
	 IRCAnywhere will need elevated permissions to bind */
    },

    "email": {
	"siteName": "IRCAnywhere",
	/* -- string 
	 * -- usage: The title to use in validation/forgot password emails
	 defaults to "IRCAnywhere" */

	"from": "IRCAnywhere <no-reply@mysite.com>",
	/* -- required
	 * -- string 
	 * -- usage: The email address to send emails from, can be either email@domain.tld
	 or Name <email@domain.tld> */

	"smtp": "smtps://username:password@smtp.gmail.com"
	/* -- required
	 * -- string 
	 * -- usage: The smtp server to connect to, it's advised you set this up properly, you can run
	 a local server and pass in a local url, or get free accounts from places like Mailgun.
	 Note the prefix smtps:// enables SSL, whereas smtp:// is unsecure. */
    },

    "clientSettings": {
	"activityTimeout": 0,
	/* -- number
	 * -- usage: The amount of hours to timeout irc clients after inactivity, not required
	 and can be set to 0 or below to deactivate timeouts */

	"networkLimit": 10,
	/* -- required
	 * -- number
	 * -- usage: Network limit for users, minimum is 0, maximum is 10, at the moment */

	"networkRestriction": [
	    "*.freenode.net"
	],
	/* -- array
	 * -- usage: Whether to restrict clients to connecting to specific hostmasks, can be
	 disabled by omitting completely, or setting to ["*"] */

	"userNamePrefix": "ia"
	/* -- required
	 * -- string 
	 * -- usage: The username prefix for users, each registered user has it's own ident
	 based on this prefix + a sequential number */
    },

    "defaultNetwork": {
	"server": "{{irc_server}}",
	/* -- required
	 * -- string 
	 * -- usage: Hostname of the default network to connect new users to */

	"port": {{port}},
	/* -- required
	 * -- number
	 * -- usage: Port to connect the default client to, min 1, max 65535 */

	"realname": "{{realname}}",
	/* -- required
	 * -- string 
	 * -- usage: The gecos for default irc clients */

	"secure": false,
	/* -- boolean 
	 * -- usage: Whether to use ssl for the default irc client, can be omitted
	 defaults to false if so */

	"password": "{{server_password}}",
	/* -- string
	 * -- usage: If the server requires a password, enter it here. Set to null to emit it
	 or remove it completely */

	"channels": [
            /**
	       {
	       "channel": "#ircanywhere-test",
	       "password": "channel-password"
	       }
            */
            {
                "channel": "#juju"
            }
	]
	/* -- array > object
	 * -- usage: An array of channels to connect to on startup, the channel must be the
	 same as the above object, password is optional, channel is not. */
    }
};
