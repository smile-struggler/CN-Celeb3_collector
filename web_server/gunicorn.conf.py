workers = 4
threads = 2
worker_connections = 2000

bind = '0.0.0.0:36923'

daemon = 'false'
worker_class = 'gevent'

pidfile = './gunicorn.pid'

accesslog = "log/access.log"
loglevel = 'warning'
errorlog = "log/debug.log"
loglevel = "debug"
