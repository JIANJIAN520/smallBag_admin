from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.template import loader
from .models import User,Course,Teacher,Like,Comment,Order,UserAndCourse,Chapter,Problem,Option,Solution,UserAndProblem,Score
from django.db.models import Count
from mysite.decorator import login_require,login_check
import pdb
import json

# Create your views here.

class Result:
    @classmethod
    def ok(cls, data={}):
        return JsonResponse({
            'code': 0,
            'msg': 'ok',
            'data': data
        })

    @classmethod
    def error(cls, e_msg='error'):
        return JsonResponse({
            'code': -1,
            'msg': e_msg,
            'data': {}
        })

def login(request):
    req = json.loads(request.body.decode())
    username = req.get('username')
    password = req.get('password')
    user = User.objects.filter(name=username).first()
    if user:              
        data = {'user': user.to_dict()} if user.password == password else {'error': '密码错误！'}
        return JsonResponse(data, safe=False)
    return JsonResponse({'error': '用户不存在！'}, safe=False)

def signup(request): 
    user = json.loads(request.body.decode()).get('params')
    name = user.get('name')
    password = user.get('password')
    is_student = user.get('is_student')
    phone = user.get('phone')
    users = User.objects.filter(name=name)
    if users:
        return Result.error('用户名已存在！')
    res = User.objects.create(name=name, password=password, is_student=is_student,phone=phone)
    return Result.ok(res.to_dict()) if res else Result.error('注册失败')

def teacher(request):
    data = {}
    teachers = Teacher.objects.all()
    subject = request.GET.get('subject')
    if subject:
        teachers = teachers.filter(subject=subject)
    ret = {t.id: t.to_dict() for t in teachers}
    data["data"] = list(ret.values())
    return JsonResponse(data, safe=False)

def course(request):
    data = {}
    courses = Course.objects.all().select_related('teacher').annotate(total_chapters=Count('chapter'))
    grade = request.GET.get('grade')
    grades = {
        'one': ['1', '2'],
        'two': ['3', '4'],
        'three': ['5', '6'],
        'four': ['7', '8'],
        'five': ['9', '10'],
        'six': ['11', '12'],
    }
    if grade:
        courses = courses.filter(grade__in=grades[grade]) 
    subject = request.GET.get('subject')
    if subject:
        courses = courses.filter(subject=subject)   
    ret = {c.id: c.to_dict() for c in courses}
    course_ids = ret.keys()
    chapters = Chapter.objects.filter(course_id__in=course_ids)

    # Chanter_list和Course.id匹配上
    course_chapter_dict = {i:[] for i in course_ids}
    [course_chapter_dict[ch.course_id].append(ch.to_dict()) for ch in chapters]
    for c_id, chs in course_chapter_dict.items():
        ret[c_id]['chapters'] = chs
    
    data["data"] = list(ret.values())
    return JsonResponse(data, safe=False)

def courseDetail(request, course_id):
    data = {}
    course = Course.objects.get(pk=course_id)
    chapters = Chapter.objects.filter(course_id=course_id)
    course = course.to_dict()
    course['chapters'] = []
    [course['chapters'].append(chapter.to_dict()) for chapter in chapters]
    data['data'] = course
    return JsonResponse(data, safe=False)


def courseComment(request,course_id):
    data = {}
    comments = Comment.objects.filter(course_id=course_id).order_by('-date')
    data['data'] = [c.to_dict() for c in comments]
    return JsonResponse(data, safe=False)


def getByName(request):
    data = {}
    name = request.GET.get('name')
    courses = Course.objects.filter(name=name)
    ret = {c.id: c.to_dict() for c in courses}
    data['data'] = list(ret.values())
    return JsonResponse(data, safe=False)

def getTeacherById(request,teacher_id):
    data = {}
    teacher = Teacher.objects.get(pk=teacher_id)
    teacher = teacher.to_dict()
    teacher['courses'] = []
    if teacher:
        courses = Course.objects.filter(teacher_id=teacher_id)
        [teacher['courses'].append(course.to_dict()) for course in courses]
        data['data'] = teacher
        return JsonResponse(data,safe=False)
    return Result.error('数据不存在')

@login_require
def addComment(request,course_id):
    req = json.loads(request.body.decode())
    content = req.get('content')
    res = Comment.objects.create(user=request.user, course_id=course_id, content=content)
    return Result.ok() if res else Result.error('评论失败')

  
@login_require
def getUserAndCourse(request):
    if request.user.is_student:
        courses = UserAndCourse.objects.filter(user_id = request.user.id)
    else:
        courses = Course.objects.filter(teacher_id = request.user.teacher.id)
    return JsonResponse({
        'data': [c.to_dict() for c in courses]
    }, safe=False)


@login_check
def getLikes(request, course_id):
    likes = Like.objects.filter(
        course_id=course_id, 
        is_like=True
    ).values_list('user_id', flat=True)

    is_liker = request.user and request.user.id in likes
    return JsonResponse({
        'like_count': len(likes),
        'is_liker': is_liker
    }, safe=False)

@login_require
def updateLike(request, course_id):
    user = Like.objects.filter(user_id = request.user.id, course_id=course_id).first()
    if user:
        user.is_like = not user.is_like
        user.save()
        return Result.ok()
    like = Like.objects.create(user_id=request.user.id, course_id=course_id,is_like=True)
    return Result.ok() if like else Result.error('操作失败')

@login_check
def getProblems(request, course_id, chapter_id):
    user = request.user
    chapter_score = 0
    if user:
        problems = Problem.get_problems_with_score_and_answer(user=user, chapter_id=chapter_id)
        chapter_score = Problem.get_chapter_score(user=user, chapter_id=chapter_id)
    else:
        problems = Problem.objects.filter(chapter_id=chapter_id)
    
    # end sort 
    # [problems[a.problem_id].update({'answer_option_id': a.option_id}) for a in user_answers]
    return Result.ok({
        'problems': [p.to_dict() for p in problems],
        'scores': chapter_score
    })

@login_require
def addAnswer(request, course_id):
    answer = json.loads(request.body.decode()).get('params')
    print(answer)
    for k, v in answer.items():
        res = UserAndProblem.objects.create(
            user = request.user, 
            problem_id = k[1:],
            option_id = v, 
            answered = True)
    p = Problem.objects.filter(id=k[1:]).first()
    Problem.cal_chapter_score(user=request.user, chapter_id=p.chapter_id)
    return Result.ok() if res else Result.error('提交失败')


@login_require
def joinStudy(request,course_id):
    can_watch = request.GET.get('0')
    usercourse = UserAndCourse.objects.filter(user_id=request.user.id,course_id=course_id)
    if not usercourse:
        usercourse = UserAndCourse.objects.create(user_id=request.user.id,course_id=course_id,can_watch=can_watch)
    return Result.ok() if usercourse else Result.error('操作失败')


@login_require
def getScores(request):
    scores = Score.objects.filter(user_id=request.user.id)
    return JsonResponse({
        'data': [s.to_dict() for s in scores]
    }, safe=False)