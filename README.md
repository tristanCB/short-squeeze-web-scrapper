# Python program to web scrape short percent of float for all SPX500 companies
Uses beautiful soup to web scrape data from http://shortsqueeze.com/. This script launches an automated chrome window which opens short squeeze.com at a ticker taken from the SPX500 list itscrapped from [wikipedia page](http://en.wikipedia.org/wiki/List_of_S%26P_500_companies).
This program configure selenium's chrome webdrive to use Tor's (free browser) proxy. This enables us to get more than the limited daily quotes from short squeeze which are based on public I.P. address. Tor must be open while the program runs.

It outputs a file (result.csv) file in the directory from which the script was executed.

# Example use
```
python shortScanner.py --outputFileName results.csv
```
[Example results](./ExampleResults.csv) for ‎July ‎7, ‎2020.

# Requirements
install [python 3](https://www.python.org/downloads)

install [Tor](https://www.torproject.org/download/) browser

install required python packages:

```pip install urllib```

```pip install beautifulsoup4```

```pip install requests```

```pip install selenium```

```pip install pandas```
	
Have TOR browser open while the script is running