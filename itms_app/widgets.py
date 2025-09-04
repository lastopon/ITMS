"""
Custom Widgets สำหรับ Django Admin
"""
from django import forms
from django.contrib.admin.widgets import AdminFileWidget, AdminTextareaWidget
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import json


class RichTextWidget(AdminTextareaWidget):
    """
    Rich Text Editor Widget using TinyMCE
    """
    class Media:
        js = (
            'https://cdn.tiny.cloud/1/no-api-key/tinymce/6/tinymce.min.js',
            'admin/js/tinymce_config.js',
        )
    
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        attrs['class'] = 'tinymce-editor'
        attrs['data-mce-conf'] = json.dumps({
            'height': 300,
            'plugins': 'advlist autolink lists link image charmap preview anchor',
            'toolbar': 'undo redo | formatselect | bold italic backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat',
            'menubar': False,
            'statusbar': False
        })
        return super().render(name, value, attrs, renderer)


class ColorPickerWidget(forms.TextInput):
    """
    Color Picker Widget
    """
    def __init__(self, attrs=None):
        default_attrs = {'type': 'color'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    
    class Media:
        css = {
            'all': ('admin/css/color_picker.css',)
        }


class DateTimePickerWidget(forms.DateTimeInput):
    """
    Enhanced DateTime Picker Widget
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'type': 'datetime-local',
            'class': 'datetime-picker'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, format='%Y-%m-%dT%H:%M')
    
    class Media:
        css = {
            'all': ('admin/css/datetime_picker.css',)
        }
        js = ('admin/js/datetime_picker.js',)


class TagWidget(forms.TextInput):
    """
    Tag Input Widget with autocomplete
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'tag-input',
            'data-role': 'tagsinput'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    
    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/bootstrap-tagsinput/0.8.0/bootstrap-tagsinput.css',)
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/bootstrap-tagsinput/0.8.0/bootstrap-tagsinput.min.js',
            'admin/js/tag_input.js',
        )


class JSONEditorWidget(AdminTextareaWidget):
    """
    JSON Editor Widget with syntax highlighting
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'json-editor',
            'rows': 20,
            'cols': 80
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    
    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.css',
                   'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/theme/monokai.min.css')
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/javascript/javascript.min.js',
            'admin/js/json_editor.js',
        )


class ImagePreviewWidget(AdminFileWidget):
    """
    Image Upload Widget with Preview
    """
    def render(self, name, value, attrs=None, renderer=None):
        output = super().render(name, value, attrs, renderer)
        
        if value and hasattr(value, 'url'):
            image_preview = format_html(
                '<div class="image-preview">'
                '<img src="{}" alt="Current Image" style="max-width: 200px; max-height: 200px; margin: 10px 0;"/>'
                '<p><a href="{}" target="_blank">View Full Size</a></p>'
                '</div>',
                value.url,
                value.url
            )
            output = format_html('{}<br/>{}', image_preview, output)
        
        return mark_safe(output)
    
    class Media:
        css = {
            'all': ('admin/css/image_preview.css',)
        }


class StatusWidget(forms.Select):
    """
    Enhanced Status Select Widget with colored options
    """
    def __init__(self, attrs=None, choices=None):
        default_attrs = {
            'class': 'status-select'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, choices=choices)
    
    def render(self, name, value, attrs=None, renderer=None):
        output = super().render(name, value, attrs, renderer)
        return format_html(
            '<div class="status-widget-wrapper">{}</div>',
            output
        )
    
    class Media:
        css = {
            'all': ('admin/css/status_widget.css',)
        }
        js = ('admin/js/status_widget.js',)


class AutocompleteWidget(forms.TextInput):
    """
    Autocomplete Widget for foreign key fields
    """
    def __init__(self, model=None, attrs=None):
        self.model = model
        default_attrs = {
            'class': 'autocomplete-input',
            'data-autocomplete': 'true'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    
    class Media:
        js = ('admin/js/autocomplete.js',)
        css = {
            'all': ('admin/css/autocomplete.css',)
        }


class MoneyWidget(forms.TextInput):
    """
    Money/Currency Input Widget
    """
    def __init__(self, attrs=None, currency='USD'):
        self.currency = currency
        default_attrs = {
            'class': 'money-input',
            'data-currency': currency,
            'placeholder': f'0.00 {currency}'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    
    class Media:
        js = ('admin/js/money_widget.js',)
        css = {
            'all': ('admin/css/money_widget.css',)
        }


class PasswordStrengthWidget(forms.PasswordInput):
    """
    Password Input with Strength Indicator
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'password-strength',
            'autocomplete': 'new-password'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        output = super().render(name, value, attrs, renderer)
        strength_indicator = format_html(
            '<div class="password-strength-indicator">'
            '<div class="strength-bar"><div class="strength-fill"></div></div>'
            '<div class="strength-text">Password Strength: <span class="strength-level">Weak</span></div>'
            '<ul class="strength-requirements">'
            '<li data-requirement="length">At least 8 characters</li>'
            '<li data-requirement="uppercase">One uppercase letter</li>'
            '<li data-requirement="lowercase">One lowercase letter</li>'
            '<li data-requirement="number">One number</li>'
            '<li data-requirement="special">One special character</li>'
            '</ul>'
            '</div>'
        )
        return format_html('{}{}', output, strength_indicator)
    
    class Media:
        js = ('admin/js/password_strength.js',)
        css = {
            'all': ('admin/css/password_strength.css',)
        }


class MultiSelectWidget(forms.SelectMultiple):
    """
    Enhanced Multiple Select Widget with search
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'multi-select',
            'data-placeholder': 'Select multiple options...'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    
    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/select2/4.1.0-rc.0/css/select2.min.css',)
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/select2/4.1.0-rc.0/js/select2.min.js',
            'admin/js/multi_select.js',
        )