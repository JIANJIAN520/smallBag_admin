from django.db import models
import pdb

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=20)
    password = models.CharField(max_length=16)
    phone = models.CharField(max_length=11)
    is_student = models.BooleanField(default=False)
    image = models.ImageField(null=True,blank=True,upload_to='media')

    def __str__(self):
        return self.name

    def is_teacher(self):
        return self.teacher

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
        return '[' + self.get_subject_display() + ']' + self.user.__str__()

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
        d = {k:v for k, v in self.__dict__.items() if not k.startswith('_')}
        d['course'] = self.course.get_subject_display()
        return d

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

    @classmethod
    def get_problems_with_score_and_answer(cls, user_id=None, user=None,chapter_id=None, chapter=None):
        """
        根据用户和章节，获取题目信息，并携带用户的得分
        Args:
            user/user_id: 用户
            chapter/chapter_id: 章节
        Return：
            list: 题目列表
        """
        chapter_id = chapter_id or chapter.id
        user_id = user_id or user.id

        # 章节对应的所有问题以及题目数量
        problems = list(cls.objects.filter(chapter_id=chapter_id))
        problems_count = len(problems)

        for p in problems:
            p.answer = None
            p.score = 0
            answer = p.get_user_answer(user_id=user_id)
            if not answer:
                continue
            p.score = 100/problems_count if p.is_answer_correct(answer) else 0
            p.answer = {
                'option_id': answer.option_id,
                'option_title': answer.option.title
            }
        return problems

    @classmethod
    def cal_chapter_score(cls, user_id=None, user=None,chapter_id=None, chapter=None):
        """
        计算章节练习得分
        Args:
            user/user_id: 用户
            chapter/chapter_id: 章节
        Return：
            int: 章节练习得分
        """
        user_id = user_id or user.id
        chapter_id = chapter_id or chapter.id
        score = cls.get_chapter_score(user_id=user_id, chapter_id=chapter_id)
        res, _ = Score.objects.get_or_create(chapter_id=chapter_id,user_id=user_id)
        res.score = score
        res.save()
        return True

    @classmethod
    def get_chapter_score(cls, user_id=None, user=None,chapter_id=None, chapter=None):
        """
        计算章节练习得分
        Args:
            user/user_id: 用户
            chapter/chapter_id: 章节
        Return：
            int: 章节练习得分
        """
        user_id = user_id or user.id
        chapter_id = chapter_id or chapter.id
        score = 0
        problems = cls.get_problems_with_score_and_answer(user_id=user_id, chapter_id=chapter_id)  
        for p in problems:
            score += p.score
        return score

    def get_user_answer(self, user=None, user_id=None):
        """
        给定用户，获取用户对该题的回答
        Args:
            user/user_id: 用户
        Return:
            UserAndProblem: 用户的回答
        """
        user_id = user_id or user.id
        return self.userandproblem_set.filter(user_id=user_id).first()

    def is_answer_correct(self, answer):
        """
        判断给定的答案是否正确
        Args:
            answer<Solution>: 给定的答案
        Return:
            bool: 是否正确
        """
    
        if not answer:
            return False
        solutions =  self.get_solutions()
        if not solutions:
            return False
        return solutions[0]['option_id'] == answer.option_id

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
        d['option'] = self.option.to_dict()
        return d


class UserAndProblem(models.Model):
    problem = models.ForeignKey(Problem,on_delete=models.CASCADE)
    option = models.ForeignKey(Option,on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answered = models.BooleanField(default=False)

    def to_dict(self):
        d = {k:v for k, v in self.__dict__.items() if not k.startswith('_')}
        d['problem'] = self.problem.to_dict()
        d['option'] = self.option.to_dict()
        d['user'] = self.user.to_dict()
        return d


class Score(models.Model):
    score = models.FloatField(default=0.0)
    chapter = models.ForeignKey(Chapter,on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField('创建时间',auto_now_add=True)

    def to_dict(self):
        d = {k:v for k, v in self.__dict__.items() if not k.startswith('_')}
        d['chapter'] = self.chapter.to_dict()
        return d