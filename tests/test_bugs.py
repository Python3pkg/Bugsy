import datetime
import responses
import json

from . import rest_url
from bugsy import Bugsy, Bug
from bugsy.errors import (BugsyException, BugException)

example_return = {'faults': [], 'bugs': [{'cf_tracking_firefox29': '---', 'classification': 'Other', 'creator': 'jgriffin@mozilla.com', 'cf_status_firefox30':
'---', 'depends_on': [123456], 'cf_status_firefox32': '---', 'creation_time': '2014-05-28T23:57:58Z', 'product': 'Release Engineering', 'cf_user_story': '', 'dupe_of': None, 'cf_tracking_firefox_relnote': '---', 'keywords': ['regression'], 'cf_tracking_b2g18': '---', 'summary': 'Schedule Mn tests on o\
pt Linux builds on cedar', 'id': 1017315, 'assigned_to_detail': {'id': 347295, 'email': 'jgriffin@mozilla.com', 'name': 'jgriffin@mozilla.com',
'real_name': 'Jonathan Griffin (:jgriffin)'}, 'severity': 'normal', 'is_confirmed': True, 'is_creator_accessible': True, 'cf_status_b2g_1_1_hd':
 '---', 'qa_contact_detail': {'id': 20203, 'email': 'catlee@mozilla.com', 'name': 'catlee@mozilla.com', 'real_name': 'Chris AtLee [:catlee]'},
 'priority': '--', 'platform': 'All', 'cf_crash_signature': '', 'version': 'unspecified', 'cf_qa_whiteboard': '', 'cf_status_b2g_1_3t': '--\
-', 'cf_status_firefox31': '---', 'is_open': False, 'cf_blocking_fx': '---', 'status': 'RESOLVED', 'cf_tracking_relnote_b2g': '---', 'cf_stat\
us_firefox29': '---', 'blocks': [654321], 'qa_contact': 'catlee@mozilla.com', 'see_also': [], 'component': 'General Automation', 'cf_tracking_firefox\
32': '---', 'cf_tracking_firefox31': '---', 'cf_tracking_firefox30': '---', 'op_sys': 'All', 'groups': [], 'cf_blocking_b2g': '---', 'target\
_milestone': '---', 'is_cc_accessible': True, 'cf_tracking_firefox_esr24': '---', 'cf_status_b2g_1_2': '---', 'cf_status_b2g_1_3': '---', 'cf_\
status_b2g18': '---', 'cf_status_b2g_1_4': '---', 'url': '', 'creator_detail': {'id': 347295, 'email': 'jgriffin@mozilla.com', 'name': 'jgri\
ffin@mozilla.com', 'real_name': 'Jonathan Griffin (:jgriffin)'}, 'whiteboard': '', 'cf_status_b2g_2_0': '---', 'cc_detail': [{'id': 30066, 'em\
ail': 'coop@mozilla.com', 'name': 'coop@mozilla.com', 'real_name': 'Chris Cooper [:coop]'}, {'id': 397261, 'email': 'dburns@mozilla.com', 'nam\
e': 'dburns@mozilla.com', 'real_name': 'David Burns :automatedtester'}, {'id': 438921, 'email': 'jlund@mozilla.com', 'name': 'jlund@mozilla.com ', 'real_name': 'Jordan Lund (:jlund)'}, {'id': 418814, 'email': 'mdas@mozilla.com', 'name': 'mdas@mozilla.com', 'real_name': 'Malini Das [:md\
as]'}], 'alias': None, 'cf_tracking_b2g_v1_2': '---', 'cf_tracking_b2g_v1_3': '---', 'flags': [], 'assigned_to': 'jgriffin@mozilla.com', 'cf_s\
tatus_firefox_esr24': '---', 'resolution': 'FIXED', 'last_change_time': '2014-05-30T21:20:17Z', 'cc': ['coop@mozilla.com', 'dburns@mozilla.com'
, 'jlund@mozilla.com', 'mdas@mozilla.com'], 'cf_blocking_fennec': '---'}]}

