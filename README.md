# YoutubePy

## Installation:
It is recomended to use via pyenv We will be supporting python 3.6.0 and above going forward

```
pip install --upgrade pip
curl https://pyenv.run | bash
curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
pyenv local 3.6.0
pip install --upgrade git+https://github.com/socialbotspy/SocialCommons.git
pip install -r requirements.txt
```

##  APIs:
  - [search and comment](#search-and-comment)

### search and comment

```python

 session = YoutubePy()

 with smart_run(session):
    session.search_and_comment(search_query="instagram bot")
 ```


## How to run:

 -  modify `quickstart.py` according to your requirements
 -  `python quickstart.py -u <my_google_username> -p <mypssword>`


## How to schedule as a job:

```bash
    */10 * * * * bash /path/to/YoutubePy/run_youtubepy_only_once_for_mac.sh /path/to/YoutubePy/quickstart.py $USERNAME $PASSWORD
```

## Help build socialbotspy
Check out this short guide on [how to start contributing!](https://github.com/InstaPy/instapy-docs/blob/master/CONTRIBUTORS.md).




