from django.shortcuts import render
from .forms import ScriptForm
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
    form = ScriptForm()
    return render(request, 'home/input_form.html', {'form': form})