comments_return = {
    'bugs': {
        '1017315': {
            'comments': [
                {
                   'attachment_id': None,
                   'author': 'gps@mozilla.com',
                   'bug_id': 1017315,
                   'creation_time': '2014-03-27T23:47:45Z',
                   'creator': 'gps@mozilla.com',
                   'id': 8589785,
                   'is_private': False,
                   'raw_text': 'raw text 1',
                   'tags': ['tag1', 'tag2'],
                   'text': 'text 1',
                   'time': '2014-03-27T23:47:45Z'
                },
                {
                   'attachment_id': 8398207,
                   'author': 'gps@mozilla.com',
                   'bug_id': 1017315,
                   'creation_time': '2014-03-27T23:56:34Z',
                   'creator': 'gps@mozilla.com',
                   'id': 8589812,
                   'is_private': True,
                   'raw_text': 'raw text 2',
                   'tags': [],
                   'text': 'text 2',
                   'time': '2014-03-27T23:56:34Z'
                },
            ],
        },
    },
}

def test_can_create_bug_and_set_summary_afterwards():
    bug = Bug()
    assert bug.id == None, "Id has been set"
    assert bug.summary == '', "Summary is not set to nothing on plain initialisation"
    bug.summary = "Foo"
    assert bug.summary == 'Foo', "Summary is not being set"
    assert bug.status == '', 'Status has been set'

def test_we_cant_set_status_unless_there_is_a_bug_id():
    bug = Bug()
    try:
        bug.status = 'RESOLVED'
    except BugException as e:
        assert str(e) == "Message: Can not set status unless there is a bug id. Please call Update() before setting Code: None"

def test_we_can_get_OS_set_from_default():
    bug = Bug()
    assert bug.OS == "All"

def test_we_can_get_OS_we_set():
    bug = Bug(op_sys="Linux")
    assert bug.OS == "Linux"

def test_we_can_get_Product_set_from_default():
    bug = Bug()
    assert bug.product == "core"

def test_we_can_get_get_the_keywords():
    bug = Bug(**example_return['bugs'][0])
    keywords = bug.keywords
    assert ['regression'] == keywords

@responses.activate
def test_we_can_add_single_keyword():
    bug = None
    bugzilla = None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                          body='{"token": "foobar"}', status=200,
                          content_type='application/json', match_querystring=True)
        rsps.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(example_return), status=200,
                      content_type='application/json', match_querystring=True)
        bugzilla = Bugsy("foo", "bar")
        bug = bugzilla.get(1017315)
    import copy
    bug_dict = copy.deepcopy(example_return)
    bug_dict['bugs'][0]['keywords'].append("ateam-marionette-server")

    updated_bug = None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.PUT, 'https://bugzilla.mozilla.org/rest/bug/1017315',
                    body=json.dumps(bug_dict), status=200,
                    content_type='application/json', match_querystring=True)

        rsps.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(bug_dict), status=200,
                      content_type='application/json', match_querystring=True)

        bug.keywords = "ateam-marionette-server"
        updated_bug = bugzilla.put(bug)

    keywords = updated_bug.keywords
    assert isinstance(keywords, list)
    assert ["regression", "ateam-marionette-server"] == keywords

@responses.activate
def test_we_can_add_multiple_keywords_to_list():
    bug = None
    bugzilla = None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                          body='{"token": "foobar"}', status=200,
                          content_type='application/json', match_querystring=True)
        rsps.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(example_return), status=200,
                      content_type='application/json', match_querystring=True)
        bugzilla = Bugsy("foo", "bar")
        bug = bugzilla.get(1017315)
    import copy
    bug_dict = copy.deepcopy(example_return)
    bug_dict['bugs'][0]['keywords'].append("intermittent")
    bug_dict['bugs'][0]['keywords'].append("ateam-marionette-server")

    updated_bug = None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.PUT, 'https://bugzilla.mozilla.org/rest/bug/1017315',
                    body=json.dumps(bug_dict), status=200,
                    content_type='application/json', match_querystring=True)

        rsps.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(bug_dict), status=200,
                      content_type='application/json', match_querystring=True)

        bug.keywords = ["intermittent", "ateam-marionette-server"]
        updated_bug = bugzilla.put(bug)

    keywords = updated_bug.keywords
    assert isinstance(keywords, list)
    assert ["regression", "intermittent", "ateam-marionette-server"] == keywords

