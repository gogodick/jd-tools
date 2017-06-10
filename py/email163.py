# -*- coding: utf-8 -*-
import smtplib
import email.MIMEMultipart# import MIMEMultipart
import email.MIMEText# import MIMEText
import email.MIMEBase# import MIMEBase
import os.path
import argparse
import mimetypes
import email.MIMEImage# import MIMEImage

def send_mail(user, pwd, to, file_name):
    sender = user+"@163.com"
    server = smtplib.SMTP("smtp.163.com")
    try:
        server.login(user,pwd) # For SMTP auth
    except Exception, e:
        print "Auth failed!"
        return
    # Construct MIMEMultipart
    main_msg = email.MIMEMultipart.MIMEMultipart()

    # Construct MIMEText
    text_msg = email.MIMEText.MIMEText("Please check the attachment!",_charset="utf-8")
    main_msg.attach(text_msg)

    # Construct MIMEBase
    ctype,encoding = mimetypes.guess_type(file_name)
    if ctype is None or encoding is not None:
        ctype='application/octet-stream'
    maintype,subtype = ctype.split('/',1)
    file_msg=email.MIMEImage.MIMEImage(open(file_name,'rb').read(),subtype)
    print ctype,encoding

    ## Add header
    basename = os.path.basename(file_name)
    file_msg.add_header('Content-Disposition','attachment', filename = basename)
    main_msg.attach(file_msg)

    # Set message
    main_msg['From'] = sender
    main_msg['To'] = to
    main_msg['Subject'] = "Test Result: " + email.Utils.formatdate( )
    main_msg['Date'] = email.Utils.formatdate( )

    # Get full text
    fullText = main_msg.as_string( )

    # Send mail to SMTP
    try:
        server.sendmail(sender, to, fullText)
    finally:
        server.quit()

if __name__ == '__main__':
    # help message
    parser = argparse.ArgumentParser(description='Send email with attachment')
    parser.add_argument('-u', '--user', 
                        help='User', required=True)
    parser.add_argument('-p', '--pwd', 
                        help='Password', required=True)
    parser.add_argument('-t', '--to', 
                        help='Email to who', required=True)
    parser.add_argument('-f', '--file', 
                        help='Attach file', required=True)
                        
    options = parser.parse_args()
    print options
    send_mail(options.user, options.pwd, options.to, options.file)

    
    