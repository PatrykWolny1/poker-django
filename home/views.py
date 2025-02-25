import os
import json
import uuid
import time
from django.shortcuts import render
from django.http import JsonResponse, FileResponse, Http404, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from home.redis_buffer_singleton import redis_buffer_instance, redis_buffer_instance_one_pair_game
from home.MyThread import MyThread
from home.ThreadVarManagerSingleton import task_manager
from main import main
import uuid
import os
from classes.Player import Player

redis_client = redis_buffer_instance_one_pair_game.redis_1

def index(request):
    """Main index view."""
    template_data = {'title': 'Poker Simulation'}
    return render(request, 'home/index.html', {'template_data': template_data})

def cards_permutations(request):
    is_dev = os.getenv('IS_DEV', 'yes')

    # Force session creation
    if not request.session.session_key:
        request.session.save()  # This ensures a session key is generated
    print(request.session.session_key)
    print("Session ID in cards_permutations: ", request.session.session_key)
    redis_buffer_instance.redis_1.set(f'{request.session.session_key}_which_app', "cards_permutations")

    if request.method == "GET":
        return render(request, 'home/cards_permutations.html', {'is_dev': is_dev})

def one_pair_game(request):
    is_dev = os.getenv('IS_DEV', 'yes')

    # Force session creation
    if not request.session.session_key:
        request.session.save()  # This ensures a session key is generated
    
    redis_buffer_instance.redis_1.set(f'{request.session.session_key}_which_app', "one_pair_game")

    if request.method == 'GET':
        return render(request, 'home/one_pair_game.html', {'is_dev': is_dev})

def gathering_games(request):
    is_dev = os.getenv('IS_DEV', 'yes')

    # Force session creation
    if not request.session.session_key:
        request.session.save()  # This ensures a session key is generated
    
    redis_buffer_instance.redis_1.set(f'{request.session.session_key}_which_app', "gathering_games")

    if request.method == 'GET':
        return render(request, 'home/gathering_games.html', {'is_dev': is_dev})

def deep_neural_network(request):
    is_dev = os.getenv('IS_DEV', 'yes')

    # Force session creation
    if not request.session.session_key:
        request.session.save()  # This ensures a session key is generated
    
    redis_buffer_instance.redis_1.set(f'{request.session.session_key}_which_app', "deep_neural_network")

    if request.method == 'GET':
        return render(request, 'home/deep_neural_network.html', {'is_dev': is_dev})


