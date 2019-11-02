from fabric.api import env, local, cd, run

env.hosts = ['cloud']


def deploy():
    local('git push')
    with cd('~/educannews'):
        run('git pull')
        run('pipenv install')
