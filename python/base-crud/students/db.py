from django.db import connection


# =============================================
# HELPERS
# =============================================
def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def dictfetchone(cursor):
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None


# =============================================
# GET ALL STUDENTS
# =============================================
def sp_student_get_all():
    try:
        with connection.cursor() as cursor:
            cursor.execute("EXEC sp_student_get_all")
            return dictfetchall(cursor)
    except Exception as e:
        raise Exception(f"Failed to fetch students: {str(e)}")


# =============================================
# GET STUDENT BY ID
# =============================================
def sp_student_get_by_id(id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("EXEC sp_student_get_by_id @id = %s", [id])
            return dictfetchone(cursor)
    except Exception as e:
        raise Exception(f"Failed to fetch student: {str(e)}")


# =============================================
# CREATE STUDENT
# =============================================
def sp_student_create(student_id, first_name, last_name,
                      date_of_birth, gender, address, contact_number):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                EXEC sp_student_create
                    @student_id     = %s,
                    @first_name     = %s,
                    @last_name      = %s,
                    @date_of_birth  = %s,
                    @gender         = %s,
                    @address        = %s,
                    @contact_number = %s
            """, [student_id, first_name, last_name,
                  date_of_birth, gender, address, contact_number])
    except Exception as e:
        raise Exception(f"Failed to create student: {str(e)}")


# =============================================
# UPDATE STUDENT
# =============================================
def sp_student_update(id, student_id, first_name, last_name,
                      date_of_birth, gender, address, contact_number):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                EXEC sp_student_update
                    @id             = %s,
                    @student_id     = %s,
                    @first_name     = %s,
                    @last_name      = %s,
                    @date_of_birth  = %s,
                    @gender         = %s,
                    @address        = %s,
                    @contact_number = %s
            """, [id, student_id, first_name, last_name,
                  date_of_birth, gender, address, contact_number])
    except Exception as e:
        raise Exception(f"Failed to update student: {str(e)}")


# =============================================
# DELETE STUDENT
# =============================================
def sp_student_delete(id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("EXEC sp_student_delete @id = %s", [id])
    except Exception as e:
        raise Exception(f"Failed to delete student: {str(e)}")