@responses.activate
def test_we_can_add_remove_a_keyword_list():
    bug = None
    bugzilla = None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                          body='{"token": "foobar"}', status=200,
                          content_type='application/json', match_querystring=True)
        rsps.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(example_return), status=200,
                      content_type='application/json', match_querystring=True)

        bugzilla = Bugsy("foo", "bar")
        bug = bugzilla.get(1017315)
    import copy
    bug_dict = copy.deepcopy(example_return)
    bug_dict['bugs'][0]['keywords'].remove("regression")

    updated_bug = None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.PUT, 'https://bugzilla.mozilla.org/rest/bug/1017315',
                    body=json.dumps(bug_dict), status=200,
                    content_type='application/json', match_querystring=True)

        rsps.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(bug_dict), status=200,
                      content_type='application/json', match_querystring=True)

        bug.keyword = ["regression-"]
        updated_bug = bugzilla.put(bug)

    keywords = updated_bug.keywords
    assert isinstance(keywords, list)
    assert [] == keywords

def test_we_can_get_Product_we_set():
    bug = Bug(product="firefox")
    assert bug.product == "firefox"

def test_we_can_get_get_cc_list():
    bug = Bug(**example_return['bugs'][0])
    cced = bug.cc
    assert isinstance(cced, list)
    assert ["coop@mozilla.com", "dburns@mozilla.com",
            "jlund@mozilla.com", "mdas@mozilla.com"] == cced

@responses.activate
def test_we_can_add_single_email_to_cc_list():
    bug = None
    bugzilla = None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                          body='{"token": "foobar"}', status=200,
                          content_type='application/json', match_querystring=True)
        rsps.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(example_return), status=200,
                      content_type='application/json', match_querystring=True)
        bugzilla = Bugsy("foo", "bar")
        bug = bugzilla.get(1017315)
    import copy
    bug_dict = copy.deepcopy(example_return)
    bug_dict['bugs'][0]['cc_detail'].append({'id': 438921, 'email': 'automatedtester@mozilla.com',
                                'name': 'automatedtester@mozilla.com ', 'real_name': 'AutomatedTester'})

    updated_bug = None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.PUT, 'https://bugzilla.mozilla.org/rest/bug/1017315',
                    body=json.dumps(bug_dict), status=200,
                    content_type='application/json', match_querystring=True)

        rsps.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(bug_dict), status=200,
                      content_type='application/json', match_querystring=True)

        bug.cc = "automatedtester@mozilla.com"
        updated_bug = bugzilla.put(bug)

    cced = updated_bug.cc
    assert isinstance(cced, list)
    assert ["coop@mozilla.com", "dburns@mozilla.com",
            "jlund@mozilla.com", "mdas@mozilla.com",
            "automatedtester@mozilla.com"] == cced

@responses.activate
def test_we_can_add_multiple_emails_to_cc_list():
    bug = None
    bugzilla = None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                          body='{"token": "foobar"}', status=200,
                          content_type='application/json', match_querystring=True)
        rsps.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(example_return), status=200,
                      content_type='application/json', match_querystring=True)
        bugzilla = Bugsy("foo", "bar")
        bug = bugzilla.get(1017315)
    import copy
    bug_dict = copy.deepcopy(example_return)
    bug_dict['bugs'][0]['cc_detail'].append({'id': 438921, 'email': 'automatedtester@mozilla.com',
                                'name': 'automatedtester@mozilla.com ', 'real_name': 'AutomatedTester'})
    bug_dict['bugs'][0]['cc_detail'].append({'id': 438922, 'email': 'foobar@mozilla.com',
                                'name': 'foobar@mozilla.com ', 'real_name': 'Foobar'})

    updated_bug = None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.PUT, 'https://bugzilla.mozilla.org/rest/bug/1017315',
                    body=json.dumps(bug_dict), status=200,
                    content_type='application/json', match_querystring=True)

        rsps.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(bug_dict), status=200,
                      content_type='application/json', match_querystring=True)

        bug.cc = ["automatedtester@mozilla.com", "foobar@mozilla.com"]
        updated_bug = bugzilla.put(bug)

    cced = updated_bug.cc
    assert isinstance(cced, list)
    assert ["coop@mozilla.com", "dburns@mozilla.com",
            "jlund@mozilla.com", "mdas@mozilla.com",
            "automatedtester@mozilla.com", "foobar@mozilla.com"] == cced

