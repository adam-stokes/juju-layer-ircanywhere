from charms.reactive import (
    when,
    set_state,
    remove_state,
    main
)

from os import path
from charms.reactive.decorators import when_file_changed

from charmhelpers.core import hookenv, host
from charmhelpers.fetch import apt_install
from charmhelpers.core.templating import render

# ./lib/nodejs.py
from nodejs import node_dist_dir, node_switch, npm

# ./lib/ircanywherelib.py
from ircanywherelib import git_clone


# REACTORS --------------------------------------------------------------------
@when('nginx.available')
def install_nodejs():
    """ Installs node
    """
    config = hookenv.config()

    hookenv.log('Installing Node.js {} for IRCAnwyere'.format(
        config['node-version']))
    node_switch(config['node-version'])
    set_state('ircanywhere.install')


@when('ircanywhere.install')
def app_install():
    """ Performs application installation
    """
    config = hookenv.config()

    # Add mongo
    apt_install(['mongodb-server'])

    # Update application
    git_clone(config['ircanywhere-url'], config['ircanywhere-release'])
    npm('install')
    npm('run gulp')

    # Writes configuration
    ctx = {
        'irc_server': config['ircanywhere-server'],
        'port': config['ircanywhere-port'],
        'realname': config['ircanywhere-realname'],
        'password': config['ircanywhere-password']
    }
    hookenv.status_set('maintenance',
                       'Rendering IRCAnywhere config: {}'.format(ctx))
    render(source='config.js',
           target=path.join(node_dist_dir(), 'config.js'),
           context=ctx)

    # Install complete, remove install bit
    remove_state('ircanywhere.install')

    # Let everyone know our application is ready
    set_state('ircanywhere.installed')


@when('ircanywhere.installed')
def start_app():
    config = hookenv.config()

    hookenv.status_set('maintenance', 'Starting IRCAnywhere application')

    # Render upstart job
    ctx = {
        'dist_dir': node_dist_dir()
    }
    render(source='ircanywhere-upstart.conf',
           target='/etc/init/ircanywhere.conf',
           context=ctx)

    hookenv.status_set('maintenance',
                       'Opening Port {}'.format(config['ircanywhere-port']))
    hookenv.open_port(config['nginx-port'])
    hookenv.status_set('active', 'ready')
    remove_state('ircanywhere.installed')


@when_file_changed('/etc/init/ircanywhere.conf')
def restart():
    hookenv.status_set('maintenance', 'Restarting IRCAnywhere service')
    host.service_restart('ircanywhere')


if __name__ == "__main__":
    main()
