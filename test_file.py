import subprocess
import json
import re

ARGS = ["ask", "simulate", "-t", "", "-l", "en-US", "-s", "amzn1.ask.skill.803026db-ece4-4bd3-b64d-ee74fcf21466"]


def get_response_from_skill(input_speech):
    ARGS[3] = input_speech
    output = subprocess.run(ARGS, shell=True, stdout=subprocess.PIPE)
    output_str = str(output.stdout)
    start_index_of_json = output_str.find('{')
    if start_index_of_json is not -1:
        samp = output_str[start_index_of_json:len(output_str) - 1].replace('\\n', "").replace('\\', "")
        j = json.loads(samp)
        return j["result"]["skillExecutionInfo"]["invocations"][0]["invocationResponse"]["body"]["response"]["outputSpeech"]["ssml"]
    return ""


def call_exit_to_make_sure_no_session_active():
    ARGS[3] = "exit"
    subprocess.run(ARGS, shell=True, stdout=subprocess.PIPE)


def test_launch_henry():
    test_name = "Test Launch Henry"
    response = get_response_from_skill("open henry")
    if re.match(r"<speak>Hello, welcome .*</speak>\Z", response):
        print("{} PASSED".format(test_name))
    else:
        print("{} FAILED".format(test_name))
        print("Returned response: ", response)


def test_update_name():
    test_name = "Test Update Name"
    response = get_response_from_skill("call me harry")
    if re.match(r"<speak>Okay, I will call you .* from now on</speak>\Z", response):
        print("{} PASSED".format(test_name))
    else:
        print("{} FAILED".format(test_name))
        print("Returned response: ", response)


def test_end_skill():
    test_name = "Test Exit Skill"
    response = get_response_from_skill("goodbye")
    if re.match(r"<speak>Sorry, there was some problem. Please try again!!</speak>\Z", response):
        print("{} FAILED".format(test_name))
        print("Expected a goodbye but got: ", response)
    else:
        print("{} PASSED".format(test_name), end=" ")
        print("-- Response was: ", response)


def test_add_goal_and_list_goals():
    test_name = "Test Add Goal and List Goals"
    response = get_response_from_skill("i want to go swim")
    response2 = get_response_from_skill("List my goals")
    if re.match(r"<speak>Sure I'll remember that!</speak>", response):
        if re.match(r"<speak>Your goals? .* go swim</speak>\Z", response2):
            print("{} PASSED".format(test_name))
        else:
            print("{} FAILED".format(test_name))
            print("List goals returned: ", response2)
    else:
        print("{} FAILED".format(test_name))
        print("Adding goal returned: ", response)


def test_get_advice_about_love():
    test_name = "Test Get Advice About Love"
    response = get_response_from_skill("give me advice about love")
    if re.match(r"<speak>Sorry, there was some problem. Please try again!!</speak>\Z", response):
        print("{} FAILED".format(test_name))
        print("Expected advice about love but got: ", response)
    else:
        print("{} PASSED".format(test_name), end=" ")
        print("-- Response was: ", response)


if __name__ == '__main__':
    call_exit_to_make_sure_no_session_active()
    test_launch_henry()
    test_update_name()
    test_add_goal_and_list_goals()
    test_get_advice_about_love()
    test_end_skill()
