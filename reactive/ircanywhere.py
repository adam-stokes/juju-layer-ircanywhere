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
from nodejs import node_dist_dir, node_switch

# ./lib/ircanywherelib.py
from ircanywherelib import (git_clone,
                            run_install_script,
                            write_config_js)

config = hookenv.config()


# HOOKS -----------------------------------------------------------------------
@hook('install')
def install():
    """ Install dependencies for application
    """
    # Install our node.js runtime, our app supports version 4.x
    if not is_state('nodejs.installed'):
        node_switch(config['node-version'])

    # Perform our application install
    set_state('ircanywhere.install')


@hook('config-changed')
def config_changed():
    if config.changed('node-version'):
        node_switch(config['node-version'])


# REACTORS --------------------------------------------------------------------
@when('ircanywhere.install')
def app_install():
    """ Performs application installation
    """
    # Clear this so it gets called once install completed
    remove_state('ircanywhere.installed')

    # Update application
    git_clone(config['ircanywhere-url'], config['ircanywhere-release'])

    # Runs the install.sh script provided by upstream
    run_install_script()

    # Write IRCAnywhere configuration file `config.js`
    write_config_js()

    # Install complete, remove install bit
    remove_state('ircanywhere.install')

    # Let everyone know our application is ready
    set_state('ircanywhere.installed')


@when('ircanywhere.installed')
def start():
    hookenv.status_set('maintenance', 'Starting IRCAnywhere application')
    ctx = {
        'irc_server': config['ircanywhere-server'],
        'port': config['ircanywhere-port'],
        'realname': config['ircanywhere-realname'],
        'password': config['ircanywhere-password']
    }
    hookenv.status_set('maintenance',
                       'Rendering IRCAnywhere config: {}'.format(ctx))
    render(source='files/config.js',
           target=path.join(node_dist_dir(), 'config.js'),
           context=ctx)

    # Render upstart job
    ctx = {
        'dist_dir': node_dist_dir()
    }
    render(source='files/ircanywhere-upstart.conf',
           target='/etc/init/ircanywhere.conf',
           context=ctx)

    hookenv.status_set('maintenance',
                       'Opening Port {}'.format(config['ircanywhere-port']))
    hookenv.open_port(config['ircanywhere-port'])
    hookenv.status_set('active', 'ready')


@when_file_changed('/etc/init/ircanywhere.conf')
def restart():
    hookenv.status_set('maintenance', 'Restarting IRCAnywhere service')
    host.service_restart('ircanywhere')


if __name__ == "__main__":
    main()
