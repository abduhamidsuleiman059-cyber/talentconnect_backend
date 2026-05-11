from django.contrib import admin, messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'message_preview', 'reply_status')
    list_filter = ('created_at', 'reply_sent_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at', 'reply_sent_at')
    ordering = ('-created_at',)
    actions = ['send_reply_email']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'
    
    def reply_status(self, obj):
        if obj.has_replied:
            return f"✅ Replied {obj.reply_sent_at.strftime('%Y-%m-%d %H:%M') if obj.reply_sent_at else ''}"
        else:
            return "❌ Pending"
    reply_status.short_description = 'Reply Status'
    
    def save_model(self, request, obj, form, change):
        # Check if reply_text is being added/modified
        if change and 'reply_text' in form.changed_data:
            if obj.reply_text and obj.reply_text.strip():
                # Send email if reply is being added or modified
                try:
                    subject = f"Reply from TalentConnect - {obj.name}"
                    message = f"""
Dear {obj.name},

Thank you for contacting TalentConnect. Here is our response to your message:

---
Your Original Message:
{obj.message}
---

Our Reply:
{obj.reply_text}
---

If you have any further questions, please don't hesitate to contact us again.

Best regards,
TalentConnect Team
                    """
                    
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[obj.email],
                        fail_silently=False,
                    )
                    
                    # Set reply timestamp
                    obj.reply_sent_at = timezone.now()
                    
                    messages.success(request, f"Reply sent successfully to {obj.email}")
                    
                except Exception as e:
                    messages.error(request, f"Failed to send reply: {str(e)}")
            else:
                # Clear reply timestamp if reply text is cleared
                obj.reply_sent_at = None
                messages.info(request, "Reply cleared")
        
        super().save_model(request, obj, form, change)
    
    def send_reply_email(self, request, queryset):
        for contact in queryset:
            if contact.reply_text and not contact.reply_sent_at:
                try:
                    subject = f"Reply from TalentConnect - {contact.name}"
                    message = f"""
Dear {contact.name},

Thank you for contacting TalentConnect. Here is our response to your message:

---
Your Original Message:
{contact.message}
---

Our Reply:
{contact.reply_text}
---

If you have any further questions, please don't hesitate to contact us again.

Best regards,
TalentConnect Team
                    """
                    
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[contact.email],
                        fail_silently=False,
                    )
                    
                    contact.reply_sent_at = timezone.now()
                    contact.save()
                    
                except Exception as e:
                    messages.error(request, f"Failed to send reply to {contact.email}: {str(e)}")
        
        messages.success(request, f"Processed {queryset.count()} contact message(s)")
    
    send_reply_email.short_description = "Send reply email for selected messages"
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email')
        }),
        ('Original Message', {
            'fields': ('message',)
        }),
        ('Admin Reply', {
            'fields': ('reply_text',),
            'description': 'Enter your reply here. It will be sent to the user when you save.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'reply_sent_at'),
            'classes': ('collapse',)
        }),
    )
