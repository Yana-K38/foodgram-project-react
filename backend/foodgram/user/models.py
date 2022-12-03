from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Follow(models.Model):

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower')

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_name_follow'
            )
        ]

    def __str__(self):
        return f'{self.user} подписана на {self.author}'
