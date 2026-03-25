import cloudinary
import cloudinary.uploader
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class CloudinaryMediaStorage(Storage):

    def _save(self, name, content):
        # Remove extensão do public_id
        public_id = name.rsplit('.', 1)[0]
        result = cloudinary.uploader.upload(
            content,
            public_id=public_id,
            resource_type='auto',
            overwrite=True,
        )
        return result['secure_url']

    def url(self, name):
        return name  # já salva a URL completa

    def exists(self, name):
        return False  # deixa o Cloudinary gerenciar duplicatas

    def delete(self, name):
        pass