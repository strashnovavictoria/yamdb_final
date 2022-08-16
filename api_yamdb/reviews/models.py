import datetime

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    """Модель User"""
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (USER, USER),
        (MODERATOR, MODERATOR),
        (ADMIN, ADMIN),
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Имя пользователя'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        verbose_name='Почта'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Фамилия'
    )
    role = models.CharField(
        choices=ROLE_CHOICES,
        max_length=50,
        default=USER,
        verbose_name='Роль пользователя'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография пользователя'
    )

    @property
    def is_admin(self):
        return self.is_staff or self.role == User.ADMIN

    @property
    def is_moderator(self):
        return self.role == User.MODERATOR

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Category(models.Model):
    """Модель категорий (типов) произведений"""
    name = models.CharField(
        max_length=256,
        unique=True,
        verbose_name='Категория'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Адрес'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория',
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель жанров произведений"""
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Жанр'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Адрес'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр',
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель произведений"""
    name = models.CharField(
        max_length=256,
        verbose_name='Название произведения'
    )
    year = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(datetime.date.today().year)],
        default=datetime.date.today().year,
        db_index=True,
        verbose_name='Дата создания произведения'
    )
    description = models.TextField(
        blank=True,
        null=True,
        default='',
        verbose_name='Описание произведения'
    )
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        default=None,
        null=True,
        verbose_name='Жанр'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Произведение',
        verbose_name_plural = 'Произведения'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'year', 'category'],
                name='unique_title'
            )
        ]

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзывов на произведения"""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5,
        verbose_name='Оценка произведения (1-10)'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации отзыва'
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Отзыв',
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]


class Comment(models.Model):
    """Модель комментариев на отзывы"""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Произведение'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(
        verbose_name='Текст комментария'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата добавления комментария'
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Комментарий',
        verbose_name_plural = 'Комментарии'
