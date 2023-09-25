from django.db import models


class ServerLog(models.Model):
    """
    Логи сервера.
    """

    class Meta:
        verbose_name = 'запись'
        verbose_name_plural = 'Логи'

    def __str__(self):
        return f'Лог №{self.pk} от ' + str(self.time.strftime('%H:%M:%S %d.%m.%Y'))

    url = models.URLField(
        max_length=200,
        verbose_name='URL запроса'
    )
    time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время'
    )
    request = models.TextField(
        null=True,
        verbose_name='Body запроса',
    )
    response_status = models.CharField(
        max_length=200,
        verbose_name='Статус ответа'
    )
    response = models.TextField(
        verbose_name='Body ответа'
    )


class UserLog(models.Model):
    """
    Пользовательские логи.
    """

    class Meta:
        verbose_name = 'запись'
        verbose_name_plural = 'Пользовательские логи'

    def __str__(self):
        return f'Лог №{self.pk} от ' + str(self.time.strftime('%H:%M:%S %d.%m.%Y'))

    time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время'
    )
    status = models.CharField(
        max_length=200,
        verbose_name='Статус операции'
    )
