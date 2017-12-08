from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from chatbot import Chat, reflections, multiFunctionCall
import requests
from django.views.decorators.csrf import csrf_exempt

pairs = (
  ("(Do you know about|what is|who is|tell me about|tell me something about)(.*)",
  ("{% call whoIs:%2 %}",)),
  ("(Show|display|recently|recent)(.*)",
   ("{% call results:%2 %}",))
)


def whoIs(query, sessionID="general"):
    try:
        response = requests.get('http://api.stackexchange.com/2.2/tags/' + query + '/wikis?site=stackoverflow')
        data = response.json()
        return data['items'][0]['excerpt']
    except:
        pass
    return "Oh, You misspelled somewhere!"


def results(query, sessionID="general"):
    query_list = query.split(' ')
    query_list = [x for x in query_list if x not in ['posted', 'questions', 'recently', 'recent', 'display', '', 'show']]
    # print(query_list)
    if len(query_list) == 1:
        # print('con 1')
        try:
            response = requests.get('https://api.stackexchange.com/2.2/questions?pagesize=5&order=desc&sort=activity&tagged=' + query_list[0] + '&site=stackoverflow')
            data = response.json()
            data_list = [data['items'][i]['title'] for i in range(5)]
            return '<br/>'.join(data_list)
        except:
            pass
    elif len(query_list) == 2 and 'unanswered' not in query_list:
        # print('con 2')
        query_list = sorted(query_list)
        n = query_list[0]
        tag = query_list[1]
        try:
            response = requests.get('https://api.stackexchange.com/2.2/questions?pagesize='+ n +'&order=desc&sort=activity&tagged=' + tag + '&site=stackoverflow')
            data = response.json()
            data_list = [data['items'][i]['title'] for i in range(int(n))]
            return '<br/>'.join(data_list)
        except:
            pass

    else:
        # print('con 3')
        query_list = [x for x in query_list if x not in ['which', 'where', 'whos', 'who\'s' 'is', 'are', 'answered', 'not', 'unanswered', 'of', 'for']]
        # print(query_list)
        if len(query_list) ==1:
            try:
                response = requests.get(
                    'https://api.stackexchange.com/2.2/questions/no-answers?pagesize=5&order=desc&sort=activity&tagged=' + query_list[0] + '&site=stackoverflow')
                data = response.json()
                data_list = [data['items'][i]['title'] for i in range(5)]
                return '<br/>'.join(data_list)
            except:
                pass
        elif len(query_list) == 2:
            query_list = sorted(query_list)
            n = query_list[0]
            tag = query_list[1]
            try:
                response = requests.get(
                    'https://api.stackexchange.com/2.2/questions/no-answers?pagesize='+ n +'&order=desc&sort=activity&tagged=' + tag + '&site=stackoverflow')
                data = response.json()
                data_list = [data['items'][i]['title'] for i in range(int(n))]
                return '<br/>'.join(data_list)
            except:
                pass
    return "Oh, You misspelled somewhere!"


#Display recent 3 python questions which are not answered
firstQuestion = "Hi, How may i help you?"

call = multiFunctionCall({"whoIs": whoIs,
                              "results": results})

chat = Chat(pairs, reflections, call=call)


def initiateChat():
    chat._startNewSession("general")
    chat.conversation["general"].append("Hi!.")


def Home(request):
    return render(request, "alpha/home.html", {'home': 'active', 'chat': 'chat'})


@csrf_exempt
def Post(request):
    while len(chat.conversation["general"])<2:
        chat.conversation["general"].append('initiate')
    if request.method == "POST":
        query = request.POST.get('msgbox', None)
        response = chat.respond(query)
        chat.conversation["general"].append(response)
        return JsonResponse({'msg': response, 'user': 'user'})
    else:
        return HttpResponse('Request must be POST.')

