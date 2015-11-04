import os
import sys
from shutil import rmtree
from subprocess import check_call, CalledProcessError
from charmhelpers.core import hookenv
from charmhelpers.fetch import apt_install
from charmhelpers.core.templating import render

# node-layer
from nodejs import node_dist_dir


config = hookenv.config()


def git_clone(upstream, release):
    """ Clones a repo and checkout revision
    FIXME: Should go away and maybe put in another runtime layer
    """
    clone_cmd = ['git', 'clone', '-q',
                 upstream, node_dist_dir()]
    checkout_cmd = ['git', 'checkout', release]
    apt_install(['git'])
    if os.path.isdir(node_dist_dir()):
        rmtree(node_dist_dir())
    try:
        hookenv.log("Cloning: {}".format(clone_cmd), 'debug')
        check_call(clone_cmd)
        os.chdir(node_dist_dir())
        hookenv.log("Checking out revision: {}".format(checkout_cmd), 'debug')
        check_call(checkout_cmd)
    except CalledProcessError as e:
        hookenv.status_set('blocked',
                           "Problem with git: {}".format(e))
        sys.exit(1)


def render_config():
    config = hookenv.config()
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
           target=os.path.join(node_dist_dir(), 'config.js'),
           context=ctx)
