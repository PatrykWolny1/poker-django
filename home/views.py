from django.shortcuts import render
from .tasks import run_python_script
from django.http import JsonResponse
from celery.result import AsyncResult
import subprocess


def index(request):
    template_data = {}
    template_data['title'] = 'Poker Game'
    return render(request, 'home/index.html', {'template_data': template_data})

def permutacje(request):
    template_data = {}
    template_data['title'] = 'Permutacje'
    return render(request, 'home/permutacje.html', {'template_data': template_data, })

# def run_script(request):
#     result = subprocess.run(['python', 'main.py'], stdout=subprocess.PIPE)
#     output = result.stdout.decode('utf-8')
#     return render(request, 'home/run_script.html', {'output': output})

def run_script(request):
    task = run_python_script.delay()
    return render(request, 'home/run_script.html', {'task_id': task.id})

def task_status(request, task_id):
    task = AsyncResult(task_id)
    if task.state == 'SUCCESS':
        return JsonResponse({'output': task.result})
    else:
        return JsonResponse({'output': 'Task is still running...'})