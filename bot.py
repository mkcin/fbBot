import fbchat as fb
from config import LOGIN, PASSWORD, FB_TARGET, FB_CONTACTS
import time

class Bot(fb.Client):
    def __init__(self, email, password, user_agent=None, max_tries=5, session_cookies=None, logging_level=fb.logging.INFO):
        super().__init__(email, password, user_agent, max_tries, session_cookies, logging_level)
        while(not self.isLoggedIn()):
            print('retrying...')
            super().__init__(email, password, user_agent, max_tries, session_cookies, logging_level)
        print('logged in!\nconnecting to my target...')
        self._target = self.searchForUsers(FB_TARGET)
        while(len(self._target)==0):
            print('retrying...')
            self._target = self.searchForUsers(FB_TARGET)
        self._target = self._target[0]
        print('found user - {}'.format(self._target.name))
        print('uid = {}'.format(self._target.uid))
        print('photo - {}'.format(self._target.photo))
        self._contacts = {}
        self._contactList=''
        self.connectToContacts()
        self._lastMessage = None
        self._isListening = False

    def start(self):
        self._waitingForNumber = False
        self._waitingForMessage = False
        self._receiver = None
        self._isListening = True
        self.startListening()
        while self._isListening:
            self.doOneListen()
            time.sleep(1)
        self.stopListening()
        self.logout()

    def connectToContacts(self):
        print('connecting to my contacts...')
        count = 1
        for contact in FB_CONTACTS:
            print('connecting to user {}'.format(contact))
            c = self.searchForUsers(contact)
            while(len(c)==0):
                print('retrying')
                c = self.searchForUsers(contact)
            c = c[0]
            print('connected! photo - {}'.format(c.photo))
            self._contacts.update({count:c})
            count = count + 1
        for key, value in self._contacts.items():
            self._contactList = str(str(self._contactList) + str(key) + '. ' + str(value.name) + '\n')

    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        if(message_object==self._lastMessage):
            print('widzialem te wiadomosc')
        else:
            if(author_id==self.uid):
                print('wiadomosc ode mnie')
            elif(author_id == self._target.uid):
                if(message_object.text == 'Exit'):
                    self.send(fb.Message(text='ok, finishing my job here, have a good day :>'), thread_id=self._target.uid, thread_type=fb.ThreadType.USER)
                    print('exiting because my master told me so.')
                    self._isListening = False
                elif(message_object.text=='S'):
                    self.send(fb.Message(text='Who would you wish to text?\n{}send \"###\" to cancel'.format(self._contactList)), thread_id=self._target.uid, thread_type=fb.ThreadType.USER)
                    self._waitingForNumber = True
                elif(message_object.text=='###'):
                    print('sending message canceled')
                    self._waitingForNumber = False
                    self._waitingForMessage = False
                    self._receiver = None
                elif(self._waitingForNumber and not self._waitingForMessage and message_object.text.isdigit()):
                    if(self._contacts[int(message_object.text)] != None):
                        self.send(fb.Message(text='{} chosen, message:'.format(self._contacts[int(message_object.text)].name)), thread_id=self._target.uid, thread_type=fb.ThreadType.USER)
                        self._receiver = self._contacts[int(message_object.text)]
                        self._waitingForMessage = True
                    else:
                        self.send(fb.Message(text='index out of range, cancelling'), thread_id=self._target.uid, thread_type=fb.ThreadType.USER)
                        self._waitingForNumber = False
                        self._waitingForMessage = False
                        self._receiver = None
                elif(self._waitingForMessage):
                    self.send(message_object, thread_id=self._receiver.uid, thread_type=fb.ThreadType.USER)
                    self.send(fb.Message(text='message sent to {}'.format(self._receiver.name)), thread_id=self._target.uid, thread_type=fb.ThreadType.USER)
                    self._waitingForMessage = False
                    self._waitingForNumber = False
                    self._receiver = None
            else:
                self.send(message_object, thread_id=self._target.uid, thread_type=fb.ThreadType.USER)
            self._lastMessage=message_object

if __name__ == '__main__':
    client = Bot(LOGIN, PASSWORD)
    client.start()
    # client.listen()
