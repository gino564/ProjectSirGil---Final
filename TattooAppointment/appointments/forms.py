from django import forms
from .models import Appointment, TattooRequest


class AppointmentForm(forms.ModelForm):
    """Form for creating/booking appointments"""

    class Meta:
        model = Appointment
        fields = ['artist', 'tattoo_request', 'scheduled_date', 'duration_hours', 'notes']
        widgets = {
            'scheduled_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                }
            ),
            'duration_hours': forms.NumberInput(
                attrs={
                    'min': '0.5',
                    'max': '8',
                    'step': '0.5',
                    'class': 'form-control'
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'rows': 4,
                    'class': 'form-control',
                    'placeholder': 'Any special requests or notes for your artist...'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Customize field properties
        self.fields['artist'].help_text = 'Select your preferred artist'
        self.fields['tattoo_request'].help_text = 'Choose an approved design (optional)'
        self.fields['tattoo_request'].required = False
        self.fields['scheduled_date'].help_text = 'Preferred date and time for your session'
        self.fields['duration_hours'].help_text = 'Estimated session duration in hours'
        self.fields['notes'].required = False

        # Filter tattoo requests to only show user's approved requests
        if user:
            self.fields['tattoo_request'].queryset = TattooRequest.objects.filter(
                client=user,
                status='approved'
            )


class TattooRequestForm(forms.ModelForm):
    """Form for submitting new tattoo requests/enquiries"""

    class Meta:
        model = TattooRequest
        fields = ['title', 'description', 'reference_image']
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'e.g., Dragon on Upper Arm'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'rows': 6,
                    'class': 'form-control',
                    'placeholder': 'Describe your tattoo idea in detail:\n- Style (traditional, realistic, watercolor, etc.)\n- Placement on body\n- Size (approximate dimensions)\n- Colors or black & grey\n- Any specific elements or symbolism\n- Reference inspirations'
                }
            ),
            'reference_image': forms.FileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'image/*'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize field properties
        self.fields['title'].help_text = 'Give your tattoo concept a descriptive title'
        self.fields['description'].help_text = 'Provide detailed information about your desired tattoo'
        self.fields['reference_image'].help_text = 'Upload a reference image (optional, but helpful)'
        self.fields['reference_image'].required = False

    def clean_title(self):
        """Validate title length"""
        title = self.cleaned_data.get('title')
        if title and len(title) < 5:
            raise forms.ValidationError('Title must be at least 5 characters long.')
        return title

    def clean_description(self):
        """Validate description length"""
        description = self.cleaned_data.get('description')
        if description and len(description) < 20:
            raise forms.ValidationError('Please provide a more detailed description (at least 20 characters).')
        return description
