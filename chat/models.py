from django.db import models
from django.utils.six import python_2_unicode_compatible
from channels import Group
from .settings import MSG_TYPE_MESSAGE
import json
from django.contrib.auth.models import User

class Message(models.Model):
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=User)


@python_2_unicode_compatible
class Room(models.Model):
    """
    A room for people to chat in.
    """

    # Room title
    title = models.CharField(max_length=255)

    # If only "staff" users are allowed (is_staff on django's User)
    staff_only = models.BooleanField(default=False)
    old_messages = models.ManyToManyField(Message)

    def str(self):
        return self.title

    @property
    def websocket_group(self):
        return Group("room-%s" % self.id)
        #
        # Returns the Channels Group that sockets should subscribe to to get sent
        # messages as they are generated.
        #

    def send_message(self, message, user, msg_type=MSG_TYPE_MESSAGE):
        """
        Called to send a message to the room on behalf of a user.
        """
        final_msg = {'room': str(self.id), 'message': message, 'username': user.username, 'msg_type': msg_type}
        # Send out the message to everyone in the room
        self.websocket_group.send(
            {"text": json.dumps(final_msg)}
        )
