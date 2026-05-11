from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    reply_text = models.TextField(blank=True, null=True, help_text="Admin reply to this contact message")
    reply_sent_at = models.DateTimeField(blank=True, null=True, help_text="When the reply was sent")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    @property
    def has_replied(self):
        return bool(self.reply_text and self.reply_sent_at)