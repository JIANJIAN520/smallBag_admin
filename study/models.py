from django.db import models

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=20)
    password = models.CharField(max_length=16)
    phone = models.CharField(max_length=11)
    is_student = models.BooleanField(default=False)
    image = models.ImageField(null=True,blank=True,upload_to='media')
    def __str__(self):
        return self.name

    def to_dict(self):
        res = {k:v for k, v in self.__dict__.items() if not k.startswith('_') and k != 'password'}
        return res

class Teacher(models.Model):
    SUBJECTS = (
        ('chinese', '语文'),
        ('math', '数学'),
        ('english', '英语')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subject = models.CharField('科目', choices=SUBJECTS, max_length=20)
    sex = models.IntegerField(default=0)
    education = models.CharField(max_length=20)
    teaching_age = models.IntegerField(default=0)
    teach_code = models.CharField(max_length=20)
    picture = models.ImageField(null=False,blank=False,upload_to='media')
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.subject.__str__()

    def to_dict(self):
        d = {k:v for k, v in self.__dict__.items() if not k.startswith('_')}
        d.update(self.user.to_dict())
        return d



class Course(models.Model):
    GRADES = (
        ('1', '一年级上'),
        ('2', '一年级下'),
        ('3', '二年级上'),
        ('4', '二年级下'),
        ('5', '三年级上'),
        ('6', '三年级下'),
        ('7', '四年级上'),
        ('8', '四年级下'),
        ('9', '五年级上'),
        ('10', '五年级下'),
        ('11', '六年级上'),
        ('12', '六年级下'),
    )
    SUBJECTS = (
        ('chinese', '语文'),
        ('math', '数学'),
        ('english', '英语')
    )
    teacher = models.ForeignKey(Teacher,on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    image = models.ImageField(null=False,blank=False,upload_to='media')
    subject = models.CharField('科目', choices=SUBJECTS, max_length=20)
    grade = models.CharField(choices=GRADES, max_length=20)
    price = models.FloatField(default=0.0)
    description = models.CharField(default='',max_length=200)
    date = models.DateTimeField('创建时间',auto_now_add=True)
    def __str__(self):
        return self.name

    def to_dict(self):
        d = {k:v for k, v in self.__dict__.items() if not k.startswith('_')}
        d['teacher'] = self.teacher.to_dict()
        return d


class Chapter(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    video = models.FileField(upload_to='media',default='')
    description = models.CharField(null=True,blank=True,max_length=200)
    def __str__(self):
        return self.name
    def to_dict(self):
        return {k:v for k, v in self.__dict__.items() if not k.startswith('_')}

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    is_like = models.BooleanField(default=False)
    def to_dict(self):
        return {k:v for k, v in self.__dict__.items() if not k.startswith('_')}



class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    date = models.DateTimeField('创建时间',auto_now_add=True)
    def __str__(self):
        return self.content
    
    def to_dict(self):
        d = {k:v for k, v in self.__dict__.items() if not k.startswith('_')}
        d['user'] = self.user.to_dict()
        return d


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateTimeField('创建时间',auto_now_add=True)
    is_pay = models.BooleanField(default=False)


class UserAndCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    can_watch = models.BooleanField(default=False)
    
    def to_dict(self):
        d = {k:v for k, v in self.__dict__.items() if not k.startswith('_')}
        d['user'] = self.user.to_dict()
        d['course'] = self.course.to_dict()
        return d

class Problem(models.Model):
    title = models.CharField(max_length=200)
    chapter = models.ForeignKey(Chapter,on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_options(self):
        return [op.to_dict() for op in self.option_set.all()]

    def get_solutions(self):
        return [s.to_dict() for s in self.solution_set.all()]

    def get_userAndProblems(self):
        return [u.to_dict() for u in self.userAndProblem_set.all()]

    def to_dict(self):
        d = {k:v for k, v in self.__dict__.items() if not k.startswith('_')}
        d['chapter'] = self.chapter.to_dict()
        d['options'] = self.get_options()
        d['solutions'] = self.get_solutions()
        return d

class Option(models.Model):
    problem = models.ForeignKey(Problem,on_delete=models.CASCADE)
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title
    def to_dict(self):
        d = {k:v for k, v in self.__dict__.items() if not k.startswith('_')}
        return d

class Solution(models.Model):
    problem = models.ForeignKey(Problem,on_delete=models.CASCADE)
    option = models.ForeignKey(Option,on_delete=models.CASCADE)
    def to_dict(self):
        d = {k:v for k, v in self.__dict__.items() if not k.startswith('_')}
        return d

class UserAndProblem(models.Model):
    problem = models.ForeignKey(Problem,on_delete=models.CASCADE)
    option = models.ForeignKey(Option,on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answered = models.BooleanField(default=False)

    def to_dict(self):
        d = {k:v for k, v in self.__dict__.items() if not k.startswith('_')}
        # d['problem'] = self.problem.to_dict()
        # d['option'] = self.option.to_dict()
        # d['user'] = self.user.to_dict()
        return d