from . import rest_url
from bugsy import (Bugsy, Bug)
from bugsy.errors import (BugsyException, LoginException)

import responses
import json

example_return = {'faults': [], 'bugs': [{'cf_tracking_firefox29': '---', 'classification': 'Other', 'creator': 'jgriffin@mozilla.com', 'cf_status_firefox30':
'---', 'depends_on': [], 'cf_status_firefox32': '---', 'creation_time': '2014-05-28T23:57:58Z', 'product': 'Release Engineering', 'cf_user_story': '', 'dupe_of': None, 'cf_tracking_firefox_relnote': '---', 'keywords': [], 'cf_tracking_b2g18': '---', 'summary': 'Schedule Mn tests on o\
pt Linux builds on cedar', 'id': 1017315, 'assigned_to_detail': {'id': 347295, 'email': 'jgriffin@mozilla.com', 'name': 'jgriffin@mozilla.com',
'real_name': 'Jonathan Griffin (:jgriffin)'}, 'severity': 'normal', 'is_confirmed': True, 'is_creator_accessible': True, 'cf_status_b2g_1_1_hd':
 '---', 'qa_contact_detail': {'id': 20203, 'email': 'catlee@mozilla.com', 'name': 'catlee@mozilla.com', 'real_name': 'Chris AtLee [:catlee]'},
 'priority': '--', 'platform': 'All', 'cf_crash_signature': '', 'version': 'unspecified', 'cf_qa_whiteboard': '', 'cf_status_b2g_1_3t': '--\
-', 'cf_status_firefox31': '---', 'is_open': False, 'cf_blocking_fx': '---', 'status': 'RESOLVED', 'cf_tracking_relnote_b2g': '---', 'cf_stat\
us_firefox29': '---', 'blocks': [], 'qa_contact': 'catlee@mozilla.com', 'see_also': [], 'component': 'General Automation', 'cf_tracking_firefox\
32': '---', 'cf_tracking_firefox31': '---', 'cf_tracking_firefox30': '---', 'op_sys': 'All', 'groups': [], 'cf_blocking_b2g': '---', 'target\
_milestone': '---', 'is_cc_accessible': True, 'cf_tracking_firefox_esr24': '---', 'cf_status_b2g_1_2': '---', 'cf_status_b2g_1_3': '---', 'cf_\
status_b2g18': '---', 'cf_status_b2g_1_4': '---', 'url': '', 'creator_detail': {'id': 347295, 'email': 'jgriffin@mozilla.com', 'name': 'jgri\
ffin@mozilla.com', 'real_name': 'Jonathan Griffin (:jgriffin)'}, 'whiteboard': '', 'cf_status_b2g_2_0': '---', 'cc_detail': [{'id': 30066, 'em\
ail': 'coop@mozilla.com', 'name': 'coop@mozilla.com', 'real_name': 'Chris Cooper [:coop]'}, {'id': 397261, 'email': 'dburns@mozilla.com', 'nam\
e': 'dburns@mozilla.com', 'real_name': 'David Burns :automatedtester'}, {'id': 438921, 'email': 'jlund@mozilla.com', 'name': 'jlund@mozilla.com ', 'real_name': 'Jordan Lund (:jlund)'}, {'id': 418814, 'email': 'mdas@mozilla.com', 'name': 'mdas@mozilla.com', 'real_name': 'Malini Das [:md\
as]'}], 'alias': None, 'cf_tracking_b2g_v1_2': '---', 'cf_tracking_b2g_v1_3': '---', 'flags': [], 'assigned_to': 'jgriffin@mozilla.com', 'cf_s\
tatus_firefox_esr24': '---', 'resolution': 'FIXED', 'last_change_time': '2014-05-30T21:20:17Z', 'cc': ['coop@mozilla.com', 'dburns@mozilla.com'
, 'jlund@mozilla.com', 'mdas@mozilla.com'], 'cf_blocking_fennec': '---'}]}

def test_we_cant_post_without_a_username_or_password():
    bugzilla = Bugsy()
    try:
        bugzilla.put("foo")
        assert 1 == 0, "Should have thrown when calling put"
    except BugsyException as e:
        assert str(e) == "Message: Unfortunately you can't put bugs in Bugzilla without credentials Code: None"

