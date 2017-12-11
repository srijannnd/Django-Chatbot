from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from chatbot import Chat, reflections, multiFunctionCall
import requests, os
from django.views.decorators.csrf import csrf_exempt
from .models import Conversation


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
    query_list = [x for x in query_list if x not in ['posted', 'questions', 'recently', 'recent', 'display', '', 'in', 'of', 'show']]
    # print(query_list)
    if len(query_list) == 1:
        # print('con 1')
        try:
            response = requests.get('https://api.stackexchange.com/2.2/questions?pagesize=5&order=desc&sort=activity&tagged=' + query_list[0] + '&site=stackoverflow')
            data = response.json()
            data_list = [str(i+1)+'. ' + data['items'][i]['title'] for i in range(5)]
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
            data_list = [str(i+1)+'. ' + data['items'][i]['title'] for i in range(int(n))]
            return '<br/>'.join(data_list)
        except:
            pass

    else:
        # print('con 3')
        query_list = [x for x in query_list if x not in ['which', 'where', 'whos', 'who\'s' 'is', 'are', 'answered', 'not', 'unanswered', 'for', 'of', 'for']]
        # print(query_list)
        if len(query_list) ==1:
            try:
                response = requests.get(
                    'https://api.stackexchange.com/2.2/questions/no-answers?pagesize=5&order=desc&sort=activity&tagged=' + query_list[0] + '&site=stackoverflow')
                data = response.json()
                data_list = [str(i+1)+'. ' + data['items'][i]['title'] for i in range(5)]
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
                data_list = [str(i+1)+'. ' + data['items'][i]['title'] for i in range(int(n))]

                return '<br/>'.join(data_list)
            except:
                pass
    return "Oh, You misspelled somewhere!"


#Display recent 3 python questions which are not answered
firstQuestion = "Hi, How may i help you?"

call = multiFunctionCall({"whoIs": whoIs,
                              "results": results})

chat = Chat(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "chatbotTemplate",
                         "Example.template"
                         ),
            reflections, call=call)


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
        #c = Conversation(query=query, response=response)
        return JsonResponse({'response': response, 'query': query})
    else:
        return HttpResponse('Request must be POST.')


'''
def Post(request):
    if request.method == "POST":
        msg = request.POST.get('msgbox', None)
        c = Chat(message=msg)
        if msg != '':
            c.save()
        return JsonResponse({'msg': msg, 'user': 'user'})
    else:
        return HttpResponse('Request must be POST.')'''

