from distutils.command.upload import upload
import imp
from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
import requests



# Create your models here.

class CMSMenu(models.Model):
    parent = models.ForeignKey('self', on_delete=models.PROTECT, related_name='children', null=True, blank=True)
    name = models.CharField(max_length=255)
    position = models.IntegerField(unique=True, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)

    class Meta:
        verbose_name_plural = 'CMSMenus'
        ordering = ('-id', )

    def __str__(self):
        return self.name
	
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)



class CMSMenuContent(models.Model):
    cms_menu = models.ForeignKey(CMSMenu, on_delete=models.PROTECT, related_name='cms_menu_contents')
    name = models.CharField(max_length=1000,unique=False,null=True,blank=True)
    position = models.IntegerField(unique=True, null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    value = models.TextField(null=True,blank=True)
    description = models.TextField(null=True, blank=True)
    duration = models.CharField(max_length=100,null=True, blank=True)
    inclution = models.TextField(null=True, blank=True)
    exclusion = models.TextField(null=True, blank=True)
    url = models.CharField(max_length=1000, null=True, blank=True)
    price = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)

    class Meta:
        verbose_name_plural = 'CMSMenuContents'
        ordering = ('id',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class CMSMenuContentImage(models.Model):
    cms_menu = models.ForeignKey(CMSMenu, on_delete=models.PROTECT, related_name='cms_menu_content_images')
    head = models.CharField(max_length=500)
    image = models.ImageField(upload_to='cms/ContentImage/',null=True, blank=True)
    cloudflare_image = models.URLField(max_length=500, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    

    class Meta:
        verbose_name_plural = 'CMSMenuContentImages'
        ordering = ('-id', )

    def __str__(self):
        return self.head
        
    def save(self, *args, **kwargs):
        if self.image:
            try:
                self.cloudflare_image = self.upload_cloudflare()
                print("Cloudflare image URL:", self.cloudflare_image)
            except Exception as e:
                print(f"Error uploading image to Cloudflare: {str(e)}")
        super().save(*args, **kwargs)
    def upload_cloudflare(self):
        endpoint = 'https://api.cloudflare.com/client/v4/accounts/f8b413899d5239382d13a2665326b04e/images/v1'
        headers = {
            'Authorization': 'Bearer Ook1HC9KydDm4YfqkmVH5KnoNsSugDDqgLFj4QHi',
        }
        files = {
            'file': self.image.file
        }
        response = requests.post(endpoint, headers=headers, files=files)
        response.raise_for_status()
        json_data = response.json()
        variants = json_data.get('result', {}).get('variants', [])
        if variants:
            cloudflare_image = variants[0]  # Use the first variant URL
            print("Cloudflare image URL from response:", cloudflare_image)
            return cloudflare_image
        else:
            print("No variants found in the Cloudflare response")
            return None







 
#add this
class Itinerary(models.Model):
    cms_content = models.ForeignKey(CMSMenuContent, on_delete=models.PROTECT,null=True,blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=1000, null=True, blank=True)

    image = models.ImageField(upload_to='cms/ContentImage/',null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Itinerary'
        ordering = ('-id', )

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)       


#For Contact



class EmailAddress(models.Model):
    full_name = models.CharField(max_length=255,null=True, blank=True)
    email = models.EmailField(null=False, blank=False)
    subject = models.CharField(max_length=255,null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'Contact'
        ordering = ('-id', )

    def __str__(self):
        return self.email
    
@receiver(post_save, sender=EmailAddress)
def send_email_on_new_signup(sender, instance, created, **kwargs):
    if created:
        # Send contact confirmation email
        subject = 'New Customer Contact With us'
        message = f'Customer Details,\n\n'
        message += f'Full Name: {instance.full_name}\n'
        message += f'Email: {instance.email}\n'
        message += f'Subject: {instance.subject}\n'
        message += f'Message: {instance.message}\n'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = ['sales@dreamziarah.com',]
        send_mail(subject, message, from_email, recipient_list)

        # Send feedback email to the sender
        feedback_subject = 'Your Journey Awaits with Dream Tourism'
        feedback_message = render_to_string('contactUs_feedback.html')
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [instance.email]
        send_mail(
            feedback_subject,
            '',
            from_email,
            recipient_list,
            html_message=feedback_message,
        )

#For Subscription

class SendEmail(models.Model):
   
    email = models.EmailField(null=False, blank=False)
    class Meta:
        verbose_name_plural = 'Send Email'
        ordering = ('-id', )

    def __str__(self):
        return self.email
    
@receiver(post_save, sender=SendEmail)
def send_email(sender, instance, created, **kwargs):
    if created:
        subject = 'New Email Subscription'
        message = render_to_string('subscription_confirmation_email.html', {'email': instance.email})

        from_email = settings.EMAIL_HOST_USER
        recipient_list = ['sales@dreamziarah.com', ]
        send_mail(
            subject,
            '',
            from_email,
            recipient_list,
            html_message=message,
        )
        feedback_subject = "Welcome to Dream Tourism's Travel Community!"
        feedback_message = render_to_string('welcome_email.html')

        from_email = settings.EMAIL_HOST_USER
        recipient_list = [instance.email]
        send_mail(
            feedback_subject,
            '',
            from_email,
            recipient_list,
            html_message=feedback_message,
        )




#add this
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name




class Blog(models.Model):
    
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='cms/BlogImage/',null=True, blank=True)
    cloudflare_image = models.URLField(max_length=500, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    short_des = models.TextField(null=True, blank=True)
    blog_category = models.CharField(max_length=255)
    date = models.DateField(blank=True)
    # tags = models.CharField( blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Blog'
        ordering = ('-id', )

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.image:
            try:
                self.cloudflare_image = self.upload_cloudflare()
                print("Cloudflare image URL:", self.cloudflare_image)
            except Exception as e:
                print(f"Error uploading image to Cloudflare: {str(e)}")
        super().save(*args, **kwargs)
    def upload_cloudflare(self):
        endpoint = 'https://api.cloudflare.com/client/v4/accounts/f8b413899d5239382d13a2665326b04e/images/v1'
        headers = {
            'Authorization': 'Bearer Ook1HC9KydDm4YfqkmVH5KnoNsSugDDqgLFj4QHi',
        }
        files = {
            'file': self.image.file
        }
        response = requests.post(endpoint, headers=headers, files=files)
        response.raise_for_status()
        json_data = response.json()
        variants = json_data.get('result', {}).get('variants', [])
        if variants:
            cloudflare_image = variants[0]  # Use the first variant URL
            print("Cloudflare image URL from response:", cloudflare_image)
            return cloudflare_image
        else:
            print("No variants found in the Cloudflare response")
            return None

class BlogComments(models.Model):
    
    blog = models.ForeignKey(Blog,on_delete=models.PROTECT,null=True,blank=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    comment_des = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)


    class Meta:
        verbose_name_plural = 'Blog_Comments'
        ordering = ('-id', )

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)       

              
