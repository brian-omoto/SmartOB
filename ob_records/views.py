from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from datetime import datetime
import psycopg2
import time
import csv

from .models import OBRecord, QueryLog, AuditLog, User
from .nlp_utils import extract_entities
from sentence_transformers import SentenceTransformer


# LOAD MODEL (CACHED)
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except:
    model = None


# AUTHENTICATION

def login_view(request):
    """Login page with role selection (Officer/Admin)"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        selected_role = request.POST.get('role', 'officer')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Verify role matches selected role
            if user.role != selected_role:
                return render(request, 'login.html', {
                    'error': f'This account is not registered as a {selected_role}. Please select the correct role.'
                })
            
            login(request, user)
            AuditLog.objects.create(
                user=user,
                action_type='LOGIN',
                affected_table='users',
                affected_record_id=user.id,
                action_details=f'{user.username} logged in as {user.role}'
            )
            
            if user.role == 'admin':
                return HttpResponseRedirect(reverse('admin_dashboard'))
            else:
                return HttpResponseRedirect(reverse('search'))
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    
    return render(request, 'login.html')

def logout_view(request):
    """Logout and redirect to login page"""
    user = request.user
    if user.is_authenticated:
        AuditLog.objects.create(
            user=user,
            action_type='LOGOUT',
            affected_table='users',
            affected_record_id=user.id,
            action_details=f'{user.username} logged out'
        )
    logout(request)
    return redirect('login')


# OFFICER SEARCH (WITH spaCy NLP + pgvector)

@login_required
def search(request):
    """Officer search page with natural language processing"""
    query = request.GET.get('q', '')
    results = []
    entities = None
    search_time = None
    query_logs = []
    recent_views = []
    total_searches = 0
    last_search_time = None

    if query:
        start_time = time.time()
        
        # Step 1: Extract entities using spaCy NLP
        entities = extract_entities(query)
        print(f"[NLP] Extracted entities: {entities}")
        
        # Step 2: Convert query to embedding for semantic search
        query_embedding = model.encode(query).tolist() if model else None
        
        # Step 3: Search using pgvector (semantic) or fallback to text search
        try:
            conn = psycopg2.connect(
                dbname="smartob_db",
                user="postgres",
                password="5434",  
                host="localhost",
                port=5432
            )
            cur = conn.cursor()
            
            if query_embedding:
                # Semantic search with pgvector
                cur.execute("""
                    SELECT ob_id, ob_number, date_reported, case_type, location, 
                           complainant_name, suspect_names, case_summary,
                           1 - (embedding <=> %s::vector) AS similarity
                    FROM ob_records
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> %s::vector
                    LIMIT 10
                """, (query_embedding, query_embedding))
            else:
                # Fallback to text search
                cur.execute("""
                    SELECT ob_id, ob_number, date_reported, case_type, location, 
                           complainant_name, suspect_names, case_summary,
                           0.5 AS similarity
                    FROM ob_records
                    WHERE case_summary ILIKE %s OR location ILIKE %s OR case_type ILIKE %s
                    LIMIT 10
                """, (f'%{query}%', f'%{query}%', f'%{query}%'))
            
            results = cur.fetchall()
            cur.close()
            conn.close()
            
            # Log the query
            QueryLog.objects.create(
                user=request.user,
                query_text=query,
                result_count=len(results)
            )
            
            search_time = round((time.time() - start_time) * 1000, 2)
            print(f"[NLP] Search completed in {search_time}ms, found {len(results)} results")
            
        except Exception as e:
            print(f"[ERROR] Database connection failed: {e}")
            results = []

    # Fetch user's query logs (last 10)
    query_logs = QueryLog.objects.filter(user=request.user).order_by('-timestamp')[:10]
    
    # Fetch recent views from session
    recent_ids = request.session.get('recent_views', [])
    if recent_ids:
        recent_views = OBRecord.objects.filter(ob_id__in=recent_ids).values_list(
            'ob_id', 'ob_number', 'date_reported', 'case_type'
        )[:5]
    
    # Fetch quick stats
    total_records = OBRecord.objects.count()
    total_searches = QueryLog.objects.filter(
        user=request.user,
        timestamp__date=datetime.now().date()
    ).count()
    
    last_log = QueryLog.objects.filter(user=request.user).order_by('-timestamp').first()
    last_search_time = last_log.timestamp.strftime('%H:%M') if last_log else None

    return render(request, 'search.html', {
        'query': query,
        'results': results,
        'entities': entities,
        'search_time': search_time,
        'query_logs': query_logs,
        'recent_views': recent_views,
        'total_records': total_records,
        'total_searches': total_searches,
        'last_search_time': last_search_time,
    })

# RECORD DETAIL (WITH RECENT VIEWS TRACKING)

@login_required
def record_detail(request, ob_id):
    """Full record details page with recent views tracking"""
    try:
        conn = psycopg2.connect(
            dbname="smartob_db",
            user="postgres",
            password="5434",  
            host="localhost",
            port=5432
        )
        cur = conn.cursor()
        
        cur.execute("""
            SELECT ob_id, ob_number, date_reported, case_type, location,
                   complainant_name, suspect_names, case_summary,
                   investigating_officer, created_at, updated_at
            FROM ob_records
            WHERE ob_id = %s
        """, (ob_id,))
        
        record = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        record = None
    
    if not record:
        return render(request, '404.html', {'message': 'Record not found'})
    
    # Track recent views in session
    recent_views = request.session.get('recent_views', [])
    if ob_id in recent_views:
        recent_views.remove(ob_id)
    recent_views.insert(0, ob_id)
    request.session['recent_views'] = recent_views[:10]
    
    return render(request, 'detail.html', {'record': record})


# ADMIN DASHBOARD

@login_required
def admin_dashboard(request):
    """Admin dashboard with system stats and audit logs"""
    if request.user.role != 'admin':
        return redirect('search')
    
    # Get audit logs using Django ORM
    logs = AuditLog.objects.all().order_by('-timestamp')[:50]
    
    # Get system stats
    total_records = OBRecord.objects.count()
    active_officers = User.objects.filter(role='officer').count()
    total_logs = AuditLog.objects.count()
    
    return render(request, 'admin_dashboard.html', {
        'logs': logs,
        'total_records': total_records,
        'active_officers': active_officers,
        'total_logs': total_logs,
    })

# CSV EXPORT (ADMIN ONLY)

@login_required
def export_csv(request):
    """Export all OB records as CSV (Admin only)"""
    if request.user.role != 'admin':
        return redirect('search')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ob_records_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'OB Number', 'Date Reported', 'Case Type', 'Location',
        'Complainant', 'Suspect(s)', 'Case Summary', 'Investigating Officer'
    ])
    
    records = OBRecord.objects.all().values_list(
        'ob_number', 'date_reported', 'case_type', 'location',
        'complainant_name', 'suspect_names', 'case_summary', 'investigating_officer'
    )
    
    for record in records:
        writer.writerow(record)
    
    AuditLog.objects.create(
        user=request.user,
        action_type='EXPORT',
        affected_table='ob_records',
        action_details=f'Exported {records.count()} OB records to CSV'
    )
    
    return response

# CRUD OPERATIONS (ADMIN ONLY)

@login_required
def create_record(request):
    """Create a new OB record (Admin only)"""
    if request.user.role != 'admin':
        return redirect('search')
    
    if request.method == 'POST':
        ob_number = request.POST.get('ob_number')
        date_reported = request.POST.get('date_reported')
        case_type = request.POST.get('case_type')
        location = request.POST.get('location')
        complainant_name = request.POST.get('complainant_name')
        suspect_names = request.POST.get('suspect_names')
        case_summary = request.POST.get('case_summary')
        investigating_officer = request.POST.get('investigating_officer')
        
        # Validate required fields
        if not all([ob_number, date_reported, case_type, location, case_summary]):
            return render(request, 'admin_create.html', {
                'error': 'Please fill in all required fields.',
                'form_data': request.POST
            })
        
        try:
            conn = psycopg2.connect(
                dbname="smartob_db",
                user="postgres",
                password="5434",  
                host="localhost",
                port=5432
            )
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO ob_records 
                (ob_number, date_reported, case_type, location, complainant_name, 
                 suspect_names, case_summary, investigating_officer, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING ob_id
            """, (ob_number, date_reported, case_type, location, complainant_name,
                  suspect_names, case_summary, investigating_officer))
            
            ob_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            
            AuditLog.objects.create(
                user=request.user,
                action_type='INSERT',
                affected_table='ob_records',
                affected_record_id=ob_id,
                action_details=f'Created OB record {ob_number}'
            )
            
            return redirect('admin_dashboard')
            
        except Exception as e:
            return render(request, 'admin_create.html', {
                'error': f'Error creating record: {str(e)}',
                'form_data': request.POST
            })
    
    return render(request, 'admin_create.html')

