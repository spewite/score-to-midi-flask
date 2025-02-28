
capture_output = True
bind = ":5000"
workers = 3
worker_class = "sync"
loglevel = "info"

# Logs de acceso y error
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"

# Formato del log de acceso
access_log_format = "%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s"
