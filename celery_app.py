# celery_app.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('mypet')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Tarefas periódicas
app.conf.beat_schedule = {
    'enviar-lembretes-agendamentos': {
        'task': 'apps.notificacoes.tasks.enviar_lembretes_agendamentos',
        'schedule': crontab(hour=8, minute=0),  # 8h da manhã
    },
}

# Configuração de beat schedule
# Para usar django-celery-beat, descomente a linha abaixo e configure no admin
# app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

