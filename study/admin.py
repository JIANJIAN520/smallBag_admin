from django.contrib import admin
import pdb
import types
from .models import User,Course,Teacher,Like,Comment,Order,UserAndCourse,Chapter,Problem,Option,Solution,UserAndProblem,Score
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone','is_student','image')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('teacher','name', 'subject','grade','price','description','date')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'sex','education','teaching_age','teach_code','picture','description')
    def render_change_form(self, request, context, *args, **kwargs):
         context['adminform'].form.fields['user'].queryset = User.objects.filter(is_student=False)
         return super(TeacherAdmin, self).render_change_form(request, context, *args, **kwargs)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'course','is_like')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course','content','date')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'course','date','is_pay')


@admin.register(UserAndCourse)
class UserAndCourseAdmin(admin.ModelAdmin):
    list_display = ('user', 'course','can_watch')



@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('course', 'name','video','description')


class OptionsInline(admin.TabularInline):
    model = Option
    extra = 0

class SolutionInline(admin.TabularInline):
    model = Solution
    extra = 0

class OptionsInlineInline(OptionsInline):
    pass

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'chapter')
    inlines = [OptionsInlineInline, SolutionInline]
    def get_inline_instances(self, request, obj=None):
        obj_id = request.resolver_match.kwargs['object_id']

        def get_queryset(_self, request):
            return super(OptionsInlineInline, _self).get_queryset(request).filter(problem_id=obj_id)

        inlines = []
        for inline_class in self.inlines:
            inline = inline_class(self.model, self.admin_site)
            if inline_class is OptionsInlineInline:
                inline.get_queryset = types.MethodType(get_queryset, inline)
                inline.queryset = inline.get_queryset(request).filter(problem_id=obj_id)
            inlines.append(inline)
        return inlines


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('problem', 'title')


@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = ('problem', 'option')


@admin.register(UserAndProblem)
class UserAndProblemAdmin(admin.ModelAdmin):
    list_display = ('problem', 'option','user','answered')


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('score', 'chapter','user','datetime')