@responses.activate
def test_we_get_a_login_exception_when_details_are_wrong():
    responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                      body='{"message": "The username or password you entered is not valid."}', status=400,
                      content_type='application/json', match_querystring=True)
    try:
        Bugsy("foo", "bar")
        assert 1 == 0, "Should have thrown an error"
    except LoginException as e:
        assert str(e) == "Message: The username or password you entered is not valid. Code: None"
        assert responses.calls[0].request.headers['X-Bugzilla-Login'] == 'foo'
        assert (responses.calls[0].request.headers['X-Bugzilla-Password'] ==
                'bar')

@responses.activate
def test_bad_api_key():
    responses.add(responses.GET,
                  'https://bugzilla.mozilla.org/rest/valid_login?login=foo',
                  body='{"documentation":"http://www.bugzilla.org/docs/tip/en/html/api/","error":true,"code":306,"message":"The API key you specified is invalid. Please check that you typed it correctly."}',
                  status=400,
                  content_type='application/json', match_querystring=True)
    try:
        Bugsy(username='foo', api_key='badkey')
        assert False, 'Should have thrown'
    except LoginException as e:
        assert str(e) == 'Message: The API key you specified is invalid. Please check that you typed it correctly. Code: 306'
    assert (responses.calls[0].request.headers['X-Bugzilla-API-Key'] ==
            'badkey')

@responses.activate
def test_validate_api_key():
    responses.add(responses.GET,
                  'https://bugzilla.mozilla.org/rest/valid_login?login=foo',
                  body='true', status=200, content_type='application/json',
                  match_querystring=True)
    Bugsy(username='foo', api_key='goodkey')
    assert (responses.calls[0].request.headers['X-Bugzilla-API-Key'] ==
            'goodkey')

@responses.activate
def test_we_cant_post_without_passing_a_bug_object():
    responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                      body='{"token": "foobar"}', status=200,
                      content_type='application/json', match_querystring=True)
    bugzilla = Bugsy("foo", "bar")
    try:
        bugzilla.put("foo")
        assert 1 == 0, "Should have thrown an error about type when calling put"
    except BugsyException as e:
        assert str(e) == "Message: Please pass in a Bug object when posting to Bugzilla Code: None"

@responses.activate
def test_we_can_get_a_bug():
    responses.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(example_return), status=200,
                      content_type='application/json', match_querystring=True)
    bugzilla = Bugsy()
    bug = bugzilla.get(1017315)
    assert bug.id == 1017315
    assert bug.status == 'RESOLVED'
    assert bug.summary == 'Schedule Mn tests on opt Linux builds on cedar'

@responses.activate
def test_we_can_get_a_bug_with_login_token():
  responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                        body='{"token": "foobar"}', status=200,
                        content_type='application/json', match_querystring=True)
  responses.add(responses.GET, rest_url('bug', 1017315),
                    body=json.dumps(example_return), status=200,
                    content_type='application/json', match_querystring=True)
  bugzilla = Bugsy("foo", "bar")
  bug = bugzilla.get(1017315)
  assert bug.id == 1017315
  assert bug.status == 'RESOLVED'
  assert bug.summary == 'Schedule Mn tests on opt Linux builds on cedar'
  assert responses.calls[1].request.headers['X-Bugzilla-Token'] == 'foobar'

@responses.activate
def test_we_can_get_username_with_userid_cookie():
  responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/user/1234',
                        body='{"users": [{"name": "user@example.com"}]}', status=200,
                        content_type='application/json', match_querystring=True)

  bugzilla = Bugsy(userid='1234', cookie='abcd')
  assert bugzilla.username == 'user@example.com'
  assert responses.calls[0].request.headers['X-Bugzilla-Token'] == '1234-abcd'

@responses.activate
def test_we_can_create_a_new_remote_bug():
    bug = Bug()
    bug.summary = "I like foo"
    responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                      body='{"token": "foobar"}', status=200,
                      content_type='application/json', match_querystring=True)
    bug_dict = bug.to_dict().copy()
    bug_dict['id'] = 123123
    responses.add(responses.POST, 'https://bugzilla.mozilla.org/rest/bug',
                      body=json.dumps(bug_dict), status=200,
                      content_type='application/json')
    bugzilla = Bugsy("foo", "bar")
    bugzilla.put(bug)
    assert bug.id != None

