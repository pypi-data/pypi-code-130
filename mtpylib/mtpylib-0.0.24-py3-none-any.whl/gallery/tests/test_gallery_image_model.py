import unittest

from django.test import TestCase
from ..models import  GalleryImage
from django.core.files.base import ContentFile
from django.utils import timezone



class Test_Gallery_model(TestCase):
    """"""
    def setUp(self) -> None:
        return super().setUp()
    
    
    def create_obj(self):
        obj1 = GalleryImage()
        obj1.name="name1"
        obj1.image.save('django_test.txt', ContentFile(b'content'))
        obj1.save()
        return obj1
 
    
    def test_create(self):
        newObj = self.create_obj()
        getObj = GalleryImage.objects.get(pk=newObj.pk)        
        self.assertEqual(newObj, getObj)
        
 
    
    
        
        
 