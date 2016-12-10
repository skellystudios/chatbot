from chatbot import Bot, State, Interaction, Intent


bot = Bot()

class YesIntent(Intent):
    strings = ["yes"]


class NoIntent(Intent):
    strings = ["no"]


class YesState(State):
    name = 'yes'
    is_terminal = True
    initial_response = "you said yes"
bot.register(YesState)


class NoState(State):
    name = 'no'
    is_terminal = True
    initial_response = "you said no"
bot.register(NoState)


class WaitingForYesNoState(State):
    name = 'waitingforyesno'
    expected_intents = [YesIntent, NoIntent]
    transition_map = {
        YesIntent: ("Thanks", YesState),
        NoIntent: ("Thanks", NoState)
    }
bot.register(WaitingForYesNoState)


class YesNoInteraction(Interaction):

    name = 'yesno'
    initial_response = "Yes or no?"
    initial_state = WaitingForYesNoState

    def launch(self, state_if_yes, state_if_no, custom_response):
        self.initial_response = custom_response or self.initial_response
        self.context[name]['state_if_yes'] = state_if_yes
        self.context[name]['state_if_no'] = state_if_no
        return super().launch()

    def complete_interaction(new_state):
        if isinstance(new_state, YesState):
            state = get_state_by_name(self.context[name]['state_if_yes'])
        elif isinstance(new_state, NoState):
            state = get_state_by_name(self.context[name]['state_if_no'])
        return

bot.register(YesNoInteraction)


class DefaultState(State):
    """
    This is a special state that checks each registered interaction's launch
    intent and then launches that interaction
    """

    def process_utterance(self, utterance):
        pass

class DefaultInteraction(Interaction):

    name = 'default'
    initial_response = "Welcome, I'm a bot"
    initial_state = DefaultState


class LameInteraction(Interaction):

    name = 'default'
    initial_response = "Are you lame"
    initial_state = DefaultState

    def launch(self):
        super().launch()
        return YesNoInteraction.launch()

    def complete_interaction(new_state):
        """
        End the interaction, and optionally pass on to a specific state.
        If not, then it passes up the interaction stack
        """
        return final_response, None, self.context



bot.run_loop()
