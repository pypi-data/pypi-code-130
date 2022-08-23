from django.db import models
# from django.utils.translation import ugettext_lazy as _

class GalleryImage(models.Model):
    title = models.CharField(max_length=256)
    key = models.CharField(max_length=256)    
    # image_a = models.FileField(_('image_a'), null=False, blank=False, help_text="image(s3)" )
    image = models.ImageField('image',null=False,blank=False,upload_to='gallery/%Y/%m/%d/')
   
    
from .fields import PrivateFileField
class PrivateFile(models.Model):
    """演示：带私有文件字段的模型"""
    name = models.CharField(max_length=256)
    some_file = PrivateFileField('file')
    
    
# class FileDemoModel(models.Model):
#     """演示：文件字段，一般情况"""
#     name = models.CharField(max_length=256)
#     my_file = models.FileField()