from django.db import models

# Create your models here.

class MODELNAME(models.Model):
    """Model definition for MODELNAME."""

    # TODO: Define fields here

    class Meta:
        """Meta definition for MODELNAME."""

        verbose_name = 'MODELNAME'
        verbose_name_plural = 'MODELNAMEs'

    def __str__(self):
        """Unicode representation of MODELNAME."""
        pass

    def save(self):
        """Save method for MODELNAME."""
        pass

    def get_absolute_url(self):
        """Return absolute url for MODELNAME."""
        return ('')

    # TODO: Define custom methods here
