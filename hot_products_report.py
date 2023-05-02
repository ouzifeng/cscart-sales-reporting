import pymysql
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

# Connect to the database
db = pymysql.connect(host='localhost', user='your_username',
                     password='your_password', database='your_database')
cursor = db.cursor()

# Generate the SQL query to populate the table
query = '''
INSERT INTO products_sold_more_than_once (product_id, product_name, total_purchases)
SELECT od.product_id, pd.product, COUNT(*) as total_purchases
FROM cscart_order_details od
JOIN cscart_products p ON od.product_id = p.product_id
JOIN cscart_product_descriptions pd ON p.product_id = pd.product_id
GROUP BY od.product_id
HAVING COUNT(*) > 1
ORDER BY total_purchases DESC;

UPDATE products_sold_more_than_once psm
LEFT JOIN (
    SELECT 
        od.product_id, 
        COUNT(*) as total_purchases,
        SUM(CASE WHEN co.timestamp >= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 30 DAY)) THEN 1 ELSE 0 END) AS last_30_days,
        SUM(CASE WHEN co.timestamp BETWEEN UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 60 DAY)) AND UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 31 DAY)) THEN 1 ELSE 0 END) AS last_60_days,
        SUM(CASE WHEN co.timestamp BETWEEN UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 90 DAY)) AND UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 61 DAY)) THEN 1 ELSE 0 END) AS last_90_days,
        SUM(CASE WHEN co.timestamp BETWEEN UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 180 DAY)) AND UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 91 DAY)) THEN 1 ELSE 0 END) AS last_180_days,
        SUM(CASE WHEN co.timestamp BETWEEN UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 360 DAY)) AND UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 181 DAY)) THEN 1 ELSE 0 END) AS last_360_days
    FROM cscart_order_details od
    JOIN cscart_orders co ON od.order_id = co.order_id
    GROUP BY od.product_id
) as temp ON psm.product_id = temp.product_id
SET psm.total_purchases = temp.total_purchases,
    psm.last_30_days = temp.last_30_days,
    psm.last_60_days = temp.last_60_days,
    psm.last_90_days = temp.last_90_days,
    psm.last_180_days = temp.last_180_days,
    psm.last_360_days = temp.last_360_days;

'''

# Execute the SQL query
cursor.execute(query)
db.commit()

# Export the resulting table as a CSV file
filename = f"products_sold_more_than_once_{datetime.now().strftime('%Y-%m-%d')}.csv"
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    # Check if the query returned any rows
    if cursor.description is not None:
        writer.writerow([i[0] for i in cursor.description])
        writer.writerows(cursor.fetchall())
    else:
        print("No rows returned from SQL query")

# Connect to the SMTP server
smtp_server = "email-smtp.eu-west-2.amazonaws.com"
smtp_port = 587
smtp_username = "your_smtp_username"
smtp_password = "your_smtp_password"
smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
smtp_connection.starttls()
smtp_connection.login(smtp_username, smtp_password)

# Compose the email message
msg = MIMEMultipart()
msg['From'] = 'add the email address it id being sent from'
msg['To'] = 'add the email address you want the report sent to'
msg['Subject'] = 'Monthly hot products report'

body = "Please find attached the monthly report on products sold more than once"

# Attach the CSV file to the email
with open(filename, 'rb') as f:
    attachment = MIMEApplication(f.read(), _subtype='csv')
    attachment.add_header('content-disposition',
                          'attachment', filename=filename)
    msg.attach(attachment)

# Add the body to the email message
msg.attach(MIMEText(body))

# Send the email
smtp_connection.sendmail(sender, recipient, msg.as_string())

# Close the SMTP connection
smtp_connection.quit()
