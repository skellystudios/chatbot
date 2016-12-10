import fileinput

class UtteranceNotMatchedException(Exception):
    pass

class Bot():

    states_by_name = dict()
    interactions_by_name = dict()

    context = {
        "interaction_stack": [],
        "state": None
    }

    default_interaction = None

    def set_default_interaction(self, interaction):
        self.default_interaction = interaction

    def get_state_by_name(self, name):
        return self.states_by_name.get(name)

    def get_interaction_by_name(self, name):
        return interactions_by_name.get(name)

    def get_utterance(self):
        return raw_input()
        #return fileinput.input()

    def register(self, class_):
        print "Registering"
        print class_
        if issubclass(class_, State):
            print "Registered state"
            name = class_.name
            self.states_by_name[name] = class_
        if issubclass(class_, Interaction):
            print "Registered interaction"
            name = class_.name
            self.interactions_by_name[name] = class_

    def get_current_state(self, context):
        state_name = self.context['state']
        state_class = self.get_state_by_name(state_name)
        state = state_class(context)
        return state

    def set_current_state(self, state):
        self.context['state'] = state.name

    def get_context(self):
        return self.context

    def set_context(self, context):
        self.context = context

    def send_response(self, response):
        if response:
            print response

    def run_loop(self):
        utterance = self.get_utterance()
        context = self.get_context()
        state = self.get_current_state(context)
        try:
            response, new_state, context = state.process_utterance(utterance)
            self.send_response(response)
        except UtteranceNotMatchedException:
            self.send_response("Sorry, I didn't get that. Try again")
            return

        self.send_response(new_state.initial_response)
        if new_state(context).is_terminal and self.context['interaction_stack']:
            """
            Find what interaction we were on, pass it the terminal state
            and the new context, and let it decide how it should end
            """
            interaction_name = self.context['interaction_stack'].pop()
            interaction_class = self.get_interaction_by_name(interaction_name)
            inteaction = interaction_class(context)
            response, new_state, updated_context = \
                interaction.complete_interaction(new_state)
            self.send_response(response)
            context = updated_context

        current_state = new_state
        self.send_response(current_state.initial_response)
        self.set_current_state(current_state)
        self.set_context(context)

class Interaction(object):
    """
    Represents an interaction between the bot and the user, such as selecting
    a locum
    """

    name = None
    initial_response = None
    initial_state = None
    final_response = None
    launch_intent = None

    def __init__(self, context):
        self.context = context

    def launch(self):
        """
        Effectively "runs" the interaction until the interaction terminates
        at which point it returns to
        """
        self.context.interaction_stack.append(name)
        return initial_response, initial_state, self.context

    def complete_interaction(new_state):
        """
        End the interaction, and optionally pass on to a specific state.
        If not, then it passes up the interaction stack
        """
        return final_response, None, self.context



class State(object):
    """
    Represents the bot's understanding of where it is in the conversation.
    For instance, if it just asked you a yes/no question then it's in the state
    of waiting for a yes or no answer
    """

    initial_response = None
    expected_intents = []
    is_terminal = False

    # Transition map is a mapping from intent to (response, next state)
    transition_map = dict()

    def __init__(self, context):
        self.context = context

    def process_utterance(self, utterance):
        """
        Take an utterance from a user and try to work out if it fits one of the
        intents. Then work out where to go from there.

        Returns response, the next state, and updated context.
        """
        matches = [intent().match(utterance) for intent in self.expected_intents]
        matches = filter(lambda x: x.is_matched(), matches)
        if not matches:
            raise UtteranceNotMatchedException
        matched_intent = matches[0] # Later, we could choose the most specific match
        for key, val in matched_intent.vars:
            self.context[key] = val
        response, next_state = self.get_transition(matched_intent)
        return response, next_state, self.context

    def get_transition(self, intent):
        return self.transition_map[intent.__class__]


class Intent(object):

    matched = False
    vars = dict()
    strings = []

    def match(self, utterance):
        """
        Matches what a user is saying (an utterance) with what they're trying
        to communicate with that utterance (their intent)
        """
        if utterance in self.strings:
            self.matched = True
        return self

    def is_matched(self):
        return self.matched
