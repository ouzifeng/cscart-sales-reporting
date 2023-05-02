# CS-Cart Sales Report:

The reporting function in CS Cart leaves a lot to be desired. This Python script solves this

When run it will build a table ranking the most popular products sold over the past 365 days, with 30, 60, 90, 180 and 365 day breakdowns.

After querying the database it will build a CSV and email it to you

INSTRUCTIONS

1. Fill out your database credentials in lines 10 and 11

2. It is setup to use AWS as the SMTP provider, input your credentials in lines 64-67. If you aren't using AWS you can input other service provider credentials in this block as well

3. Trigger it via the CMD line, or setup a monthly cron on your server 
