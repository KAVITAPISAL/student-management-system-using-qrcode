from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import AbstractUser




class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)


class Session(models.Model):
    start_year = models.DateField()
    end_year = models.DateField()

    def __str__(self):
        return "From " + str(self.start_year) + " to " + str(self.end_year)
    


class CustomUser(AbstractUser):
    USER_TYPE = ((1, "HOD"), (2, "Staff"), (3, "Student"),(4, "Librarian"))
    GENDER = [("M", "Male"), ("F", "Female")] 
    mobile_no= models.CharField(max_length=15,unique=True,null=True,blank=True) 
    username = models.CharField(max_length=250,blank=True,null=True )  # Removed username, using email instead
    email = models.EmailField(unique=True)
    user_type = models.CharField(default=1, choices=USER_TYPE, max_length=1)
    gender = models.CharField(max_length=1, choices=GENDER)
    profile_pic = models.ImageField()
    address = models.TextField()
    fcm_token = models.TextField(default="")  # For firebase notifications
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Admin(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

class Course(models.Model):
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Student(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name="admin_name")
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=False)
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True)
    student_id=models.CharField(max_length=120,null=True, blank=False)

    def __str__(self):
        return self.admin.email


class Staff(models.Model):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=False)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.admin.last_name + " " + self.admin.first_name

class Librarian(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name="librarian_name")

    def __str__(self):
        return self.admin.email


class Subject(models.Model):
    name = models.CharField(max_length=120)
    staff = models.ForeignKey(Staff,on_delete=models.CASCADE,)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Attendance(models.Model):
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING)
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AttendanceReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StudentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    test = models.FloatField(default=0)
    exam = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:
            Admin.objects.create(admin=instance)
        if instance.user_type == 2:
            Staff.objects.create(admin=instance)
        if instance.user_type == 3:
            Student.objects.create(admin=instance)
        if instance.user_type == 4:
            Librarian.objects.create(admin=instance)    



@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    print(sender,instance)
    if instance.user_type == 1:
        Admin.objects.get_or_create(admin=instance)
    if instance.user_type == 2:
        Staff.objects.get_or_create(admin=instance)
    if instance.user_type == 3:
        Student.objects.get_or_create(admin=instance)
    if instance.user_type == 4:
        Librarian.objects.get_or_create(admin=instance)



class StudentDocuments(models.Model):
    choice=(
        ("birth certficate","birth certficate"),
        ("SSC certficate","SSC certficate"),
        ("HSC certficate","HSC certficate"),
        ("cast certficate","cast certficate"),
        ("income certficate","income certficate"),
        ("cast validity","cast validity"),
    )
    student=models.ForeignKey(Student, on_delete=models.CASCADE)
    document_name=models.CharField(choices=choice,max_length=50)
    document_pdf=models.FileField(upload_to='student_documents/')
    
    # verified=models.BooleanField(default=False)
    # response=models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return self.student.student_id

    
class Fine(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE)
    amount=models.DecimalField(default=0.00,max_digits=10,decimal_places=2)
    paid=models.BooleanField(default=False)
    order_id = models.CharField(unique=True, max_length=500, null=True, blank=True, default=None) 
    datetime_of_payment = models.DateTimeField(auto_now=False,null=True,blank=True)
    
    # related to razorpay
    razorpay_order_id = models.CharField(max_length=500, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=500, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=500, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id is None :
            self.order_id = "{}_{}_{}".format(self.student.department,self.student.student_id.username,timezone.now().strftime('%H%M%S') )  
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{} payment->{}".format(self.student,self.amount)

class ContactUs(models.Model):
    name=models.CharField(max_length=30)
    email=models.CharField(max_length=30)
    subject=models.CharField(max_length=30)
    message=models.CharField(max_length=500)

    def __str__(self):
        return "{} {}".format(self.name,self.email)