import os
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from . import db_helper

def custom_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'id' not in request.session:
            messages.warning(request, "Log in to access the control panel.")
            return redirect('homepage')
        request.custom_user = db_helper.get_user_by_id(request.session['id'])
        if not request.custom_user:
            return redirect('logout')
        return view_func(request, *args, **kwargs)
    return wrapper

def homepage(request):
    if 'id' in request.session:
        return redirect('dashboard')
    return render(request, 'homepage.html')

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        user = db_helper.authenticate_user(u, p)
        if user:
            request.session['id'] = user['id']
            request.session['username'] = user['username']
            request.session['is_admin'] = bool(user['is_admin'])
            return JsonResponse({'success': True, 'redirect_url': reverse('dashboard')})
        else:
           return JsonResponse({
                'success': False, 
                'error_message': "Invalid username or password configuration."
            }, status=401)
    return redirect('homepage')

def logout_view(request):
    request.session.flush()
    return redirect('homepage')

@custom_login_required
def dashboard(request):
    user = request.custom_user
    is_admin = bool(user['is_admin'])
    
    # Extract access rules
    user_dept_id = user.get('department_id')
    can_cross_access = bool(user.get('can_access_other_depts'))
    all_system_folders = db_helper.get_all_folders_with_users()
    
    if is_admin:
        folders = all_system_folders
    else:
        permitted_folder_ids = db_helper.get_user_permitted_folders_list(user['id'])
        folders = []
        for folder in all_system_folders:
            is_owner = (int(folder['user_id']) == int(user['id']))
            is_explicitly_permitted = (folder['id'] in permitted_folder_ids)
            
            folder_owner_profile = db_helper.get_user_by_id(folder['user_id'])
            folder_owner_dept = folder_owner_profile.get('department_id') if folder_owner_profile else None
            is_same_department = (user_dept_id is not None and folder_owner_dept == user_dept_id)

            if is_owner or is_explicitly_permitted or is_same_department or can_cross_access:
                folders.append(folder)

    departments_list = db_helper.get_all_departments()
    dept_map = {d['id']: d['name'] for d in departments_list}

    for folder in folders:
        owner_profile = db_helper.get_user_by_id(folder['user_id'])
        dept_id = owner_profile.get('department_id') if owner_profile else None
        folder['department_name'] = dept_map.get(dept_id, 'Unassigned')

    folders.sort(key=lambda x: x.get('department_name', 'Unassigned'))

    # 1. Identify which tab/view should load in the central pane
    active_view = request.GET.get('view', 'home')
    selected_folder_id = request.GET.get('folder_id')

    # If a folder was selected, default active_view to automations content
    if selected_folder_id:
        active_view = 'automations'

    # Base context
    context = {
        'folders': folders,
        'is_admin': is_admin,
        'active_view': active_view,
    }

    # 2. If User Management is active, load admin database parameters
    if active_view == 'user_management' and is_admin:
        search_query = request.GET.get('search', '')
        users_list = db_helper.search_and_get_users(search_query)
        departments = db_helper.get_all_departments()
        
        for u in users_list:
            u['permitted_folders'] = db_helper.get_user_permitted_folders_list(u['id'])
            
        context.update({
            'users_list': users_list,
            'departments': departments,
            'all_system_folders': all_system_folders,
            'search_query': search_query,
        })

    # 3. Handle automation directories if loaded
    selected_folder = None
    automations = {}
    path_error = None

    if selected_folder_id:
        selected_folder = db_helper.get_folder_by_id(selected_folder_id)
        if selected_folder and not is_admin:
            has_view_rights = any(int(f['id']) == int(selected_folder_id) for f in folders)
            if not has_view_rights:
                selected_folder = None

    if selected_folder:
        phys_path = selected_folder['physical_path']
        if os.path.exists(phys_path) and os.path.isdir(phys_path):
            try:
                files = os.listdir(phys_path)
                pattern = re.compile(r"^(.+?)\.((?:\d+\.)*\d+.*?)\.nupkg$", re.IGNORECASE)
                
                raw_automations = {}
                for f in files:
                    match = pattern.match(f)
                    if match:
                        package_name, version = match.groups()
                        if package_name not in raw_automations:
                            raw_automations[package_name] = []
                        raw_automations[package_name].append(version)
                
                active_version = db_helper.get_active_versions_for_folder(selected_folder['id'])
                
                for pkg_name, versions in raw_automations.items():
                    sorted_versions = sorted(versions, reverse=True)
                    active = active_version if (active_version in sorted_versions) else (sorted_versions[0] if sorted_versions else "N/A")
                    
                    automations[pkg_name] = {
                        'versions': sorted_versions,
                        'active': active
                    }
            except Exception as e:
                path_error = f"Failed to list directory contents: {str(e)}"
        else:
            path_error = f"Directory not accessible or path invalid: '{phys_path}'"

    context.update({
        'selected_folder': selected_folder,
        'automations': automations,
        'path_error': path_error,
    })
    
    return render(request, 'dashboard.html', context)


