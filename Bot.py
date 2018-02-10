import fbchat as fb
from config import LOGIN, PASSWORD, FB_TARGET
import time

class Bot(fb.Client):
    def __init__(self, email, password, user_agent=None, max_tries=5, session_cookies=None, logging_level=fb.logging.INFO):
        super().__init__(email, password, user_agent, max_tries, session_cookies, logging_level)
        while(not self.isLoggedIn()):
            print('retrying...')
            super().__init__(email, password, user_agent, max_tries, session_cookies, logging_level)
        print('logged in!')
        self._target = self.searchForUsers(FB_TARGET)[0]
        self._lastMessage = None
        print('found user - {}, uid = {}\nphoto - {}'.format(self._target.name, self._target.uid, self._target.photo))

        self._isListening = False

    def start(self):
        self._isListening = True
        self.startListening()
        while self._isListening:
            self.doOneListen()
            time.sleep(5)
        self.stopListening()
        self.logout()


    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        # self.markAsDelivered(author_id, thread_id)
        # self.markAsRead(author_id)
        if(message_object==self._lastMessage):
            print('widzialem te wiadomosc')
        else:
            if(author_id==self.uid):
                print('wiadomosc ode mnie')
            elif(author_id == self._target.uid and message_object.text=='exit'):
                self.send(fb.Message(text='ok, finishing my job here, have a good day :>'), thread_id=self._target.uid, thread_type=fb.ThreadType.USER)
                print('exiting because my master told me so.')
                self._isListening = False
            else:
                self.send(message_object, thread_id=self._target.uid, thread_type=fb.ThreadType.USER)
            self._lastMessage=message_object
        # print(author_id + " " + self._target.uid)
        # print(thread_type==fb.ThreadType.USER)
        # self.send(message_object, thread_id=author_id, thread_type=thread_type)

        #
        # log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))
        # pass

if __name__ == '__main__':
    client = Bot(LOGIN, PASSWORD)
    client.start()
    # client.listen()
