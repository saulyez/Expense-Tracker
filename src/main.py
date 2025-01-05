from mailApi import GmailHandler


if __name__ == '__main__':
    gmail = GmailHandler(creds_file='../mail_creds.json', token_file='./mail_token.pickle')
    gmail.get_attachments(save_dir = 'attachments')