# --- REPLICA CENTRALIZED USER MANAGEMENT VIEWS ---

@custom_login_required
def admin_user_management(request):
    if not bool(request.custom_user['is_admin']):
        messages.error(request, "Access Denied: Administrative Clearance Required.")
        return redirect('dashboard')

    search_query = request.GET.get('search', '')
    users_list = db_helper.search_and_get_users(search_query)
    departments = db_helper.get_all_departments()
    all_system_folders = db_helper.get_all_folders_with_users()

    # Match up multi-select parameters directly on runtime runtime elements
    for u in users_list:
        u['permitted_folders'] = db_helper.get_user_permitted_folders_list(u['id'])

    context = {
        'users_list': users_list,
        'departments': departments,
        'all_system_folders': all_system_folders,
        'search_query': search_query,
        'is_admin': True,
        'folders': all_system_folders, 
    }
    return render(request, 'adminpage/admin_user_management.html', context)

@custom_login_required
def admin_save_user(request, user_id=None):
    if not bool(request.custom_user['is_admin']):
        messages.error(request, "Access Denied: Action Rejected.")
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        dept_id = request.POST.get('department_id')
        can_access_other_depts = 1 if request.POST.get('can_access_other_depts') == 'on' else 0
        is_admin_flag = 1 if request.POST.get('is_admin') == 'on' else 0
        selected_folders = request.POST.getlist('accessible_folders')

        dept_id = int(dept_id) if dept_id and dept_id.isdigit() else None

        try:
            db_helper.admin_save_orchestrator_user_profile(
                user_id=user_id,
                username=username,
                password=password,
                is_admin=is_admin_flag,
                department_id=dept_id,
                can_access_other_depts=can_access_other_depts,
                allowed_folder_ids=selected_folders
            )
            messages.success(request, f"Permissions map updated for '{username}'.")
        except Exception as e:
            messages.error(request, f"Database operational failure: {str(e)}")

    return redirect('admin_user_management')

# --- PRESERVED ENVIRONMENT CONTROL METHODS ---

@custom_login_required
def create_folder(request):
    if request.method == 'POST':
        if request.custom_user['is_admin']:
            messages.error(request, "Global workspace configurations are modified only by local owners.")
            return redirect('dashboard')
            
        name = request.POST.get('name')
        physical_path = request.POST.get('physical_path')
        if name and physical_path:
            db_helper.create_project_folder(request.custom_user['id'], name, physical_path)
            messages.success(request, f"Registered Package environment '{name}'.")
        else:
            messages.error(request, "Fields cannot be blank.")
    return redirect('dashboard')

@custom_login_required
def edit_folder(request, folder_id):
    if request.method == 'POST':
        if request.custom_user['is_admin']:
            messages.error(request, "Global configurations cannot be edited in admin mode.")
            return redirect('dashboard')

        folder = db_helper.get_folder_by_id(folder_id)
        if not folder or folder['id'] != request.custom_user['id']:
            messages.error(request, "Folder modification rejected.")
            return redirect('dashboard')

        name = request.POST.get('name')
        physical_path = request.POST.get('physical_path')
        if name and physical_path:
            db_helper.update_project_folder(folder_id, name, physical_path)
            messages.success(request, f"Configuration changes saved.")
        else:
            messages.error(request, "Changes must contain values.")
    return redirect(f"{reverse('dashboard')}?folder_id={folder_id}")

@custom_login_required
def select_version(request):
    # Exit early if a user attempts a GET request or is a global admin account 
    if request.method != 'POST' or request.custom_user['is_admin']:
        messages.error(request, "Invalid method or insufficient permissions.")
        return redirect('dashboard')

    folder_id = request.POST.get('folder_id')
    package_name = request.POST.get('package_name')
    version = request.POST.get('version')

    folder = db_helper.get_folder_by_id(folder_id)
    if not folder or folder['id'] != request.custom_user['id']:
        messages.error(request, "Change version command invalid.")
        return redirect('dashboard')

    # 👇 Clean workflow structure execution logic layer
    db_helper.set_active_version(folder_id, package_name, version, request.custom_user['id'])
    messages.success(request, f"Deployed active package version {version} for '{package_name}'.")
    return redirect(f"{reverse('dashboard')}?folder_id={folder_id}")