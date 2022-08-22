from django.shortcuts import redirect
from psu_base.classes.Log import Log
from demo.models import DemoOne, DemoTwo
import random
import string
log = Log()


def index(request):

    new_d = DemoOne()
    new_d.code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    new_d.title = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
    new_d.priority = random.choice(range(1, 9))
    new_d.active = random.choice([True, False])
    new_d.save()

    new_d2 = DemoTwo()
    new_d2.parent = new_d
    new_d2.detail = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
    new_d2.save()

    return redirect('export:status')