@responses.activate
def test_we_can_add_remove_an_email_to_cc_list():
    bug = None
    bugzilla = None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                          body='{"token": "foobar"}', status=200,
                          content_type='application/json', match_querystring=True)
        rsps.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(example_return), status=200,
                      content_type='application/json', match_querystring=True)

        bugzilla = Bugsy("foo", "bar")
        bug = bugzilla.get(1017315)
    import copy
    bug_dict = copy.deepcopy(example_return)
    bug_dict['bugs'][0]['cc_detail'].remove([person for person in bug_dict['bugs'][0]['cc_detail'] if person['id'] == 397261][0])
    bug_dict['bugs'][0]['cc_detail'].append({'id': 438921, 'email': 'automatedtester@mozilla.com',
                                'name': 'automatedtester@mozilla.com ', 'real_name': 'AutomatedTester'})

    updated_bug = None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.PUT, 'https://bugzilla.mozilla.org/rest/bug/1017315',
                    body=json.dumps(bug_dict), status=200,
                    content_type='application/json', match_querystring=True)

        rsps.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(bug_dict), status=200,
                      content_type='application/json', match_querystring=True)

        bug.cc = ["automatedtester@mozilla.com", "dburns@mozilla.com-"]
        updated_bug = bugzilla.put(bug)

    cced = updated_bug.cc
    assert isinstance(cced, list)
    assert ["coop@mozilla.com", "jlund@mozilla.com",
            "mdas@mozilla.com", "automatedtester@mozilla.com"] == cced

@responses.activate
def test_we_can_remove_an_email_to_cc_list():
    bug = None
    bugzilla = None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                          body='{"token": "foobar"}', status=200,
                          content_type='application/json', match_querystring=True)
        rsps.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(example_return), status=200,
                      content_type='application/json', match_querystring=True)

        bugzilla = Bugsy("foo", "bar")
        bug = bugzilla.get(1017315)
    import copy
    bug_dict = copy.deepcopy(example_return)
    bug_dict['bugs'][0]['cc_detail'].remove([person for person in bug_dict['bugs'][0]['cc_detail'] if person['id'] == 397261][0])
    bug_dict['bugs'][0]['cc_detail'].remove([person for person in bug_dict['bugs'][0]['cc_detail'] if person['id'] == 418814][0])

    updated_bug = None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.PUT, 'https://bugzilla.mozilla.org/rest/bug/1017315',
                    body=json.dumps(bug_dict), status=200,
                    content_type='application/json', match_querystring=True)

        rsps.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(bug_dict), status=200,
                      content_type='application/json', match_querystring=True)

        bug.cc = ["automatedtester@mozilla.com", "dburns@mozilla.com-"]
        updated_bug = bugzilla.put(bug)

    cced = updated_bug.cc
    assert isinstance(cced, list)
    assert ["coop@mozilla.com", "jlund@mozilla.com"] == cced

def test_we_throw_an_error_for_invalid_status_types():
    bug = Bug(**example_return['bugs'][0])
    try:
        bug.status = "foo"
        assert 1 == 0, "Should have thrown an error about invalid type"
    except BugException as e:
        assert str(e) == "Message: Invalid status type was used Code: None"

