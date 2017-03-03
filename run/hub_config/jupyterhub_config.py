import os

c = get_config()

c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'

c.DockerSpawner.container_image = os.environ['NOTEBOOK_DOCKER_IMAGE']
spawn_cmd = os.environ.get('NOTEBOOK_SPAWN_CMD', "")
c.DockerSpawner.extra_create_kwargs.update({ 'command': spawn_cmd })

network_name = os.environ['HUB_NETWORK_NAME']
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = network_name
c.DockerSpawner.extra_host_config.update({ 'network_mode': network_name })

host_notebook_dir = os.environ.get('HOST_NOTEBOOK_DIR')
notebook_dir = os.environ.get('NOTEBOOK_DIR', '/notebooks')
c.DockerSpawner.notebook_dir = notebook_dir
c.DockerSpawner.volumes.update({ host_notebook_dir : notebook_dir })
host_notebook_config = os.environ.get('HOST_NOTEBOOK_CONFIG')
host_notebook_secret = os.environ.get('HOST_NOTEBOOK_SECRET')
c.DockerSpawner.volumes.update({ host_notebook_config  : '/jupyter/config' })
c.DockerSpawner.volumes.update({ host_notebooks_secret : '/jupyter/secret' })
c.DockerSpawner.volumes.update({ '/var/run/docker.sock': '/var/run/docker.sock' })
c.DockerSpawner.extra_create_kwargs.update({ 'volume_driver': 'local' })

c.DockerSpawner.remove_containers = True
c.DockerSpawner.debug = True

driver_name = os.environ["NVIDIA_DRIVER_NAME"]
c.DockerSpawner.read_only_volumes.update({driver_name: "/usr/local/nvidia"})
c.DockerSpawner.extra_create_kwargs.update({"volume_driver": "nvidia-docker"})
c.DockerSpawner.extra_host_config.update({ "devices":["/dev/nvidiactl","/dev/nvidia-uvm","/dev/nvidia-uvm-tools","/dev/nvidia0","/dev/nvidia1"]})

c.JupyterHub.hub_ip = 'jupyterhub'
c.JupyterHub.hub_port = 8080

# TLS config
c.JupyterHub.port = 80
c.JupyterHub.ssl_key = os.environ['JUPYTERHUB_SSL_KEY']
c.JupyterHub.ssl_cert = os.environ['JUPYTERHUB_SSL_CERT']

# Authenticate using Google OAuth 2.0
c.JupyterHub.authenticator_class = 'oauthenticator.GoogleOAuthenticator'
c.GoogleOAuthenticator.client_id = os.environ['GOOGLE_CLIENT_ID']
c.GoogleOAuthenticator.client_secret = os.environ['GOOGLE_CLIENT_SECRET']
c.GoogleOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']


# Persist hub data on volume mounted inside container
data_dir = os.environ.get('JUPYTERHUB_DATA_DIR', '/jupyterhub/data')
c.JupyterHub.db_url = os.path.join('sqlite:///', data_dir, 'jupyterhub.sqlite')
c.JupyterHub.cookie_secret_file = os.path.join(data_dir, 'jupyterhub_cookie_secret')


# Whitlelist users and admins
c.Authenticator.whitelist = whitelist = set()
c.Authenticator.admin_users = admin = set()
c.JupyterHub.admin_access = True
pwd = os.path.dirname(__file__)
with open(os.path.join(pwd, 'userlist')) as f:
    for line in f:
        if not line:
            continue
        parts = line.split()
        name = parts[0]
        whitelist.add(name)
        if len(parts) > 1 and parts[1] == 'admin':
            admin.add(name)
