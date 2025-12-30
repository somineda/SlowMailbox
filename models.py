from tortoise import fields
from tortoise.models import Model


class Letter(Model):
    id = fields.IntField(pk=True)
    recipient_email = fields.CharField(max_length=255)
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    #7일 후
    send_at = fields.DatetimeField()
    sent = fields.BooleanField(default=False)
    sent_at = fields.DatetimeField(null=True)

    #30일 후
    second_send_at = fields.DatetimeField()
    second_sent = fields.BooleanField(default=False)
    second_sent_at = fields.DatetimeField(null=True)

    class Meta:
        table = "letters"
