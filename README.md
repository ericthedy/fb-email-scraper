# Facebook Email Scraper

As a marketer thre is a need to be able to scrape emails from websites. Some websites do not show emails at all. But most of them will show a 
Facebook Business page url somewhere. Many times you will find a valid email on the Facebook Business page.

This script takes a csv file as the input and scrapes all page urls in the spreasheet for emials using regex. To add complexity the scrape
changes browsers before hitting the limit of pages that can be pulled up on facebook with visible data before being forced to login.
The output is logged in a new csv file which is output in the same directory as the script file.

Requires brokwser drivers to work. 
Chrome Driver, Edge Driver, and Firefox drivers are needed and should be located in the same directoy with this script.

Utlizes BeautifuSoup and Selenium
