echo "BUILD START"
python3.10 -m ensurepip
echo "pip install"
python3.10 -m pip install -r requirements.txt
echo "manage.py"
python3.10 manage.py collectstatic --noinput --clear
echo "BUILD END"