from django import forms
from .models import UploadedFile

class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['title', 'description', 'file', 'file_type', 'is_free', 'price', 'project_manager']

    def clean(self):
        cleaned_data = super().clean()
        is_free = cleaned_data.get('is_free')
        price = cleaned_data.get('price')
        if not is_free and (price is None):
            self.add_error('price', 'لطفاً قیمت را وارد کنید یا گزینه رایگان را فعال کنید.')
        return cleaned_data
