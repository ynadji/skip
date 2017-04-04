# installing

open Terminal.app. lines beginning with `$` should be typed into the terminal
and end hitting the `Enter` key. lines beginning with `#` are explanatory
comments. if you're using OS X's Terminal.app instead of typing paths you can
(e.g. the `path/to/reviews.xslx` part) you can just drag & drop the xlsx file
into the terminal and it will fill it out for you.

```
$ git clone git@github.com:ynadji/skip.git
$ cd skip
# if on OS X
$ sudo easy_install pip
$ pip install --user -r requirements.txt
$ python parse.py path/to/reviews.xslx
```

If you do not have `NLTK` installed (you probably won't on the first run) the
script will prompt you to do so. After installing everything, re-run the above
`python parse.py ...` command.
