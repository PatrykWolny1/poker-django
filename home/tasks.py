from celery import shared_task
import subprocess

@shared_task
def run_python_script():
    result = subprocess.run(['python', 'hello.py'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')