echo "BUILD START"
python3.9 -m ensurepip
echo "pip install"
python3.9 -m pip install -r requirements.txt
#echo "manage.py"
#python3.9 manage.py collectstatic --noinput --clear
echo "BUILD END"