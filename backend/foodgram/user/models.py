from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator

class UserProfile(AbstractUser):
    username = models.CharField(
        verbose_name='Имя пользователя',
        validators=[UnicodeUsernameValidator()],
        max_length=150,
        unique=True
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150,
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Адрес электронной почты',
    )
    first_name = models.CharField(
        verbose_name='Введите ваше имя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Введите вашу фамилию',
        max_length=150,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
    
    def __str__(self):
        return f'{self.username}: {self.email}'

class Follow(models.Model):

    following = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='following')
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='follower')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_name_follow'
            )
        ]
    
    def __str__(self):
        return f'{self.user} follows {self.following}'