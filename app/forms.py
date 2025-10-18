from django import forms
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    # honeypot (ukryte pole – boty je wypełnią)
    hp_field = forms.CharField(required=False, widget=forms.HiddenInput())
    
    # GDPR consent checkboxes
    data_processing_consent = forms.BooleanField(
        required=True,
        label='Wyrażam zgodę na przetwarzanie moich danych osobowych w celu udzielenia odpowiedzi na zapytanie zgodnie z Polityką Prywatności.',
        error_messages={'required': 'Zgoda na przetwarzanie danych jest wymagana.'}
    )

    class Meta:
        model = Appointment
        fields = ['name', 'phone', 'email', 'preferred_date', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Imię i nazwisko'}),
            'phone': forms.TextInput(attrs={'placeholder': '+48 xxx xxx xxx'}),
            'email': forms.EmailInput(attrs={'placeholder': 'email@example.com'}),
            'preferred_date': forms.TextInput(attrs={'placeholder': 'np. jutro po 15:00, następny tydzień'}),
            'message': forms.Textarea(attrs={'placeholder': 'Opisz swoje potrzeby...', 'rows': 4}),
        }
        labels = {
            'name': 'Imię i nazwisko *',
            'phone': 'Telefon *',
            'email': 'Email',
            'preferred_date': 'Preferowany termin',
            'message': 'Wiadomość',
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('hp_field'):
            raise forms.ValidationError("Invalid submission.")
        
        # Additional validation for GDPR compliance
        if not cleaned.get('data_processing_consent'):
            raise forms.ValidationError("Zgoda na przetwarzanie danych jest wymagana.")
            
        return cleaned


class DataSubjectRightsForm(forms.Form):
    REQUEST_TYPES = [
        ('access', 'Żądanie dostępu do danych (prawo dostępu)'),
        ('rectification', 'Żądanie sprostowania danych (prawo sprostowania)'),
        ('erasure', 'Żądanie usunięcia danych (prawo do zapomnienia)'),
        ('portability', 'Żądanie przenoszenia danych (prawo do przenoszenia)'),
        ('restriction', 'Żądanie ograniczenia przetwarzania (prawo do ograniczenia)'),
        ('objection', 'Sprzeciw wobec przetwarzania (prawo sprzeciwu)'),
    ]
    
    # honeypot field
    hp_field = forms.CharField(required=False, widget=forms.HiddenInput())
    
    request_type = forms.ChoiceField(
        choices=REQUEST_TYPES,
        required=True,
        label='Rodzaj żądania *',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    full_name = forms.CharField(
        max_length=120,
        required=True,
        label='Imię i nazwisko *',
        widget=forms.TextInput(attrs={'placeholder': 'Podaj swoje pełne imię i nazwisko', 'class': 'form-control'})
    )
    
    email = forms.EmailField(
        required=True,
        label='Adres email *',
        widget=forms.EmailInput(attrs={'placeholder': 'email@example.com', 'class': 'form-control'})
    )
    
    phone = forms.CharField(
        max_length=30,
        required=False,
        label='Telefon',
        widget=forms.TextInput(attrs={'placeholder': '+48 xxx xxx xxx', 'class': 'form-control'})
    )
    
    identification = forms.CharField(
        required=True,
        label='Informacje identyfikacyjne *',
        widget=forms.Textarea(attrs={
            'placeholder': 'Podaj informacje umożliwiające weryfikację Twojej tożsamości (np. data urodzenia, adres, data wizyty, itp.)',
            'rows': 3,
            'class': 'form-control'
        }),
        help_text='Te informacje są wymagane do weryfikacji Twojej tożsamości zgodnie z RODO.'
    )
    
    details = forms.CharField(
        required=False,
        label='Dodatkowe szczegóły',
        widget=forms.Textarea(attrs={
            'placeholder': 'Opisz szczegółowo swoje żądanie...',
            'rows': 4,
            'class': 'form-control'
        })
    )
    
    privacy_consent = forms.BooleanField(
        required=True,
        label='Wyrażam zgodę na przetwarzanie moich danych osobowych w celu realizacji żądania zgodnie z Polityką Prywatności. *',
        error_messages={'required': 'Zgoda na przetwarzanie danych jest wymagana.'}
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('hp_field'):
            raise forms.ValidationError("Invalid submission.")
        
        if not cleaned.get('privacy_consent'):
            raise forms.ValidationError("Zgoda na przetwarzanie danych jest wymagana.")
            
        return cleaned
