from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.db.models import Count, Sum
from .models import ToDoList
from .forms import CreateNewList


# Create your views here.

def index(request, id):
    ls = get_object_or_404(ToDoList, id=id)

    if ls in request.user.todolist.all():
        if request.method == "POST":

            if request.POST.get("save"):
                for item in ls.item_set.all():
                    if request.POST.get("c" + str(item.id)):
                        item.complete = True
                    else:
                        item.complete = False

                    item.save()

            elif request.POST.get("newItem"):
                txt = request.POST.get("new")

                if len(txt) > 2:
                    ls.item_set.create(text=txt, complete=False)
                else:
                    print("Invalid input")
        return render(request, "main/list.html", {"ls": ls})
    else:
        return render(request, "main/view.html", {})


def home(request):
    if not request.user.is_authenticated:
        data = {'list_count': 0, 'item_count': 0}
        return render(request, "main/home.html", data)
    data = (
        request.user.todolist
            .annotate(items=Count('item'))
            .aggregate(
            list_count=Count('pk'),
            item_count=Sum('items')
        )
    )
    return render(request, "main/home.html", data)


def create(request):
    if request.method == "POST":
        form = CreateNewList(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            to_do_list = ToDoList(name=name)
            to_do_list.save()
            request.user.todolist.add(to_do_list)

        return HttpResponseRedirect("/%i" % to_do_list.id)
    else:
        form = CreateNewList()

    return render(request, "main/create.html", {"form": form})


def view(request):
    context_dict = {}
    if request.user.is_authenticated:
        if request.method == "POST":
            if request.POST.get('id_to_delete'):
                ToDoList.objects.get(
                    id=request.POST.get('id_to_delete')).delete()

        for list in request.user.todolist.all():
            done = 0
            total = 0
            for item in list.item_set.all():
                total += 1
                if item.complete:
                    done += 1
            context_dict[list] = str(done) + '/' + str(total)

    return render(request, "main/view.html", {"context_dict": context_dict})
