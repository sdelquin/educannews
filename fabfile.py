from fabric.api import env, local, cd, run

env.hosts = ['production']


def deploy():
    local('git push')
    with cd('~/educannews'):
        run('git pull')
        run('pipenv install')
        # supctl is just an alias (with settings) to supervisorctl
        run('supctl restart educannews')