def test_we_can_get_the_resolution():
    bug = Bug(**example_return['bugs'][0])
    assert "FIXED" == bug.resolution

def test_we_can_set_the_resolution():
    bug = Bug(**example_return['bugs'][0])
    bug.resolution = 'INVALID'
    assert bug.resolution == 'INVALID'

def test_we_cant_set_the_resolution_when_not_valid():
    bug = Bug(**example_return['bugs'][0])
    try:
        bug.resolution = 'FOO'
        assert 1==0, "Should thrown an error"
    except BugException as e:
        assert str(e) == "Message: Invalid resolution type was used Code: None"

def test_we_can_pass_in_dict_and_get_a_bug():
    bug = Bug(**example_return['bugs'][0])
    assert bug.id == 1017315
    assert bug.status == 'RESOLVED'
    assert bug.summary == 'Schedule Mn tests on opt Linux builds on cedar'
    assert bug.assigned_to == "jgriffin@mozilla.com"

def test_we_can_get_a_dict_version_of_the_bug():
    bug = Bug(**example_return['bugs'][0])
    result = bug.to_dict()
    assert example_return['bugs'][0]['id'] == result['id']

def test_we_can_get_depends_on_list():
    bug = Bug(**example_return['bugs'][0])
    depends_on = bug.depends_on
    assert isinstance(depends_on, list)
    assert depends_on == [123456]

@responses.activate
def test_we_can_add_and_remove_depends_on():
    bug = None
    bugzilla = None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                          body='{"token": "foobar"}', status=200,
                          content_type='application/json', match_querystring=True)
        rsps.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(example_return), status=200,
                      content_type='application/json', match_querystring=True)

        bugzilla = Bugsy("foo", "bar")
        bug = bugzilla.get(1017315)
    import copy
    bug_dict = copy.deepcopy(example_return)
    bug_dict['bugs'][0]['depends_on'].remove(123456)
    bug_dict['bugs'][0]['depends_on'].append(145123)

    updated_bug = None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.PUT, 'https://bugzilla.mozilla.org/rest/bug/1017315',
                    body=json.dumps(bug_dict), status=200,
                    content_type='application/json', match_querystring=True)

        rsps.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(bug_dict), status=200,
                      content_type='application/json', match_querystring=True)

        bug.depends_on = ["123456-", "145123"]
        updated_bug = bugzilla.put(bug)

    deps = updated_bug.depends_on
    assert isinstance(deps, list)
    assert [145123] == deps

def test_we_can_get_blocks_list():
    bug = Bug(**example_return['bugs'][0])
    blocks = bug.blocks
    assert isinstance(blocks, list)
    assert blocks == [654321]

@responses.activate
def test_we_can_add_and_remove_blocks():
    bug = None
    bugzilla = None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                          body='{"token": "foobar"}', status=200,
                          content_type='application/json', match_querystring=True)
        rsps.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(example_return), status=200,
                      content_type='application/json', match_querystring=True)

        bugzilla = Bugsy("foo", "bar")
        bug = bugzilla.get(1017315)
    import copy
    bug_dict = copy.deepcopy(example_return)
    bug_dict['bugs'][0]['blocks'].remove(654321)
    bug_dict['bugs'][0]['blocks'].append(145123)

    updated_bug = None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.PUT, 'https://bugzilla.mozilla.org/rest/bug/1017315',
                    body=json.dumps(bug_dict), status=200,
                    content_type='application/json', match_querystring=True)

        rsps.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(bug_dict), status=200,
                      content_type='application/json', match_querystring=True)

        bug.blocks = ["654321-", "145123"]
        updated_bug = bugzilla.put(bug)

    deps = updated_bug.blocks
    assert isinstance(deps, list)
    assert [145123] == deps

@responses.activate
def test_we_can_update_a_bug_from_bugzilla():
    responses.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(example_return), status=200,
                      content_type='application/json', match_querystring=True)
    bugzilla = Bugsy()
    bug = bugzilla.get(1017315)
    import copy
    bug_dict = copy.deepcopy(example_return)
    bug_dict['bugs'][0]['status'] = "REOPENED"
    responses.reset()
    responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/bug/1017315',
                      body=json.dumps(bug_dict), status=200,
                      content_type='application/json')
    bug.update()
    assert bug.status == 'REOPENED'

