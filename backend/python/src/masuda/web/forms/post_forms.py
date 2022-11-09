from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from masudaapi.models import Post

class SearchForm(forms.Form):
    keyword = forms.CharField(
        label='キーワード',
        max_length=200,
        required=False
    )
    masuda_id = forms.CharField(
        label='増田ID',
        max_length=50,
        required=False
    )
    posted_at_from = forms.DateTimeField(
        label='投稿日時from',
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=['%Y-%m-%d %H:%M'],
        required=False
    )
    posted_at_to = forms.DateTimeField(
        label='投稿日時to',
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=['%Y-%m-%d %H:%M'],
        required=False
    )
    response_count_from = forms.IntegerField(
        label='トラックバック数from',
        required=False
    ) 
    response_count_to = forms.IntegerField(
        label='トラックバック数to',
        required=False
    ) 
    bookmark_count_from = forms.IntegerField(
        label='ブックマーク数from',
        required=False
    ) 
    bookmark_count_to = forms.IntegerField(
        label='ブックマーク数to',
        required=False
    ) 
    may_be_deleted = forms.BooleanField(
        label='削除されたかもしれない',
        required=False,
        widget=forms.CheckboxInput(
            # attrs={'class': 'form-control'}
        )
    )
    space_masuda = forms.BooleanField(
        label='スペース増田',
        required=False,
        widget=forms.CheckboxInput()
    )
    delete_later = forms.BooleanField(
        label='あとで消す',
        required=False,
        widget=forms.CheckboxInput(
            # attrs={'class': 'form-control'}
        )
    )
    page_size = forms.IntegerField(
        label='ページあたりの件数',
        initial=25,
        required=False,
        min_value=1,
        validators=[MinValueValidator(1)]
    )

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'body')

class FetchForm(forms.Form):
    page_from = forms.IntegerField(
        label='ページ数from',
        initial=1,
        required=True,
        min_value=1,
        validators=[MinValueValidator(1)]
    )
    page_to = forms.IntegerField(
        label='ページ数to',
        initial=1,
        required=True,
        min_value=1,
        validators=[MinValueValidator(1)]
    )

class SelectiveDeleteForm(forms.Form):

    class AcceptAnythingMultipleChoiceField(forms.MultipleChoiceField):
        def validate(self, value):
            if self.required and not value:
                raise ValidationError(
                    self.error_messages['required'], 
                    code='required'
                )
    del_ids = AcceptAnythingMultipleChoiceField(
        required=True,
        # choices=(('1', 'a'), ('2', 'b')),
        # widget=forms.CheckboxSelectMultiple
    )
