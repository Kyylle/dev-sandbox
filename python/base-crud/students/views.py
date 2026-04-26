from django.shortcuts import render, redirect
from django.contrib import messages
from .db import (
    sp_student_get_all,
    sp_student_get_by_id,
    sp_student_create,
    sp_student_update,
    sp_student_delete,
)

def student_list(request):
    try:
        students = sp_student_get_all()
    except Exception as e:
        messages.error(request, str(e))
        students = []
    return render(request, 'students/list.html', {'students': students})

def student_detail(request, id):
    try:
        student = sp_student_get_by_id(id)
        if not student:
            messages.error(request, 'Student not found.')
            return redirect('student_list')
    except Exception as e:
        messages.error(request, str(e))
        return redirect('student_list')
    return render(request, 'students/detail.html', {'student': student})

def student_create(request):
    if request.method == 'POST':
        try:
            sp_student_create(
                request.POST['student_id'],
                request.POST['first_name'],
                request.POST['last_name'],
                request.POST['date_of_birth'],
                request.POST['gender'],
                request.POST['address'],
                request.POST['contact_number'],
            )
            messages.success(request, 'Student created successfully!')
            return redirect('student_list')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'students/form.html', {'action': 'Create'})

def student_update(request, id):
    try:
        student = sp_student_get_by_id(id)
        if not student:
            messages.error(request, 'Student not found.')
            return redirect('student_list')
    except Exception as e:
        messages.error(request, str(e))
        return redirect('student_list')

    if request.method == 'POST':
        try:
            sp_student_update(
                id,
                request.POST['student_id'],
                request.POST['first_name'],
                request.POST['last_name'],
                request.POST['date_of_birth'],
                request.POST['gender'],
                request.POST['address'],
                request.POST['contact_number'],
            )
            messages.success(request, 'Student updated successfully!')
            return redirect('student_list')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'students/form.html', {'action': 'Update', 'student': student})

def student_delete(request, id):
    try:
        student = sp_student_get_by_id(id)
        if not student:
            messages.error(request, 'Student not found.')
            return redirect('student_list')
    except Exception as e:
        messages.error(request, str(e))
        return redirect('student_list')

    if request.method == 'POST':
        try:
            sp_student_delete(id)
            messages.success(request, 'Student deleted successfully!')
            return redirect('student_list')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'students/confirm_delete.html', {'student': student})