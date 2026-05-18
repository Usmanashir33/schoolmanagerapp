# create service to send data to websocket from signals and views using celery tasks to avoid blocking the main thread and to ensure that the data is sent even if the user is not actively viewing the page at the time of the update
from celery import shared_task
class SchoolServices:
    
    @staticmethod
    @shared_task(bind=True, name="send_activity_log",max_retries=2)
    def send_activity_log(self, destination, data):
        from core.websocketutils import signal_sender
        try :
            signal_sender(destination, data)
        except Exception as e:
            # log the error and retry the task after some time
            self.retry(countdown=10)  # retry after 10 seconds