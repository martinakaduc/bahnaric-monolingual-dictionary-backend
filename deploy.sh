export SCRIPT_NAME=/bahnar/monolingual-dictionary/
gunicorn --config gunicorn-cfg.py run:app
