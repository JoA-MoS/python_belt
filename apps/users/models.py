# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
import validate
from error import Error
import bcrypt

# Create your models here.


class UserManager(models.Manager):
    def validate_registration(self, data):
        errors = []
        valid, data = validate.registration_form(data)
        if valid:
            existing_users = self.filter(email=data['email'])
            if existing_users:
                errors.append(Error(
                    'email', 'email already registered if you have forgoten your password please use the password reset link'))
            else:
                return (True, data)
        
        errors.extend(data)
        return (False, errors)
           
    def add_user(self, data, ses):
        valid, errors = self.validate_registration(data)
        if valid:
            hashedpwd = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt())
            new_user = self.create(first_name=data['first_name'],
                                       last_name=data['last_name'],
                                       email=data['email'],
                                       password=hashedpwd,)
            ses['user_id'] = new_user.id
            return (valid, new_user)
        else:
            return (valid, errors)

    def get_user(self, user_id):
        try:
            return self.get(id=user_id)
        except:
            return None

    def logged_in(self, ses):
        if 'user_id' in ses:
            try:
                user = self.get_user(ses['user_id'])
                return user
            except:
                return None
        return None

    def authenticate(self, data, ses):
        errors = []
        users = {}
        valid, data = validate.login_form(data)
        if valid:
            # if the login form looks good check if the user password matches
            users = self.filter(email=data['email'])
            if len(users) > 1:
                errors.append(Error('email', 'something went wrong please contact customer support'))
            elif len(users) == 0:
                errors.append(Error('email', 'please check your email and try again'))
            else:
                if bcrypt.hashpw(data['password'].encode(), users[0].password.encode()) != users[0].password:
                    errors.append(Error('email, password', 'incorrect email and password combination please try again'))
                else:
                    ses['user_id']=users[0].id
                    return (True, users[0])
        
        errors.extend(data)
        return (False, errors)
            


class User(models.Model):
    objects = UserManager()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}: {} {} {}'.format(self.id, self.first_name, self.last_name, self.email)

    def __unicode__(self):
        return '{}: {} {} {}'.format(self.id, self.first_name, self.last_name, self.email)

    @property
    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    @property
    def is_authenticated(self):
        #if we have a user object to access this property then 
        #they are authenticated it should always be true
        return True
