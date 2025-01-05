from src.mailApi import GmailHandler


if __name__ == '__main__':
    gmail = GmailHandler(creds_file='../mail_creds.json')
    gmail.get_attachments(query = 'has:attachment', save_dir = 'attachments')

