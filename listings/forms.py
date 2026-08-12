from django import forms

class VenueSearchForm(forms.Form):
    guest_count = forms.IntegerField(required=False, min_value=1)
    event_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    lat = forms.FloatField(required=False)
    lng = forms.FloatField(required=False)
    radius_km = forms.FloatField(required=False, initial=25.0)