def get_session_id(request):
    """Ensure a session exists and return its ID."""
    # Accessing request.session ensures the session exists

    if not request.session.session_key:
        request.session.create()  # Explicitly create a session if it doesn't exist
    session_key = request.session.session_key  # Retrieve the session key
    
    redis_buffer_instance.redis_1.set('session_key', session_key)

    unique_session_id = generate_unique_session_id(session_key)
    
    print("Session ID in get_session_id: ", unique_session_id)
    redis_buffer_instance.redis_1.set(f'{session_key}', unique_session_id)
    redis_buffer_instance.redis_1.set(f'{unique_session_id}', session_key)

    which_app = redis_buffer_instance.redis_1.get(f'{session_key}_which_app').decode('utf-8')
    print(which_app, session_key)
    if which_app == "cards_permutations":
        _initialize_redis_values_perms_combs(request, unique_session_id)

        _add_id_to_redis(request, f'perms_combs', unique_session_id)
        _add_id_to_redis(request, f'arrangement', unique_session_id)

        if redis_buffer_instance.redis_1.get(f'arrangement_{unique_session_id}').decode('utf-8') == '1':
            _add_id_to_redis(request, f'straight_royal_flush', unique_session_id) 

    elif which_app == "one_pair_game":
        _initialize_redis_values_gra_jedna_para(unique_session_id)
    elif which_app == "gathering_games":
        _initialize_redis_values_gathering_games(unique_session_id)
    elif which_app == "deep_neural_network":
        _initialize_redis_values_deep_neural_network(unique_session_id)


    choice = redis_buffer_instance.redis_1.get(f'choice_{unique_session_id}').decode('utf-8')

    
    print("Choice: ", choice)
    if choice == '1':
        name = "thread_perms_combs"

        task_manager.add_session(unique_session_id, name)

        task_manager.session_threads[unique_session_id][name].add_event("stop_event_progress")
        task_manager.session_threads[unique_session_id][name].add_event("stop_event_immediately")
        task_manager.session_threads[unique_session_id][name].event["stop_event_progress"].clear()
        task_manager.session_threads[unique_session_id][name].event["stop_event_immediately"].clear()
        redis_buffer_instance.redis_1.set(f'{unique_session_id}_thread_name', name)

        print(task_manager.session_threads)
        print(task_manager.session_threads[unique_session_id][name].event)

        start_thread_combs_perms(request, unique_session_id, name)
    
    elif choice == '2':
        name = "thread_one_pair_game"
        
        task_manager.add_session(unique_session_id, name)
        task_manager.session_threads[unique_session_id][name].add_event("stop_event_progress")
        task_manager.session_threads[unique_session_id][name].add_event("stop_event_croupier")
        task_manager.session_threads[unique_session_id][name].add_event("stop_event_next")
        task_manager.session_threads[unique_session_id][name].add_event("stop_event_immediately")
        task_manager.session_threads[unique_session_id][name].event["stop_event_progress"].clear()
        task_manager.session_threads[unique_session_id][name].event["stop_event_croupier"].clear()
        task_manager.session_threads[unique_session_id][name].event["stop_event_next"].clear()
        task_manager.session_threads[unique_session_id][name].event["stop_event_immediately"].clear()
        redis_buffer_instance.redis_1.set(f'{unique_session_id}_thread_name', name)
        redis_buffer_instance.redis_1.set(f'when_start_game_{unique_session_id}', '0')
        redis_buffer_instance.redis_1.set(f'when_first_{unique_session_id}', 0)
        redis_buffer_instance.redis_1.set(f'retreive_session_key_{unique_session_id}', session_key)

        start_thread_one_pair_game(request, unique_session_id, name)

    elif choice == '4':
        name = "gathering_games"

        task_manager.add_session(unique_session_id, name)

        task_manager.session_threads[unique_session_id][name].add_event("stop_event_progress")
        task_manager.session_threads[unique_session_id][name].add_event("stop_event_croupier")
        task_manager.session_threads[unique_session_id][name].add_event("stop_event_next")
        task_manager.session_threads[unique_session_id][name].add_event("stop_event_immediately")
        task_manager.session_threads[unique_session_id][name].event["stop_event_progress"].clear()
        task_manager.session_threads[unique_session_id][name].event["stop_event_croupier"].clear()
        task_manager.session_threads[unique_session_id][name].event["stop_event_next"].clear()
        task_manager.session_threads[unique_session_id][name].event["stop_event_immediately"].clear()
        redis_buffer_instance.redis_1.set(f'{unique_session_id}_thread_name', name)
        redis_buffer_instance.redis_1.set(f'when_start_game_{unique_session_id}', '0')
        redis_buffer_instance.redis_1.set(f'when_first_{unique_session_id}', 0)

        print(task_manager.session_threads)
        print(task_manager.session_threads[unique_session_id][name].event)

        start_thread_gathering_games(request, unique_session_id, name)
  
    elif choice == '5':
        name = "deep_neural_network"

        task_manager.add_session(unique_session_id, name)

        task_manager.session_threads[unique_session_id][name].add_event("stop_event_progress")
        task_manager.session_threads[unique_session_id][name].event["stop_event_progress"].clear()
        redis_buffer_instance.redis_1.set(f'{unique_session_id}_thread_name', name)
        redis_buffer_instance.redis_1.set(f'when_start_game_{unique_session_id}', '1')

        print(task_manager.session_threads)
        print(task_manager.session_threads[unique_session_id][name].event)

    return JsonResponse({"status" : f"Started thread combs_perms. ID: {unique_session_id}"})

def start_task_deep_neural_network(request):
    if request.method == "POST":
        session_key = request.session.session_key

        unique_session_id = redis_buffer_instance.redis_1.get(f'{session_key}').decode('utf-8')

        print("In start DNN: ", unique_session_id)

        name = "deep_neural_network"
        
        start_thread_deep_neural_network(request, unique_session_id, name)

        return JsonResponse({"status": "success", "message": "Creating DNN model started..."})