@login_required
def edit_record(request, ob_id):
    """Edit an existing OB record (Admin only)"""
    if request.user.role != 'admin':
        return redirect('search')
    
    # Fetch the record
    try:
        conn = psycopg2.connect(
            dbname="smartob_db",
            user="postgres",
            password="5434",  
            host="localhost",
            port=5432
        )
        cur = conn.cursor()
        
        cur.execute("""
            SELECT ob_id, ob_number, date_reported, case_type, location,
                   complainant_name, suspect_names, case_summary, investigating_officer
            FROM ob_records
            WHERE ob_id = %s
        """, (ob_id,))
        
        record = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        record = None
    
    if not record:
        return render(request, '404.html', {'message': 'Record not found'})
    
    if request.method == 'POST':
        ob_number = request.POST.get('ob_number')
        date_reported = request.POST.get('date_reported')
        case_type = request.POST.get('case_type')
        location = request.POST.get('location')
        complainant_name = request.POST.get('complainant_name')
        suspect_names = request.POST.get('suspect_names')
        case_summary = request.POST.get('case_summary')
        investigating_officer = request.POST.get('investigating_officer')
        
        if not all([ob_number, date_reported, case_type, location, case_summary]):
            return render(request, 'admin_edit.html', {
                'error': 'Please fill in all required fields.',
                'record': record,
                'form_data': request.POST
            })
        
        try:
            conn = psycopg2.connect(
                dbname="smartob_db",
                user="postgres",
                password="5434",  
                host="localhost",
                port=5432
            )
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE ob_records
                SET ob_number = %s, date_reported = %s, case_type = %s, location = %s,
                    complainant_name = %s, suspect_names = %s, case_summary = %s,
                    investigating_officer = %s, updated_at = NOW()
                WHERE ob_id = %s
            """, (ob_number, date_reported, case_type, location, complainant_name,
                  suspect_names, case_summary, investigating_officer, ob_id))
            
            conn.commit()
            cur.close()
            conn.close()
            
            AuditLog.objects.create(
                user=request.user,
                action_type='UPDATE',
                affected_table='ob_records',
                affected_record_id=ob_id,
                action_details=f'Updated OB record {ob_number}'
            )
            
            return redirect('admin_dashboard')
            
        except Exception as e:
            return render(request, 'admin_edit.html', {
                'error': f'Error updating record: {str(e)}',
                'record': record,
                'form_data': request.POST
            })
    
    return render(request, 'admin_edit.html', {'record': record})

@login_required
def delete_record(request, ob_id):
    """Delete an OB record (Admin only)"""
    if request.user.role != 'admin':
        return redirect('search')
    
    try:
        conn = psycopg2.connect(
            dbname="smartob_db",
            user="postgres",
            password="5434", 
            host="localhost",
            port=5432
        )
        cur = conn.cursor()
        
        cur.execute("SELECT ob_id, ob_number FROM ob_records WHERE ob_id = %s", (ob_id,))
        record = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        record = None
    
    if not record:
        return render(request, '404.html', {'message': 'Record not found'})
    
    if request.method == 'POST':
        try:
            conn = psycopg2.connect(
                dbname="smartob_db",
                user="postgres",
                password="5434",  
                host="localhost",
                port=5432
            )
            cur = conn.cursor()
            
            cur.execute("DELETE FROM ob_records WHERE ob_id = %s", (ob_id,))
            conn.commit()
            cur.close()
            conn.close()
            
            AuditLog.objects.create(
                user=request.user,
                action_type='DELETE',
                affected_table='ob_records',
                affected_record_id=ob_id,
                action_details=f'Deleted OB record {record[1]}'
            )
            
            return redirect('admin_dashboard')
            
        except Exception as e:
            return render(request, 'admin_confirm_delete.html', {
                'error': f'Error deleting record: {str(e)}',
                'record': record
            })
    
    return render(request, 'admin_confirm_delete.html', {'record': record})


# USER MANAGEMENT (ADMIN ONLY)


@login_required
def user_management(request):
    """List all police officers (Admin only)"""
    if request.user.role != 'admin':
        return redirect('search')
    
    officers = User.objects.filter(role='officer')
    return render(request, 'admin_users.html', {'officers': officers})

@login_required
def create_user(request):
    """Create a new officer account (Admin only)"""
    if request.user.role != 'admin':
        return redirect('search')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        
        if not all([username, password, full_name]):
            return render(request, 'admin_create_user.html', {
                'error': 'Please fill in all required fields.'
            })
        
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                full_name=full_name,
                email=email,
                role='officer'
            )
            
            AuditLog.objects.create(
                user=request.user,
                action_type='INSERT',
                affected_table='users',
                affected_record_id=user.id,
                action_details=f'Created officer account {username}'
            )
            
            return redirect('user_management')
            
        except Exception as e:
            return render(request, 'admin_create_user.html', {
                'error': f'Error creating user: {str(e)}'
            })
    
    return render(request, 'admin_create_user.html')

@login_required
def delete_user(request, user_id):
    """Delete an officer account (Admin only)"""
    if request.user.role != 'admin':
        return redirect('search')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        
        AuditLog.objects.create(
            user=request.user,
            action_type='DELETE',
            affected_table='users',
            affected_record_id=user_id,
            action_details=f'Deleted officer account {username}'
        )
        
        return redirect('user_management')
    
    return render(request, 'admin_confirm_delete_user.html', {'user': user})