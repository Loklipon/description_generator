from django.db import models


class Product(models.Model):
    """
    Продукт.
    """

    class Meta:
        verbose_name = 'элемент номенклатуры'
        verbose_name_plural = 'Номенклатура'
        ordering = ('type', 'name')

    def __str__(self):
        return self.name

    uuid = models.UUIDField(
        verbose_name='UUID продукта'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название продукта'
    )
    description = models.TextField(
        null=True,
        verbose_name='Описание продукта'
    )
    type = models.CharField(
        max_length=200,
        null=True,
        verbose_name='Тип'
    )
    num = models.CharField(
        max_length=200,
        null=True,
        verbose_name='Артикул'
    )


class Monitoring(models.Model):
    """
    Мониторинг.
    """

    class Meta:
        verbose_name = 'запись'
        verbose_name_plural = 'Мониторинг'

    def __str__(self):
        return f'Проверка ТТК блюда "{self.dish_name}".'

    dish_name = models.CharField(
        max_length=200,
        verbose_name='Блюдо'
    )
    num = models.CharField(
        max_length=200,
        null=True,
        verbose_name='Артикул'
    )
    status = models.CharField(
        max_length=200,
        verbose_name='Статус выгрузки'
    )
    error = models.CharField(
        max_length=200,
        verbose_name='Описание'
    )
    date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата выгрузки'
    )


class Department(models.Model):
    """
    Организация.
    """

    class Meta:
        verbose_name = 'торговая точка'
        verbose_name_plural = 'Торговые точки'

    def __str__(self):
        return self.name

    name = models.CharField(
        max_length=200,
        verbose_name='Наименование организации'
    )
    uuid = models.UUIDField(
        verbose_name='UUID организации'
    )


class Document(models.Model):
    """
    Приказ.
    """

    class Meta:
        verbose_name = 'приказ'
        verbose_name_plural = 'Приказы'

    def __str__(self):
        return 'Приказ'

    document_number = models.CharField(
        max_length=200,
        verbose_name='Номер приказа',
        null=True
    )
    date = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        null=True
    )
    organization = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        verbose_name='Торговая точка',
        null=True
    )
    file = models.FileField(
        verbose_name='Файл приказа',
        null=True
    )
    response = models.TextField(
        verbose_name='Body ответа',
        null=True
    )


class Chain(models.Model):
    """
    Чейн.
    """

    class Meta:
        verbose_name = 'учетные данные'
        verbose_name_plural = 'Учетные данные'

    def __str__(self):
        return 'Учетные данные'

    name = models.CharField(
        max_length=200,
        verbose_name='Название организации',
    )
    server_url = models.URLField(
        verbose_name='Адрес сервера'
    )
    server_port = models.CharField(
        max_length=200,
        verbose_name='Порт'
    )
    server_login = models.CharField(
        max_length=200,
        verbose_name='Логин',
    )
    server_password = models.CharField(
        max_length=200,
        verbose_name='Пароль',
    )


class Config(models.Model):
    check_button = models.BooleanField(
        default=False
    )
