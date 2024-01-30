from django.db import models
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import FileExtensionValidator
from .xmltools import analyze_file, include_sync_button
from enum import Enum
import uuid


def default_color():
    return '#076AAB'

def default_favor_color():
    return '#417505'

def default_conflict_color():
    return '#d0021b'

class NodeTypes(Enum):
    DEFAULT = "default"
    MERGING = "merging"

class Project(models.Model):
    name = models.CharField(_("Name"), max_length=100)
    picture = models.FileField(_("Picture"), null=True, blank=True)
    description = models.CharField(_("Description"), max_length=200,
                                   null=True, blank=True)
    password = models.CharField(
        _("Password"), max_length=50, null=True, blank=True)
    pin = models.CharField(_("PIN"), max_length=6, unique=True)
    id = models.UUIDField(_("Id"), primary_key=True,
                          default=uuid.uuid4, editable=False)
    email = models.EmailField(_("Email"), null=True, blank=True)
    default_color = models.CharField(_("node_color"), max_length=7, default=default_color())
    favor_color = models.CharField(_("favor_color"), max_length=7, default=default_favor_color())
    conflict_color = models.CharField(_("conflict_color"), max_length=7, default=default_conflict_color())

    @classmethod
    def create_and_save(cls, name, picture, description, password=""):
        proj = cls.objects.create(
            name=name, picture=picture, description=description, password=password)
        proj.save()
        return proj

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")


class File(models.Model):
    # Format: YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]
    timestamp = models.DateTimeField(
        _("Timestamp"), auto_now_add=True, auto_now=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.ManyToManyField.symmetrical
    ancestors = models.ManyToManyField("self", symmetrical=False)
    description = models.CharField(_("Description"), max_length=200,
                                   null=True, blank=True)
    number_scripts = models.IntegerField(_("number_scripts"), default=0)
    number_sprites = models.IntegerField(_("number_sprites"), default=0)
    color = models.CharField(_("color"), max_length=7, default=default_color())

    class Meta:
        abstract = True


class SnapFile(File):
    # validates only naming of file
    file = models.FileField(_("File"), blank=True, validators=[
        FileExtensionValidator(['xml', 'XML', 'conflict'])])
    # thumbnail = models.ImageField(_("Thumbnail"), null=True, blank=True)
    user = models.CharField(_("user"), max_length=30, null=True)
    xPosition = models.FloatField(_("xPosition"), default=0)
    yPosition = models.FloatField(_("yPosition"), default=0)
    collapsed = models.BooleanField(_("collapsed"), default=False)
    hidden = models.BooleanField(_("hidden"), default=False)
    type = models.CharField(_("type"), max_length=30, null=True, default=NodeTypes.DEFAULT.value)

    @classmethod
    def create_and_save(cls, project, file, ancestors=None, user=None, description=''):
        snap = cls.objects.create(
            project=project, file=file, user=user, description=description)
        if (ancestors):
            snap.ancestors.set(ancestors)
            if(type(ancestors[0]) == str):
                ancestor_as_file = SnapFile.objects.get(id=int(ancestors[0]))
                snap.xPosition = ancestor_as_file.xPosition
                snap.yPosition = ancestor_as_file.yPosition + 100
            else:
                snap.xPosition = ancestors[0].xPosition
                snap.yPosition = ancestors[0].yPosition + 100

        snap.save()
        return snap

    def xml_job(self):
        include_sync_button(self.get_media_path(),
                            proj_id=self.project.id, me=self.id)

        stats = analyze_file(self.get_media_path())
        self.number_scripts = stats[0]
        self.number_sprites = stats[1]

        self.save()

    def as_dict(self):
        ancestor_ids = [x.id for x in self.ancestors.all()]

        return {
            'id': self.id,
            'description': self.description,
            'ancestors': ancestor_ids,
            'file_url': self.get_media_path(),
            'timestamp': str(self.timestamp),
            'number_scripts': self.number_scripts,
            'number_sprites': self.number_sprites,
            'color': self.color,
            'xPosition': self.xPosition,
            'yPosition': self.yPosition,
            'collapsed': self.collapsed,
            'hidden': self.hidden,
            'type': self.type
        }

    def get_media_path(self):
        return settings.MEDIA_URL + str(self.file)

    class Meta:
        verbose_name = _("SnapFile")
        verbose_name_plural = _("SnapFiles")


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'password', 'email']
        labels = {
            'description': _('Description (optional)'),
            'password': _('Password (optional)'),
            'email': _('email (optional), for restoring password and pin'),
        }


class SnapFileForm(ModelForm):
    class Meta:
        model = SnapFile
        fields = ['file', 'description']
        labels = {
            'file': _('File (optional)'),
            'description': _('Description (optional)'),
        }


class ConflictFile(File):
    # validates only naming of file
    file = models.FileField(_("File"), blank=True, validators=[
        FileExtensionValidator(['xml', 'XML', 'txt', 'TXT', 'base64', 'BASE64'])])

    @classmethod
    def create_and_save(cls, project, file, ancestors=None, description=''):
        confl = cls.objects.create(
            project=project, file=file, description=description)
        if (ancestors):
            confl.ancestors.set(ancestors)

        confl.save()
        return confl

    # def xml_job(self):
    #     include_sync_button(self.get_media_path(),
    #                         proj_id=self.project.id, me=self.id)

    #     stats = analyze_file(self.get_media_path())
    #     self.number_scripts = stats[0]
    #     self.number_sprites = stats[1]

    #     self.save()

    def as_dict(self):
        ancestor_ids = [x.id for x in self.ancestors.all()]
        file_url = settings.MEDIA_URL + str(self.file)

        return {
            'id': self.id,
            'description': self.description,
            'ancestors': ancestor_ids,
            'file_url': file_url,
            'timestamp': str(self.timestamp),
            'number_scripts': self.number_scripts,
            'number_sprites': self.number_sprites,
            'color': self.color
        }

    def get_media_path(self):
        return settings.MEDIA_URL + str(self.file)

    class Meta:
        verbose_name = _("ConflictFile")
        verbose_name_plural = _("ConflictFiles")


class MergeConflict(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, default="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    left = models.ForeignKey(SnapFile, on_delete=models.CASCADE, related_name="leftFile")
    right = models.ForeignKey(SnapFile, on_delete=models.CASCADE, related_name="rightFile")
    connected_file = models.ForeignKey(SnapFile, on_delete=models.DO_NOTHING, related_name="connected_file", null=True)
    hunks = models.fields


class Hunk(models.Model):
    mergeConflict = models.ForeignKey(MergeConflict, on_delete=models.CASCADE)
    left = models.ForeignKey(ConflictFile, on_delete=models.CASCADE, related_name="leftHunk")
    right = models.ForeignKey(ConflictFile, on_delete=models.CASCADE, related_name="rightHunk")
    choice = models.CharField(_("choice"), max_length=30, null=True)

    def as_dict(self):
        return {
            'id': self.id,
            'left': self.left.as_dict(),
            'right': self.right.as_dict(),
            'choice': self.choice if self.choice != None else ""
        }
