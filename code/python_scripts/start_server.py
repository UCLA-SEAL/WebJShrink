from subprocess import call

call('export FLASK_APP=server.py', shell=True)
call('flask run --host=0.0.0.0 --port=5000', shell=True)
