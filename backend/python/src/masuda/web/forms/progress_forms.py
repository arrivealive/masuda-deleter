from re import L
from django import forms
from django.core.exceptions import ValidationError
from masudaapi.models import Progress

class FilterDeleteForm(forms.Form):

    class AcceptAnythingMultipleChoiceField(forms.MultipleChoiceField):
        def validate(self, value):
            if self.required and not value:
                raise ValidationError(
                    self.error_messages['required'], 
                    code='required'
                )
    status = AcceptAnythingMultipleChoiceField(
        label='削除対象',
        required=True,
        choices=[(status.value, status.label) for status in Progress.STATUS if status.name not in ['PENDING', 'PROCESSING']],
        widget=forms.CheckboxSelectMultiple,
        initial=[Progress.STATUS.PROCESSED, Progress.STATUS.STOPPED, Progress.STATUS.ERROR]
    )
    