def stop_task_deep_neural_network(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        session_id = data.get('session_id', None)

        print("Session ID in stop_task_deep_neural_network: ", session_id)

        if session_id in task_manager.session_threads:
            task_manager.session_threads[session_id]["deep_neural_network"].event["stop_event_progress"].set()
            # task_manager.session_threads[session_id]["deep_neural_network"].event["stop_event_dnn"].set()

        if session_id in task_manager.session_threads:
            _stop_thread(request, session_id, "deep_neural_network")
        return JsonResponse({"message": f"Task stopped for session {session_id}"})
    return JsonResponse({"error": "No active session."}, status=400)

def start_task_gathering_games(request):
    if request.method == "POST":
        session_key = request.session.session_key  # Retrieve the session key

        unique_session_id = redis_buffer_instance.redis_1.get(f'{session_key}').decode('utf-8')
        print("In start_game: ", unique_session_id)
        # redis_buffer_instance.redis_1.set(f'retreive_session_key_{unique_session_id}', session_key)

        name = "gathering_games"
        task_manager.session_threads[unique_session_id][name].event["stop_event_progress"].set()
        task_manager.session_threads[unique_session_id][name].event["stop_event_croupier"].set()
        task_manager.session_threads[unique_session_id][name].event["stop_event_immediately"].set()
        task_manager.session_threads[unique_session_id][name].thread[unique_session_id].join()

        unique_session_id = generate_unique_session_id(session_key)

        _initialize_redis_values_gathering_games(unique_session_id)
        redis_buffer_instance.redis_1.set(f'when_first_{unique_session_id}', 1)
        redis_buffer_instance.redis_1.set(f'when_start_game_{unique_session_id}', '1')
        redis_buffer_instance.redis_1.set(f'get_start_game_key_{session_key}', unique_session_id)
        redis_buffer_instance.redis_1.set(f'{session_key}', unique_session_id)
        redis_buffer_instance.redis_1.set(f'retreive_session_key_{unique_session_id}', session_key)
        redis_buffer_instance.redis_1.set(f'{unique_session_id}_thread_name', name)

        task_manager.add_session(unique_session_id, name)
        task_manager.session_threads[unique_session_id][name].add_event("stop_event_progress")
        task_manager.session_threads[unique_session_id][name].add_event("stop_event_croupier")
        task_manager.session_threads[unique_session_id][name].add_event("stop_event_next")
        task_manager.session_threads[unique_session_id][name].add_event("stop_event_immediately")

        # Store thread details using the unique session ID
        task_manager.session_threads[unique_session_id][name].event["stop_event_progress"].clear()
        task_manager.session_threads[unique_session_id][name].event["stop_event_croupier"].clear()
        task_manager.session_threads[unique_session_id][name].event["stop_event_next"].clear()
        task_manager.session_threads[unique_session_id][name].event["stop_event_immediately"].clear()

        my_thread = MyThread(
            target=main,
            session_id=unique_session_id,
            name = name,
        )

        # Store thread details using the unique session ID
        task_manager.session_threads[unique_session_id][name].set_thread(unique_session_id, my_thread)
        task_manager.session_threads[unique_session_id][name].thread[unique_session_id].daemon = True
        task_manager.session_threads[unique_session_id][name].thread[unique_session_id].start()

        return JsonResponse({"status": "success", "message": "Game started"})
    
    return JsonResponse({"status": "success", "message": "WRONG"})

def stop_task_gathering_games(request):
    """Handle task stopping from POST request."""
    if request.method == 'POST':
        data = json.loads(request.body)
        session_id = data.get('session_id', None)

        print("Session ID in stop_task_gathering_games: ", session_id)

        if session_id in task_manager.session_threads:
            task_manager.session_threads[session_id]["gathering_games"].event["stop_event_progress"].set()
            task_manager.session_threads[session_id]["gathering_games"].event["stop_event_immediately"].set()
            task_manager.session_threads[session_id]["gathering_games"].event["stop_event_croupier"].set()

        if session_id in task_manager.session_threads:
            _stop_thread(request, session_id, "gathering_games")
        return JsonResponse({"message": f"Task stopped for session {session_id}"})
    return JsonResponse({"error": "No active session."}, status=400)

def start_task_combs_perms(request):
    return JsonResponse({"status" : "Starting thread for combs_perms..."})

def stop_task_combs_perms(request):
    """Handle task stopping from POST request."""
    if request.method == 'POST':
        data = json.loads(request.body)
        session_id = data.get('session_id', None)

        print("Session ID in stop_task_combs_perms: ", session_id)

        if session_id in task_manager.session_threads:
            task_manager.session_threads[session_id]["thread_perms_combs"].event["stop_event_progress"].set()
            task_manager.session_threads[session_id]["thread_perms_combs"].event["stop_event_immediately"].set()

        if session_id in task_manager.session_threads:
            _stop_thread(request, session_id, "thread_perms_combs")
        return JsonResponse({"message": f"Task stopped for session {session_id}"})
    return JsonResponse({"error": "No active session."}, status=400)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def stop_task_one_pair_game(request):
    """Handle task stopping from POST request."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')

            print(f"Received session_id: {session_id}")

            name = "thread_one_pair_game"
            if session_id in task_manager.session_threads:
                task_manager.session_threads[session_id]["thread_one_pair_game"].event["stop_event_croupier"].set()
                task_manager.session_threads[session_id]["thread_one_pair_game"].event["stop_event_progress"].set()
                task_manager.session_threads[session_id]["thread_one_pair_game"].event["stop_event_immediately"].set()

            if session_id in task_manager.session_threads:
                _stop_thread(request, session_id, name)

            return JsonResponse({"message": f"Task stopped for session {session_id}"})
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({"error": "An error occurred while processing the request."}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=400)

def download_saved_file(request):
    """Serve a saved file as an attachment download."""
    unique_session_id = redis_buffer_instance.redis_1.get(f'{request.session.session_key}').decode('utf-8')
    print(unique_session_id)
    thread_name = redis_buffer_instance.redis_1.get(f'{unique_session_id}_thread_name').decode('utf-8')

    if thread_name == 'perms_combs':
        file_path = f'permutations_data/data_perms_combs_ID_{unique_session_id}.txt'
    elif thread_name == 'gathering_games':
        file_path = f'ml_data/poker_game_one_pair_combs_all_to_update_duplicates_{unique_session_id}.csv'
    elif thread_name == 'deep_neural_network':
        file_path = f'ml_data/models_plots_predictions_{unique_session_id}.zip'

    if not os.path.exists(file_path):
        raise Http404("File not found")
    
    response = FileResponse(open(file_path, 'rb'), as_attachment=True)

    if thread_name == 'perms_combs':
        response['Content-Disposition'] = f'attachment; filename="collected_data_perms_combs_{unique_session_id}.txt"'
    elif thread_name == 'gathering_games':
        response['Content-Disposition'] = f'attachment; filename="gathered_games_{unique_session_id}.csv"'
    elif thread_name == 'deep_neural_network':
        response['Content-Disposition'] = f'attachment; filename="deep_neural_network_{unique_session_id}.zip"'

    return response

def download_all_games_saved_file(request):
    """Serve a saved file as an attachment download."""
    unique_session_id = redis_buffer_instance.redis_1.get(f'{request.session.session_key}').decode('utf-8')
    print(unique_session_id)
    thread_name = redis_buffer_instance.redis_1.get(f'{unique_session_id}_thread_name').decode('utf-8')
    
    if thread_name == 'gathering_games':
        file_path = f'ml_data/poker_game_one_pair_combs_all.csv'

    copy_games_to_all(f"ml_data/poker_game_one_pair_combs_all_to_update_duplicates_{unique_session_id}.csv",
                      "ml_data/poker_game_one_pair_combs_all.csv")
    
    if not os.path.exists(file_path):
        raise Http404("File not found")
    
    response = FileResponse(open(file_path, 'rb'), as_attachment=True)
    if thread_name == 'gathering_games':
        response['Content-Disposition'] = f'attachment; filename="all_gathered_games{unique_session_id}.csv"'

    return response  

def copy_games_to_all(all_combs_with_duplicates, file_one_pair_combs_all):
    header = "Player ID,Exchange,Exchange Amount,Cards Before 1,Cards Before 2,Cards Before 3,Cards Before 4,Cards Before 5,Card Exchanged 1,Card Exchanged 2,Card Exchanged 3,Win"
                
    with open(all_combs_with_duplicates, 'r') as source:
        with open(file_one_pair_combs_all, 'a') as destination:
            lines = source.readlines()
            if os.path.getsize(file_one_pair_combs_all) == 0:
                destination.writelines(header + "\n")
            destination.writelines(lines)

                    
    print("Plik ", all_combs_with_duplicates, " i jego wartosci zostaly skopiowane do pliku ",
            file_one_pair_combs_all)                    
                
def submit_number(request):
    """Submit a number from JSON data in POST request to Redis."""
    print(request.session.session_key)
    if request.method == "POST":
        data = json.loads(request.body)
        number = data.get("value")
        print(request.session.session_key)
        unique_session_id = redis_buffer_instance.redis_1.get(f'{request.session.session_key}').decode('utf-8')
        print(unique_session_id, number)
        redis_buffer_instance.redis_1.set(f"number_{unique_session_id}", str(number))
        return JsonResponse({"message": "Number received successfully", "value": number})
    return JsonResponse({"error": "Invalid request"}, status=400)

def start_game(request):
    if request.method == "POST":
        session_key = request.session.session_key  # Retrieve the session key

        unique_session_id = redis_buffer_instance.redis_1.get(f'{session_key}').decode('utf-8')
        print("In start_game: ", unique_session_id)
        # redis_buffer_instance.redis_1.set(f'retreive_session_key_{unique_session_id}', session_key)

        name = "thread_one_pair_game"
        task_manager.session_threads[unique_session_id][name].event["stop_event_progress"].set()
        task_manager.session_threads[unique_session_id][name].event["stop_event_croupier"].set()
        task_manager.session_threads[unique_session_id][name].event["stop_event_immediately"].set()
        task_manager.session_threads[unique_session_id][name].thread[unique_session_id].join()

        unique_session_id = generate_unique_session_id(session_key)

        _initialize_redis_values_gra_jedna_para(unique_session_id)
        redis_buffer_instance.redis_1.set(f'when_first_{unique_session_id}', 1)
        redis_buffer_instance.redis_1.set(f'when_start_game_{unique_session_id}', '1')
        redis_buffer_instance.redis_1.set(f'get_start_game_key_{session_key}', unique_session_id)
        redis_buffer_instance.redis_1.set(f'{session_key}', unique_session_id)
        redis_buffer_instance.redis_1.set(f'retreive_session_key_{unique_session_id}', session_key)


        task_manager.add_session(unique_session_id, name)
        task_manager.session_threads[unique_session_id][name].add_event("stop_event_progress")
        task_manager.session_threads[unique_session_id][name].add_event("stop_event_croupier")
        task_manager.session_threads[unique_session_id][name].add_event("stop_event_next")
        task_manager.session_threads[unique_session_id][name].add_event("stop_event_immediately")

        # Store thread details using the unique session ID
        task_manager.session_threads[unique_session_id][name].event["stop_event_progress"].clear()
        task_manager.session_threads[unique_session_id][name].event["stop_event_croupier"].clear()
        task_manager.session_threads[unique_session_id][name].event["stop_event_next"].clear()
        task_manager.session_threads[unique_session_id][name].event["stop_event_immediately"].clear()

        start_thread_one_pair_game(request, unique_session_id, name)

        return JsonResponse({"status": "success", "message": "Game started"})
    return JsonResponse({"status": "success", "message": "WRONG"})
def _initialize_redis_values_gra_jedna_para(session_id):
    """Initialize Redis values specific to gra_jedna_para."""
    redis_buffer_instance.redis_1.set(f'arrangement_{session_id}', '8')
    redis_buffer_instance.redis_1.set(f'choice_1_{session_id}', '2')
    redis_buffer_instance.redis_1.set(f'choice_{session_id}', '2')
    redis_buffer_instance.redis_1.set(f'game_si_human_{session_id}', '2')
    redis_buffer_instance.redis_1.set(f'when_one_pair_{session_id}', '1')
    redis_buffer_instance.redis_1.set(f'prog_when_fast_{session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'entered_value_{session_id}', '10982') #one_pair 1098240
    redis_buffer_instance.redis_1.set(f'player_number_{session_id}', '0')
    redis_buffer_instance.redis_1.set(f'shared_progress_{session_id}', '0')
    redis_buffer_instance.redis_1.set(f'connection_accepted_{session_id}', 'no')   
     

def _initialize_redis_values_perms_combs(request, session_id):
    redis_buffer_instance.redis_1.set(f'choice_1_{session_id}', '2')
    redis_buffer_instance.redis_1.set(f'choice_{session_id}', '1')
    number = redis_buffer_instance.redis_1.get(f'number_{request.session.session_key}').decode('utf-8')
    redis_buffer_instance.redis_1.set(f'entered_value_{session_id}', number)
    redis_buffer_instance.redis_1.set(f'prog_when_fast_{session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'min_{session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'max_{session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'count_arrangements_{session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'count_arrangements_stop_{session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'print_gen_combs_perms_{session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'shared_progress_{session_id}', '0')
    redis_buffer_instance.redis_1.set(f'connection_accepted_{session_id}', 'no')

def _initialize_redis_values_gathering_games(session_id):
    redis_buffer_instance.redis_1.set(f'arrangement_{session_id}', '8')
    redis_buffer_instance.redis_1.set(f'choice_1_{session_id}', '2')
    redis_buffer_instance.redis_1.set(f'choice_{session_id}', '4')
    redis_buffer_instance.redis_1.set(f"number_{session_id}", '-1')
    redis_buffer_instance.redis_1.set(f'entered_value_{session_id}', '1098240')
    redis_buffer_instance.redis_1.set(f'when_one_pair_{session_id}', '1')
    redis_buffer_instance.redis_1.set(f'prog_when_fast_{session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'min_{session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'max_{session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'shared_progress_{session_id}', '0')
    redis_buffer_instance.redis_1.set(f'connection_accepted_{session_id}', 'no')
    redis_buffer_instance.redis_1.set(f"gathering_games_exit_{session_id}", "-1")

def _initialize_redis_values_deep_neural_network(session_id):
    redis_buffer_instance.redis_1.set(f'choice_2_{session_id}', '1')
    redis_buffer_instance.redis_1.set(f'choice_{session_id}', '5')
    redis_buffer_instance.redis_1.set(f'entered_value_{session_id}', '1098240')
    redis_buffer_instance.redis_1.set(f'shared_progress_{session_id}', '0')
    redis_buffer_instance.redis_1.set(f'connection_accepted_{session_id}', 'no')
    
    wins_exch = redis_buffer_instance.redis_1.get(f'choice_2_{session_id}').decode('utf-8')

    if wins_exch == '1':
        binaryOutputValue = "1 - Wygrana/Przegrana"
    else:
        binaryOutputValue = "3 - Ilosc wymienianych kart"

    formData = {
            "learningRate": "0.0001",
            "batchSize": "32",
            "optimizer": "Adam",
            "activation": "relu",
            "activationOutput": "sigmoid",
            "loss": "BinaryCrossentropy",
            "layer1": "256",
            "layer2": "512",
            "layer3": "64",
            "binaryOutput": binaryOutputValue 
    }

    json_data = json.dumps(formData)

    redis_buffer_instance.redis_1.set(f'form_data_{session_id}', json_data)

def generate_unique_session_id(session_id):
    """Generate a unique identifier by combining session ID and UUID."""
    return f"{session_id}_{uuid.uuid4().hex}"

def fetch_session_id(request):
    unique_session_id = redis_buffer_instance.redis_1.get(f'{request.session.session_key}').decode('utf-8')
    return JsonResponse({'session_id': unique_session_id})

def start_thread_one_pair_game(request, unique_session_id, name):
    print("Session ID in start_thread: ", unique_session_id)
    
    my_thread = MyThread(
        target=main,
        session_id=unique_session_id,
        name = name,
    )

    # Store thread details using the unique session ID
    task_manager.session_threads[unique_session_id][name].set_thread(unique_session_id, my_thread)
    task_manager.session_threads[unique_session_id][name].thread[unique_session_id].daemon = True
    task_manager.session_threads[unique_session_id][name].thread[unique_session_id].start()
    # print(task_manager.session_threads)

    return JsonResponse({'task_status': 'Thread started', 'thread_id': unique_session_id})

def start_thread_combs_perms(request, unique_session_id, name):
    print("Session ID in start_thread: ", unique_session_id)
    perms_combs = redis_buffer_instance.redis_1.get(f'{'perms_combs'}_{unique_session_id}').decode('utf-8')
    
    if perms_combs == '1':
        perms_combs = True
    elif perms_combs == '0':
        perms_combs = False

    my_thread = MyThread(target=Player(thread=True, unique_session_id=unique_session_id, all_arrangements=False).cards_permutations, 
                        flag1=False, 
                        flag2=perms_combs, 
                        session_id=unique_session_id)
    
    task_manager.session_threads[unique_session_id][name].set_thread(unique_session_id, my_thread)
    task_manager.session_threads[unique_session_id][name].thread[unique_session_id].daemon = True
    task_manager.session_threads[unique_session_id][name].thread[unique_session_id].start()
    print(task_manager.session_threads)

    return JsonResponse({'task_status': 'Thread started', 'thread_id': unique_session_id}, status=200)

def start_thread_gathering_games(request, unique_session_id, name):
    print("Session ID in start_thread: ", unique_session_id)
    
    my_thread = MyThread(
        target=main,
        session_id=unique_session_id,
        name = name,
    )

    # Store thread details using the unique session ID
    task_manager.session_threads[unique_session_id][name].set_thread(unique_session_id, my_thread)
    task_manager.session_threads[unique_session_id][name].thread[unique_session_id].daemon = True
    task_manager.session_threads[unique_session_id][name].thread[unique_session_id].start()
    # print(task_manager.session_threads)

    return JsonResponse({'task_status': 'Thread started', 'thread_id': unique_session_id})

def start_thread_deep_neural_network(request, unique_session_id, name):
    print("Session ID in start_thread: ", unique_session_id)
    
    redis_buffer_instance.redis_1.set(f'when_first_{unique_session_id}', 1)

    my_thread = MyThread(
        target=main,
        session_id=unique_session_id,
        name = name,
    )

    # Store thread details using the unique session ID
    task_manager.session_threads[unique_session_id][name].set_thread(unique_session_id, my_thread)
    task_manager.session_threads[unique_session_id][name].thread[unique_session_id].daemon = True
    task_manager.session_threads[unique_session_id][name].thread[unique_session_id].start()
    # print(task_manager.session_threads)

    return JsonResponse({'task_status': 'Thread started', 'thread_id': unique_session_id})


def _stop_thread(request, session_id, name):
    """Stop the thread based on the unique session ID."""

    # Ensure the session ID is unique per thread
    print("Session ID in stop_thread: ", session_id)
    print("Keys in session_threads:", task_manager.session_threads.keys())

    if session_id in task_manager.session_threads and name in task_manager.session_threads:
        task_manager.session_threads[session_id][name].thread[session_id].join()  # Wait for the thread to terminate
        # task_manager.session_threads[session_id]  # TODO if there are 2 session_ids then del first 

        print(f"Thread {session_id} stopped")
        return JsonResponse({'status': 'Success on stopping thread', 'message': 'Thread stopped successfully'}, status=200)
    else:
        print(f"Thread not managed by session_threads: {session_id}")
        return JsonResponse({'status': 'Failure on stopping thread', 'message': 'Thread not managed by session_threads'}, status=500)

def permutacje(request):
    session_id = request.session.session_key
    print("Session ID in permutacje: ", session_id)
    return _toggle_redis_value(request, f'perms_combs_{session_id}', '0', 'Permutacje is ON')

def kombinacje(request):
    session_id = request.session.session_key
    print("Session ID in kombinacje: ", session_id)
    return _toggle_redis_value(request, f'perms_combs_{session_id}', '1', 'Kombinacje is ON')

def high_card(request):
    session_id = request.session.session_key
    print("Session ID in high_card: ", session_id)
    return _toggle_redis_value(request, f'arrangement_{session_id}', '9', 'High Card is ON')

def one_pair(request):
    session_id = request.session.session_key
    print("Session ID in one_pair: ", session_id)
    return _toggle_redis_value(request, f'arrangement_{session_id}', '8', 'One Pair is ON')

def two_pairs(request):
    session_id = request.session.session_key
    print("Session ID in two_pairs: ", session_id)
    return _toggle_redis_value(request, f'arrangement_{session_id}', '7', 'Two Pairs are ON')

def three_of_a_kind(request):
    session_id = request.session.session_key
    print("Session ID in three_of_a_kind: ", session_id)
    return _toggle_redis_value(request, f'arrangement_{session_id}', '6', 'Three of a Kind is ON')

def straight(request):
    session_id = request.session.session_key
    print("Session ID in straight: ", session_id)
    return _toggle_redis_value(request, f'arrangement_{session_id}', '5', 'Straight is ON')

def color(request):
    session_id = request.session.session_key
    print("Session ID in color: ", session_id)
    return _toggle_redis_value(request, f'arrangement_{session_id}', '4', 'Color is ON')

def full(request):
    session_id = request.session.session_key
    print("Session ID in full: ", session_id)
    return _toggle_redis_value(request, f'arrangement_{session_id}', '3', 'Full is ON')

def carriage(request):
    session_id = request.session.session_key
    print("Session ID in carriage: ", session_id)
    return _toggle_redis_value(request, f'arrangement_{session_id}', '2', 'Carriage is ON')

def straight_flush(request):
    session_id = request.session.session_key
    print("Session ID in straight_flush: ", session_id)
    redis_buffer_instance.redis_1.set(f'arrangement_{session_id}', '1')
    redis_buffer_instance.redis_1.set(f'straight_royal_flush_{session_id}', '0')
    return JsonResponse({'status': 'Straight Flush is ON'})

def straight_royal_flush(request):
    session_id = request.session.session_key
    print("Session ID in straight_royal_flush: ", session_id)
    redis_buffer_instance.redis_1.set(f'arrangement_{session_id}', '1')
    redis_buffer_instance.redis_1.set(f'straight_royal_flush_{session_id}', '1')
    return JsonResponse({'status': 'Straight Royal Flush is ON'})

def wins(request):
    session_id = request.session.session_key
    unique_session_id = redis_buffer_instance.redis_1.get(f"{session_id}").decode('utf-8')
    print("Session ID in Wins/Loses: ", session_id)
    redis_buffer_instance.redis_1.set(f'choice_2_{unique_session_id}', '1')
    return JsonResponse({'status': 'Wins/Loses is ON'})

def exchange(request):
    session_id = request.session.session_key
    unique_session_id = redis_buffer_instance.redis_1.get(f"{session_id}").decode('utf-8')
    print("Session ID in Exchange: ", session_id)
    redis_buffer_instance.redis_1.set(f'choice_2_{unique_session_id}', '2')
    return JsonResponse({'status': 'Exchange Amount is ON'})

def serve_plot_view(request, plot_name):
    # Path to the image created by the create_plot function
    session_key = request.session.session_key
    unique_session_id = redis_buffer_instance.redis_1.get(session_key).decode('utf-8')
    image_path = f'plots/{plot_name}_{unique_session_id}.png'
    image_data = open(image_path, 'rb').read()
    return HttpResponse(image_data, content_type='image/png')

def apply_form_view(request):
    if request.method == 'POST':
        try:
            # Parse the JSON body of the request
            unique_session_id = redis_buffer_instance.redis_1.get(request.session.session_key).decode('utf-8')
            redis_buffer_instance.redis_1.set(f'form_data_{unique_session_id}', request.body)
            data = json.loads(request.body)
            
            # Extract values from the data
            learning_rate = data.get('learningRate')
            batch_size = data.get('batchSize')
            optimizer = data.get('optimizer')
            activation = data.get('activation')
            activation_output = data.get('activationOutput')
            loss = data.get('loss')
            layer1 = data.get('layer1')
            layer2 = data.get('layer2')
            layer3 = data.get('layer3')
            binary_output = data.get('binaryOutput')
            
            print("Received form data:")
            print(f"Learning Rate: {learning_rate}")
            print(f"Batch Size: {batch_size}")
            print(f"Optimizer: {optimizer}")
            print(f"Activation: {activation}")
            print(f"Activation Output: {activation_output}")
            print(f"Loss: {loss}")
            print(f"Layer 1: {layer1}, Layer 2: {layer2}, Layer 3: {layer3}")
            print(f"Binary Output: {binary_output}")
            
            # Return a JSON response indicating success.
            return JsonResponse({'status': 'success', 'message': 'Form data processed successfully.'})
        except Exception as e:
            # Return an error response if something went wrong
            return JsonResponse({'status': 'error', 'error': str(e)}, status=400)
    
    # If the request method is not POST, return a 405 Method Not Allowed response.
    return HttpResponseBadRequest("Only POST requests are allowed.")

# Utility function to toggle Redis values
def _toggle_redis_value(request, key, value, status_message):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set(key, value)
        return JsonResponse({'status': status_message})
    return JsonResponse({'status': 'Invalid request'}, status=400)

def _add_id_to_redis(request, key, session_id):
    value = redis_buffer_instance.redis_1.get(f'{key}_{request.session.session_key}').decode('utf-8')
    redis_buffer_instance.redis_1.set(f'{key}_{session_id}', value)
    print(f"After adding id to redis key: {key}_{session_id} = {value}")

def get_redis_value(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        body = json.loads(request.body)
        session_id = body.get("session_id")  # Extract the key from the JSON body
        if not session_id:
            return JsonResponse({"error": "Session ID is missing"}, status=400)
        
        print(f"Received key: {session_id}")
        
        task_manager.session_threads[session_id]["thread_one_pair_game"].event["stop_event_next"].set()
        
        return JsonResponse({"message": f"Next clicked!"})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
def goodbye(request):
    return render(request, 'home/goodbye.html', {'message': 'We’re sorry, but cookies are required to use this site. Przepraszamy, ale pliki cookie są niezbędne do korzystania z tej strony.'})