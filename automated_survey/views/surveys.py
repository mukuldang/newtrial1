from automated_survey.models import Survey
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from twilio import twiml


@require_GET
def show_survey_results(request, survey_id):
    survey = Survey.objects.get(id=survey_id)
    responses_to_render = [response.as_dict() for response in survey.responses]

    template_context = {
        'responses': responses_to_render,
        'survey_title': survey.title
    }

    return render_to_response('results.html', context=template_context)


@csrf_exempt
def show_survey(request, survey_id):
    survey = Survey.objects.get(id=survey_id)
    first_question = survey.first_question

    first_question_ids = {
        'survey_id': survey.id,
        'question_id': first_question.id
    }

    first_question_url = reverse('question', kwargs=first_question_ids)

    welcome = 'Hello and thank you for taking the %s survey' % survey.title
    twiml_response = twiml.Response()
    if request.is_sms:
        twiml_response.message(welcome)
    else:
        twiml_response.say(welcome)
    twiml_response.redirect(first_question_url, method='GET')

    return HttpResponse(twiml_response, content_type='application/xml')


@require_POST
def redirect_to_first_survey(request):
    first_survey = Survey.objects.first()
    first_survey_url = reverse('survey', kwargs={'survey_id': first_survey.id})
    return HttpResponseRedirect(first_survey_url)


@require_GET
def redirect_to_first_results(request):
    first_survey = Survey.objects.first()
    results_for_first_survey = reverse(
        'survey_results', kwargs={
            'survey_id': first_survey.id})
    return HttpResponseRedirect(results_for_first_survey)