def test_we_cant_update_unless_we_have_a_bug_id():
    bug = Bug()
    try:
        bug.update()
    except BugException as e:
        assert str(e) == "Message: Unable to update bug that isn't in Bugzilla Code: None"

@responses.activate
def test_we_can_update_a_bug_with_login_token():
  responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                        body='{"token": "foobar"}', status=200,
                        content_type='application/json', match_querystring=True)

  responses.add(responses.GET, rest_url('bug', 1017315),
                    body=json.dumps(example_return), status=200,
                    content_type='application/json', match_querystring=True)
  bugzilla = Bugsy("foo", "bar")
  bug = bugzilla.get(1017315)
  import copy
  bug_dict = copy.deepcopy(example_return)
  bug_dict['bugs'][0]['status'] = "REOPENED"
  responses.reset()
  responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/bug/1017315',
                    body=json.dumps(bug_dict), status=200,
                    content_type='application/json', match_querystring=True)
  bug.update()
  assert bug.id == 1017315
  assert bug.status == 'REOPENED'
  assert bug.summary == 'Schedule Mn tests on opt Linux builds on cedar'

@responses.activate
def test_that_we_can_add_a_comment_to_a_bug_before_it_is_put():
    responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                          body='{"token": "foobar"}', status=200,
                          content_type='application/json', match_querystring=True)

    responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/bug/1017315?include_fields=version&include_fields=id&include_fields=summary&include_fields=status&include_fields=op_sys&include_fields=resolution&include_fields=product&include_fields=component&include_fields=platform',
                      body=json.dumps(example_return), status=200,
                      content_type='application/json', match_querystring=True)
    bugzilla = Bugsy("foo", "bar")
    bug = Bug()
    bug.summary = "I like cheese"
    bug.add_comment("I like sausages")

    bug_dict = bug.to_dict().copy()
    bug_dict['id'] = 123123

    responses.add(responses.POST, 'https://bugzilla.mozilla.org/rest/bug',
                      body=json.dumps(bug_dict), status=200,
                      content_type='application/json', match_querystring=True)
    bugzilla.put(bug)

@responses.activate
def test_that_we_can_add_a_comment_to_an_existing_bug():
    responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                          body='{"token": "foobar"}', status=200,
                          content_type='application/json', match_querystring=True)

    responses.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(example_return), status=200,
                      content_type='application/json', match_querystring=True)
    bugzilla = Bugsy("foo", "bar")
    bug = bugzilla.get(1017315)

    responses.add(responses.POST, 'https://bugzilla.mozilla.org/rest/bug/1017315/comment',
                      body=json.dumps({}), status=200,
                      content_type='application/json', match_querystring=True)

    bug.add_comment("I like sausages")

    assert len(responses.calls) == 3

@responses.activate
def test_comment_retrieval():
    responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                        body='{"token": "foobar"}', status=200,
                        content_type='application/json', match_querystring=True)
    responses.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(example_return), status=200,
                      content_type='application/json', match_querystring=True)
    responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/bug/1017315/comment',
                    body=json.dumps(comments_return), status=200,
                    content_type='application/json', match_querystring=True)

    bugzilla = Bugsy("foo", "bar")
    bug = bugzilla.get(1017315)
    comments = bug.get_comments()
    assert len(comments) == 2
    c1 = comments[0]
    assert c1.attachment_id is None
    assert c1.author == 'gps@mozilla.com'
    assert c1.bug_id == 1017315
    assert c1.creation_time == datetime.datetime(2014, 3, 27, 23, 47, 45)
    assert c1.creator == 'gps@mozilla.com'
    assert c1.id == 8589785
    assert c1.is_private is False
    assert c1.text == 'text 1'
    assert c1.tags == set(['tag1', 'tag2'])
    assert c1.time == datetime.datetime(2014, 3, 27, 23, 47, 45)

