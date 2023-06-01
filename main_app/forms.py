from django import forms
from django.forms.widgets import DateInput, TextInput

from .models import *
import re
from django.core.validators import validate_email

class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # Here make some changes such as:
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


class PasswordField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = forms.PasswordInput()

    def validate(self, value):
        super().validate(value)

        # Perform custom password validation here
        # Example validation rules: password length and complexity
        min_length = 8
        if len(value) < min_length:
            raise forms.ValidationError(f"Password must be at least {min_length} characters long.")

        # Add your additional password complexity rules here
        # Example: at least one uppercase, one lowercase, and one digit
        if not any(c.isupper() for c in value):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not any(c.islower() for c in value):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in value):
            raise forms.ValidationError("Password must contain at least one digit.")


class CustomUserForm(FormSettings):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    password = PasswordField()
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')])
    
    profile_pic = forms.ImageField()
    address = forms.CharField(widget=forms.Textarea)
   
    mobile_no=forms.CharField(required=True)
    widget = {
        'password': forms.PasswordInput(),
    }

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)

        if kwargs.get('instance'):
            instance = kwargs.get('instance').admin.__dict__
            self.fields['password'].required = False
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"

    def clean_mobile_no(self, *args, **kwargs):
        
        pattern = r'^\+?\d{1,4}?\s?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'
        mobile_no = self.cleaned_data.get('mobile_no')
        if CustomUser.objects.filter(mobile_no=mobile_no).exists():
            raise forms.ValidationError("Phone no. exists")
        elif not re.match(pattern, mobile_no):
            raise forms.ValidationError("Invalid mobile number.")
        return mobile_no
    
    def clean_email(self, *args, **kwargs):
        formEmail = self.cleaned_data['email'].lower()
        try:
            validate_email(formEmail)
        except forms.ValidationError:
            raise forms.ValidationError("Invalid email address.")    
        if self.instance.pk is None:  # Insert
            if CustomUser.objects.filter(email=formEmail).exists():
                raise forms.ValidationError(
                    "The given email is already registered")
        
        else:  # Update
            dbEmail = self.Meta.model.objects.get(
                id=self.instance.pk).admin.email.lower()
            if dbEmail != formEmail:  # There has been changes
                if CustomUser.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError("The given email is already registered")

        return formEmail

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email',  'password','gender','profile_pic', 'address','mobile_no' ]


class StudentForm(CustomUserForm):
    student_id = forms.CharField(max_length=250, label="Student ID")
    
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields + \
            ['course', 'session','student_id']

    def clean_student_id(self):
        student_id = self.cleaned_data['student_id']
        
        if Student.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError(f"{student_id} already exists.")
        return student_id
class AdminForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Admin
        fields = CustomUserForm.Meta.fields


class StaffForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields + \
            ['course']

class LibrarianForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(LibrarianForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Librarian
        fields = CustomUserForm.Meta.fields 
        
class CourseForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['name']
        model = Course


class SubjectForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Subject
        fields = ['name', 'staff', 'course']


class SessionForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(SessionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Session
        fields = '__all__'
        widgets = {
            'start_year': DateInput(attrs={'type': 'date'}),
            'end_year': DateInput(attrs={'type': 'date'}),
        }


class LeaveReportStaffForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStaff
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStaffForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStaff
        fields = ['feedback']


class LeaveReportStudentForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStudent
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStudentForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStudent
        fields = ['feedback']


class StudentEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields + \
            ['course', 'session','student_id']


class StaffEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields


class EditResultForm(FormSettings):
    session_list = Session.objects.all()
    session_year = forms.ModelChoiceField(
        label="Session Year", queryset=session_list, required=True)

    def __init__(self, *args, **kwargs):
        super(EditResultForm, self).__init__(*args, **kwargs)

    class Meta:
        model = StudentResult
        fields = ['session_year', 'subject', 'student', 'test', 'exam']


class StudentDocumentForm(forms.ModelForm):
    document_pdf = forms.FileField()
    def __init__(self, *args, **kwargs):
        super(StudentDocumentForm, self).__init__(*args, **kwargs)

     

    def clean_document_pdf(self):
        document_pdf = self.cleaned_data.get('document_pdf')
        
        if document_pdf:
            # Perform your validation logic here
            # For example, check the file size or file extension
            if document_pdf.size > 500 * 1024 * 1024:  # 10 MB
                raise forms.ValidationError("File size should be less than 50 MB.")
            
            valid_extensions = ['.pdf']
            if not any(document_pdf.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError("Only PDF files are allowed.")

        return document_pdf  
    class Meta:
        model = StudentDocuments
        fields = ["document_name","document_pdf"]    


class ContactUsForm(forms.ModelForm) :

    def __init__(self, *args, **kwargs):
        super(ContactUsForm, self).__init__(*args, **kwargs)
    class Meta:
        model = ContactUs
        fields = "__all__"


class AddNewPaymentForm(forms.ModelForm):
    # student_choices = [(student.student_id, student.student_id) for student in Student.objects.all()]
    # student =forms.ChoiceField(choices =student_choices)

    select=(
        (" "," "),
        ("1","Collage Fee"),
        ("2","Semester Exam Fee"),
        
        )
    sem=(
        (" "," "),
        ("1","1"),
        ("2","2"),
        ("3","3"),
        ("4","4"),
        ("5","5"),
        ("6","6"),
        
        )
    name =forms.ChoiceField(choices =select)
    fee_type=forms.ChoiceField(choices =sem,label="Semester")

    def __init__(self, *args, **kwargs):
        super(AddNewPaymentForm, self).__init__(*args, **kwargs)

        self.fields['student'] = forms.ChoiceField(choices=self.get_student_choices())

    def get_student_choices(self):
        student_choices = [(student.student_id, student.student_id) for student in Student.objects.all()]
        return student_choices
    class Meta:
        model = Fee
        fields = ['name','fee_type','student', 'amount'] 

    
    def clean_student(self):
        student = self.cleaned_data['student']
        std=Student.objects.get(student_id=student)
        print(std.id)
        return std 
     
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <=0:
            raise forms.ValidationError("Enter Amount ")


        return amount  
        
