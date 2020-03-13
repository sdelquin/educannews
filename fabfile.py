from fabric.api import env, local, cd, run

env.hosts = ['cloud']


def deploy():
    local('git push')
    with cd('~/code/educannews'):
        run('git pull')
        run('pipenv install')
