from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import CustomUser, Membership, Review
from django.contrib.auth import get_user_model


# User Creation Form
class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.USER_ROLES, widget=forms.Select(attrs={"class": "form-select"}))
    first_name = forms.CharField(max_length=150, required=True,
                                  widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(max_length=150, required=True,
                                widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user

# User Authentication Form
class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = get_user_model()

# User Edit Form (Admin)
class UserEditForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=CustomUser.USER_ROLES,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

# Add User Form (Admins)
class AddUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), required=True)
    role = forms.ChoiceField(choices=CustomUser.USER_ROLES, widget=forms.Select(attrs={"class": "form-select"}))

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'role', 'password']

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.set_password(self.cleaned_data['password'])
            user.save()
        return user

class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ["user", "membership_type", "auto_renew"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = CustomUser.objects.all()  # Show all users
        self.fields['membership_type'].widget = forms.RadioSelect(choices=Membership.TIER_CHOICES)
        self.fields['auto_renew'].widget = forms.CheckboxInput()

    def clean_membership_type(self):
        membership_type = self.cleaned_data.get('membership_type')
        if membership_type not in dict(Membership.TIER_CHOICES):
            raise forms.ValidationError("Invalid membership type selected.")
        return membership_type

class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']  # Removed role field

    password_change_form = PasswordChangeForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.password_form = self.password_change_form(user=self.instance)

    def clean(self):
        cleaned_data = super().clean()
        if self.password_form.cleaned_data.get('new_password1'):
            if not self.password_form.is_valid():
                raise forms.ValidationError(self.password_form.errors)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.password_form.cleaned_data.get('new_password1'):
            user.set_password(self.password_form.cleaned_data['new_password2'])
        if commit:
            user.save()
        return user
    
# For Users
class UserMembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ["membership_type", "auto_renew"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['membership_type'].widget = forms.Select(choices=Membership.TIER_CHOICES)
        self.fields['auto_renew'].widget = forms.CheckboxInput()

    def clean_membership_type(self):
        membership_type = self.cleaned_data.get('membership_type')
        if membership_type not in dict(Membership.TIER_CHOICES):
            raise forms.ValidationError("Invalid membership type selected.")
        return membership_type
    
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['review_text']
        widgets = {
            'review_text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Your review...'}),
        }