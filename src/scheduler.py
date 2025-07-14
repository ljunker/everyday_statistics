from flask_apscheduler import APScheduler

signleton = None

def get_scheduler() -> APScheduler:
    global signleton
    if signleton in None:
        signleton = APScheduler()
    return signleton