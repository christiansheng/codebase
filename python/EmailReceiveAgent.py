import re
import email
import imaplib
from pprint import pprint


class EmailReceiveAgent:
    def __init__(self, auth, host="imap.exmail.qq.com"):
        self.agent = imaplib.IMAP4_SSL(host=host, port=imaplib.IMAP4_SSL_PORT)
        self._login(auth)

    def _login(self, auth):
        self.agent.login(auth['username'], auth['password'])
        self.agent.select("INBOX")

    def get_unseen_uids(self):
        result, data = self.agent.uid('search', None, "UNSEEN")
        if result == 'OK' and data:
            uids = data[0].decode().split()
            return uids
        return None

    def fetch_raw_by_uid(self, uid):
        result, data = self.agent.uid('fetch', uid, '(RFC822)')
        if result == 'OK' and data:
            raw_email = data[0][1].decode()
            return raw_email
        return None

    def fetch_msg_by_uid(self, uid):
        raw = self.fetch_raw_by_uid(uid)
        msg = email.message_from_string(raw)
        # return msg.items()
        return msg

    @staticmethod
    def parse_email_by_msg(msg):
        content = ''
        file_list = []
        # check every mime data block
        for part in msg.walk():
            if not part.is_multipart():
                # if it is multipart, the data is of no use. (knowing more about 'mime', will help u understand it.)
                # content_type = part.get_content_type()
                file_name = part.get_filename()
                if file_name:
                    # for decode purpose
                    h = email.header.Header(file_name)
                    dh = email.header.decode_header(h)
                    file_name = dh[0][0]
                    encode = dh[0][1]
                    # decode file as unicode-based
                    file_name = file_name.decode(encode, 'ignore')
                    # get content of the attachment file
                    file_data = part.get_payload(decode=True)
                    file_list.append({
                        "file_name": file_name,
                        "file_data": file_data
                    })
                else:
                    # email text content
                    content = part.get_payload(decode=True)

        print(msg)
        tmp = email.header.decode_header(msg['Subject'])[0]
        subject = tmp[0] if tmp[1] is None else tmp[0].decode(tmp[1])
        tmp = email.header.decode_header(msg['From'])[0]
        source = tmp[0] if tmp[1] is None else tmp[0].decode(tmp[1])

        return {
            'source': source,
            'subject': subject,
            "content": content.decode(),
            "file_list": file_list
        }

    def parse_email_by_uid(self, uid):
        msg = self.fetch_msg_by_uid(uid)
        return self.parse_email_by_msg(msg)

    def set_as_seen_by_uid(self, uid):
        self.agent.uid('store', uid, '+FLAGS', '\\Seen')

if __name__ == "__main__":
    login_auth = {
        'username': "user@xxx.com",
        'password': "password"
    }

    agent = EmailReceiveAgent(auth=login_auth, host="imap.exmail.qq.com")
    unseen_uids = agent.get_unseen_uids()
    print(unseen_uids)
    resumes = []
    for k, i in enumerate(unseen_uids):
        # print(k)
        agent.set_as_seen_by_uid(i)
        m = agent.parse_email_by_uid(i)
        pprint(m)
