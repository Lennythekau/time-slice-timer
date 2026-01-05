from datetime import datetime
from time import sleep


def show(date: datetime = datetime.now()):
    print(date)


show()
sleep(1)
show(datetime.now())
sleep(1)
show()
