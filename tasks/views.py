from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm as ucf, AuthenticationForm 
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError as int_er
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': ucf
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request,user)
                return redirect('tasks')
            except int_er:
                return render(request, 'signup.html', {
                    'form': ucf,
                    'error': 'El usuario ya existe'
                })

        else:
            return render(request, 'signup.html', {
                'form': ucf,
                'error': 'Las contraseñas no coinciden.'
            })


def home(request):
    return render(request, 'home.html')

@login_required
def tasks(request):
    # tasks=Task.objects.all().order_by('-created') Para ver todas las tareas
    tasks=Task.objects.filter(user=request.user, datecompleted__isnull=True).order_by('-created') #para ver las tareas asignadas al usuario que inició sesión, y que aún no están completadas.
    return render(request,'tasks.html', {
        'tasks':tasks
    })

@login_required
def tasks_complete(request):
    # tasks=Task.objects.all().order_by('-created') Para ver todas las tareas
    tasks=Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-created') #para ver las tareas asignadas al usuario que inició sesión, y que aún no están completadas.
    return render(request,'tasks_complete.html', {
        'tasks':tasks
    })

@login_required
def task_detail(request,task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task,pk=task_id,user=request.user)
        form = TaskForm(instance=task)
        return render(request,'task_detail.html', {
            'task':task, 
            'form':form
        })
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request,'task_detail.html', {
                'task':task,
                'form':form,
                'error':'Error'
            })

@login_required
def complete_task(request, task_id):
    task=get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')
    
@login_required
def delete_task(request, task_id):
    task=get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')


@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
            return render(request,'signin.html',{
            'form': AuthenticationForm
        })
    else:
        user =  authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        
        if user is None:
            return render(request,'signin.html',{
                'form': AuthenticationForm,
                'error':'El usuario no existe, o la contraseña es incorrecta.'
            })

        else:
            login(request, user)
            return redirect('tasks')

@login_required
def create_task(request):
    if request.method == 'GET':
        return render (request, 'create_task.html', {
            'form':TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render (request, 'create_task.html', {
                'form':TaskForm,
                'error': 'Es obligatorio llenar todos los campos.'
            })




