from django.contrib.auth.models import BaseUserManager

class UserBaseManager(BaseUserManager):
    def create_user(self, email, firstName, lastName, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not firstName and not lastName:
            raise ValueError('Users must have a first and last name')
        
        user = self.model(
            email=email,
            firstName=firstName,
            lastName=lastName,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, firstName, lastName, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, firstName, lastName, password, **extra_fields)
    