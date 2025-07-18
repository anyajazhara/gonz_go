from django import forms

class ReceiptUploadForm(forms.Form):
    receipt = forms.ImageField(label="Upload Receipt", required=True)
    eta = forms.TimeField(
        label="Estimated Time of Arrival at Gonz",
        widget=forms.TimeInput(attrs={"type": "time"}),
        required=True
    )