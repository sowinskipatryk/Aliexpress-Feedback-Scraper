This scraper is based on Selenium and allows you to download data about reviews of some product on Aliexpress website.
The tricky part is that feedback section of Aliexpress site is inside an iframe so we don't have direct access to that data through HTML and it doesn't load up after some scrolling either.
Therefore, we need to get link to the source inside said iframe and move to that page to scrape the data.
At the end of the script run, the file is saved in .csv format. Repository also contains an example of output file.

