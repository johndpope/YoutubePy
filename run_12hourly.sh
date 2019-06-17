if [ "$1" = "install" ]
then
    sudo python -m virtualenv env3
fi

source env3/bin/activate

if [ "$1" = "install" ]
then
    pip install -r requirements.txt
    python savecookie.py
fi

python update_cache.py# -headless 1
bash clean_data.sh
python youtube_comment_to_win_giveaway.py# -headless 1
