from django.contrib import admin
from .models import ChatSession, Interaction


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_active', 'created_at', 'ended_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'user__username')
    readonly_fields = ('session_id', 'created_at', 'ended_at')
    date_hierarchy = 'created_at'


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('pregunta_corta', 'respuesta_corta', 'feedback', 'session', 'created_at')
    list_filter = ('feedback', 'created_at')
    search_fields = ('user_message', 'bot_response')
    readonly_fields = ('interaction_id', 'created_at')
    date_hierarchy = 'created_at'

    @admin.display(description='Pregunta')
    def pregunta_corta(self, obj):
        return obj.user_message[:60]

    @admin.display(description='Respuesta')
    def respuesta_corta(self, obj):
        return obj.bot_response[:80]
