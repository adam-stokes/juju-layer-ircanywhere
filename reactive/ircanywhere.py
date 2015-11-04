from charms.reactive import (
    when,
    set_state,
    remove_state,
    is_state,
    main,
    hook
)

from os import path
from charms.reactive.decorators import when_file_changed

from charmhelpers.core import hookenv, host
from charmhelpers.core.templating import render

# ./lib/nodejs.py
from nodejs import node_dist_dir, node_switch, npm

# ./lib/ircanywherelib.py
from ircanywherelib import (git_clone,
                            run_install_script)


# REACTORS --------------------------------------------------------------------
@when('nginx.available')
def install_vhost():
    config = hookenv.config()
    hookenv.status_set('maintenance',
                       'Loading IRCAnywhere vhost and restarting nginx')

    render(source='vhost.conf',
           target='/etc/nginx/sites-enabled/default',
           context={
               'application_address': hookenv.unit_public_ip(),
               'application_port': config['ircanywhere-web-port'],
               'port': config['nginx-port']
           })
    set_state('nginx.restart')
    set_state('ircanywhere.install.prereqs')


@when('ircanywhere.install.prereqs')
def install_prereqs():
    """ Installs node
    """
    config = hookenv.config()
    node_switch(config['node-version'])
    remove_state('ircanywhere.install.prereqs')
    set_state('ircanywhere.install.app')


@when('ircanywhere.install.app')
def app_install():
    """ Performs application installation
    """
    config = hookenv.config()

    # Clear this so it gets called once install completed
    remove_state('ircanywhere.installed')

    hookenv.status_set('maintenance', 'Installing Node for IRCAnywhere')

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
    remove_state('ircanywhere.install.app')

    # Let everyone know our application is ready
    set_state('ircanywhere.installed')


@when('ircanywhere.installed')
def start():
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
    hookenv.open_port(config['ircanywhere-port'])
    hookenv.status_set('active', 'ready')


@when_file_changed('/etc/init/ircanywhere.conf')
def restart():
    hookenv.status_set('maintenance', 'Restarting IRCAnywhere service')
    set_state('nginx.restart')
    host.service_restart('ircanywhere')


if __name__ == "__main__":
    main()