@responses.activate
def test_we_can_put_a_current_bug():
    responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                      body='{"token": "foobar"}', status=200,
                      content_type='application/json', match_querystring=True)
    bug_dict = example_return.copy()
    bug_dict['summary'] = 'I love foo but hate bar'
    responses.add(responses.PUT, 'https://bugzilla.mozilla.org/rest/bug/1017315',
                      body=json.dumps(bug_dict), status=200,
                      content_type='application/json')
    responses.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(example_return), status=200,
                      content_type='application/json', match_querystring=True)
    bugzilla = Bugsy("foo", "bar")
    bug = Bug(**example_return['bugs'][0])
    bug.summary = 'I love foo but hate bar'
    bug.assigned_to = "automatedtester@mozilla.com"

    bugzilla.put(bug)
    assert bug.summary == 'I love foo but hate bar'
    assert bug.assigned_to == "automatedtester@mozilla.com"

@responses.activate
def test_we_handle_errors_from_bugzilla_when_posting():
  responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                    body='{"token": "foobar"}', status=200,
                    content_type='application/json', match_querystring=True)
  responses.add(responses.POST, 'https://bugzilla.mozilla.org/rest/bug',
                    body='{"error":true,"code":50,"message":"You must select/enter a component."}', status=400,
                    content_type='application/json')

  bugzilla = Bugsy("foo", "bar")
  bug = Bug()
  try:
      bugzilla.put(bug)
      assert 1 == 0, "Put should have raised an error"
  except BugsyException as e:
      assert str(e) == "Message: You must select/enter a component. Code: 50"

@responses.activate
def test_we_handle_errors_from_bugzilla_when_updating_a_bug():
  responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                    body='{"token": "foobar"}', status=200,
                    content_type='application/json', match_querystring=True)
  responses.add(responses.PUT, 'https://bugzilla.mozilla.org/rest/bug/1017315',
                    body='{"error":true,"code":50,"message":"You must select/enter a component."}', status=400,
                    content_type='application/json')
  bugzilla = Bugsy("foo", "bar")

  bug_dict = example_return.copy()
  bug_dict['summary'] = 'I love foo but hate bar'
  bug = Bug(**bug_dict['bugs'][0])
  try:
      bugzilla.put(bug)
  except BugsyException as e:
      assert str(e) == "Message: You must select/enter a component. Code: 50"

@responses.activate
def test_we_can_set_the_user_agent_to_bugsy():
  responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                    body='{"token": "foobar"}', status=200,
                    content_type='application/json', match_querystring=True)
  Bugsy("foo", "bar")
  assert responses.calls[0].request.headers['User-Agent'] == "Bugsy"

@responses.activate
def test_we_can_handle_errors_when_retrieving_bugs():
    error_response = {
    "code" : 101,
    "documentation" : "http://www.bugzilla.org/docs/tip/en/html/api/",
    "error" : True,
    "message" : "Bug 111111111111 does not exist."
    }
    responses.add(responses.GET, rest_url('bug', 111111111),
                      body=json.dumps(error_response), status=404,
                      content_type='application/json', match_querystring=True)
    bugzilla = Bugsy()
    try:
        bug = bugzilla.get(111111111)
        assert False, "A BugsyException should have been thrown"
    except BugsyException as e:
        assert str(e) == "Message: Bug 111111111111 does not exist. Code: 101"
    except Exception as e:
        assert False, "Wrong type of exception was thrown"

def test_we_can_know_when_bugsy_is_not_authenticated():
    bugzilla = Bugsy()
    assert not bugzilla.authenticated

@responses.activate
def test_we_can_know_when_bugsy_is_authenticated_using_password():
    responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                    body='{"token": "foobar"}', status=200,
                    content_type='application/json', match_querystring=True)
    bugzilla = Bugsy("foo", "bar")
    assert bugzilla.authenticated

@responses.activate
def test_we_can_know_when_bugsy_is_authenticated_using_apikey():
    responses.add(responses.GET,
                  'https://bugzilla.mozilla.org/rest/valid_login?login=foo',
                  body='true', status=200, content_type='application/json',
                  match_querystring=True)
    bugzilla = Bugsy(username='foo', api_key='goodkey')
    assert bugzilla.authenticated