@responses.activate
def test_we_raise_an_exception_when_getting_comments_and_bugzilla_errors():
    responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                          body='{"token": "foobar"}', status=200,
                          content_type='application/json', match_querystring=True)

    responses.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(example_return), status=200,
                      content_type='application/json', match_querystring=True)
    bugzilla = Bugsy("foo", "bar")
    bug = bugzilla.get(1017315)

    error_response = {'code': 67399,
                      'message': "The requested method 'Bug.comments' was not found.",
                      'documentation': 'http://www.bugzilla.org/docs/tip/en/html/api/',
                       'error': True}

    responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/bug/1017315/comment',
                    body=json.dumps(error_response), status=400,
                    content_type='application/json', match_querystring=True)
    try:
        comments = bug.get_comments()
        assert False, "Should have raised an BugException for the bug not existing"
    except BugsyException as e:
        assert str(e) == "Message: The requested method 'Bug.comments' was not found. Code: 67399"

@responses.activate
def test_we_raise_an_exception_if_commenting_on_a_bug_that_returns_an_error():
    responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                          body='{"token": "foobar"}', status=200,
                          content_type='application/json', match_querystring=True)

    responses.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(example_return), status=200,
                      content_type='application/json', match_querystring=True)
    bugzilla = Bugsy("foo", "bar")
    bug = bugzilla.get(1017315)

    # will now return the following error. This could happen if the bug was open
    # when we did a `get()` but is now hidden
    error_response = {'code': 101,
                      'message': 'Bug 1017315 does not exist.',
                      'documentation': 'http://www.bugzilla.org/docs/tip/en/html/api/',
                      'error': True}
    responses.add(responses.POST, 'https://bugzilla.mozilla.org/rest/bug/1017315/comment',
                      body=json.dumps(error_response), status=404,
                      content_type='application/json', match_querystring=True)
    try:
        bug.add_comment("I like sausages")
        assert False, "Should have raised an BugException for the bug not existing"
    except BugsyException as e:
        assert str(e) == "Message: Bug 1017315 does not exist. Code: 101"

    assert len(responses.calls) == 3

@responses.activate
def test_we_can_add_tags_to_bug_comments():
    responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                          body='{"token": "foobar"}', status=200,
                          content_type='application/json', match_querystring=True)

    responses.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(example_return), status=200,
                      content_type='application/json', match_querystring=True)
    bugzilla = Bugsy("foo", "bar")
    bug = bugzilla.get(1017315)

    responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/bug/1017315/comment',
                    body=json.dumps(comments_return), status=200,
                    content_type='application/json', match_querystring=True)

    comments = bug.get_comments()

    responses.add(responses.PUT, 'https://bugzilla.mozilla.org/rest/bug/comment/8589785/tags',
                    body=json.dumps(["spam","foo"]), status=200,
                    content_type='application/json', match_querystring=True)
    comments[0].add_tags("foo")

    assert len(responses.calls) == 4

@responses.activate
def test_we_can_remove_tags_to_bug_comments():
    responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/login',
                          body='{"token": "foobar"}', status=200,
                          content_type='application/json', match_querystring=True)

    responses.add(responses.GET, rest_url('bug', 1017315),
                      body=json.dumps(example_return), status=200,
                      content_type='application/json', match_querystring=True)
    bugzilla = Bugsy("foo", "bar")
    bug = bugzilla.get(1017315)

    responses.add(responses.GET, 'https://bugzilla.mozilla.org/rest/bug/1017315/comment',
                    body=json.dumps(comments_return), status=200,
                    content_type='application/json', match_querystring=True)

    comments = bug.get_comments()

    responses.add(responses.PUT, 'https://bugzilla.mozilla.org/rest/bug/comment/8589785/tags',
                    body=json.dumps(["spam","foo"]), status=200,
                    content_type='application/json', match_querystring=True)
    comments[0].remove_tags("foo")

    assert len(responses.calls) == 4
