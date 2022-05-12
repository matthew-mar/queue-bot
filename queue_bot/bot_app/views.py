import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from bot_app.models import Queue
import random


@csrf_exempt
def add_queue_member(requset):
    if requset.method == "POST":
        queue_members = requset.POST["data"]
        queue: Queue = Queue.objects.filter(queue_name="a")[0]
        qm = json.loads(queue.queue_members)
        print(qm)
        qm.append({"member": random.randint(1_000_000, 10_000_000)})
        queue.queue_members = json.dumps(qm)
        queue.save()
    return JsonResponse(data={"response": 200})
