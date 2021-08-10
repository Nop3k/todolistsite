from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import ToDoList
from .forms import CreateNewList


# Create your views here.

def index(response, id):
    ls = ToDoList.objects.get(id=id)

    if ls in response.user.todolist.all():
        if response.method == "POST":

            if response.POST.get("save"):
                for item in ls.item_set.all():
                    if response.POST.get("c" + str(item.id)):
                        item.complete = True
                    else:
                        item.complete = False

                    item.save()

            elif response.POST.get("newItem"):
                txt = response.POST.get("new")

                if len(txt) > 2:
                    ls.item_set.create(text=txt, complete=False)
                else:
                    print("Invalid input")
        return render(response, "main/list.html", {"ls": ls})
    else:
        return render(response, "main/view.html", {})


def home(response):
    item_count = 0
    if response.user.is_authenticated:
        list_count = len(response.user.todolist.all())
        for list in response.user.todolist.all():
            for item in list.item_set.all():
                item_count += 1
        print(item_count)
    else:
        list_count = 0
    return render(response, "main/home.html",
                  {"list_count": list_count, "item_count": item_count})


def create(response):
    if response.method == "POST":
        form = CreateNewList(response.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            to_do_list = ToDoList(name=name)
            to_do_list.save()
            response.user.todolist.add(to_do_list)

        return HttpResponseRedirect("/%i" % to_do_list.id)
    else:
        form = CreateNewList()

    return render(response, "main/create.html", {"form": form})


def view(response):
    context_dict = {}
    if response.user.is_authenticated:
        if response.method == "POST":
            if response.POST.get('id_to_delete'):
                ToDoList.objects.get(
                    id=response.POST.get('id_to_delete')).delete()

        for list in response.user.todolist.all():
            done = 0
            total = 0
            for item in list.item_set.all():
                total += 1
                if item.complete:
                    done += 1
            context_dict[list] = str(done) + '/' + str(total)

    return render(response, "main/view.html", {"context_dict": context_dict})
