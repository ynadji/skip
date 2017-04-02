# installing

all in the terminal:

```
$ git clone git@github.com:ynadji/skip.git
$ cd skip
$ pip install --user -r requirements.txt
$ python parse.py path/to/reviews.xslx
```

If you do not have `NLTK` installed (you probably won't on the first
run) the script will prompt you to do so. After installing everything,
re-run the above `python parse.py ...` command.
