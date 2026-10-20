from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from .models import Course, Lesson, Question, Choice, Submission, Enrollment


class OnlineCourseAssessmentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('teststudent', 'test@example.com', 'password123')
        self.user.first_name = 'Test'
        self.user.save()

        self.course = Course.objects.create(
            name='Test Django Course',
            description='Test course description',
            pub_date=date.today(),
            total_enrollment=0
        )
        self.lesson = Lesson.objects.create(
            title='Test Lesson 1',
            order=0,
            course=self.course,
            content='Lesson content'
        )
        self.question = Question.objects.create(
            lesson=self.lesson,
            course=self.course,
            question_text='What is Django?',
            grade=10
        )
        self.c1 = Choice.objects.create(
            question=self.question,
            choice_text='A Python web framework',
            is_correct=True
        )
        self.c2 = Choice.objects.create(
            question=self.question,
            choice_text='A database',
            is_correct=False
        )

    def test_question_is_get_score_correct(self):
        """Test is_get_score returns True when correct choice is provided."""
        self.assertTrue(self.question.is_get_score([self.c1.id]))

    def test_question_is_get_score_incorrect(self):
        """Test is_get_score returns False when wrong choice is selected."""
        self.assertFalse(self.question.is_get_score([self.c2.id]))
        self.assertFalse(self.question.is_get_score([self.c1.id, self.c2.id]))

    def test_course_list_view(self):
        """Test CourseListView renders 200 OK."""
        response = self.client.get(reverse('onlinecourse:index'))
        self.assertEqual(response.status_code, 200)

    def test_course_detail_view(self):
        """Test CourseDetailView renders 200 OK."""
        response = self.client.get(reverse('onlinecourse:course_details', args=(self.course.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Django Course')

    def test_exam_submission_and_result(self):
        """Test submitting exam and viewing result."""
        self.client.login(username='teststudent', password='password123')
        submit_url = reverse('onlinecourse:submit', args=(self.course.id,))
        post_data = {
            f'choice_{self.c1.id}': self.c1.id
        }
        response = self.client.post(submit_url, post_data)
        self.assertEqual(response.status_code, 302)

        # Follow redirect to result page
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Congratulations')
        self.assertContains(response, '100/100')
