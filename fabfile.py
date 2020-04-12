from fabric.api import env, local, cd, run, prefix

env.hosts = ['cloud']


def deploy():
    local('git push')
    with prefix('source ~/.virtualenvs/educannews/bin/activate'):
        with cd('~/code/educannews'):
            run('git pull')
            run('pip install -r requirements.txt')
