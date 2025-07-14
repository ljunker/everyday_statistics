from flask_apscheduler import APScheduler

signleton = None

def get_scheduler() -> APScheduler:
    global signleton
    if signleton is None:
        signleton = APScheduler()
    return signleton