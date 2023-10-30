import asyncio
import shulker as mc
from dill import dumps
import requests
import json
import html

HOST = 'localhost:5000'
URI = f'http://{HOST}/api/v1/chat'

from tools.pulsar import Portal

class Template(Portal):
    async def on_join(self):
        await self.subscribe('voice.query_gpt', self.query_gpt)
        
        user_input = "0 players succeeded in finding the word 'theory' in the game, what should the gamemaster say to comfort them?"
        history = {'internal': [], 'visible': []}
        
        self.query_gpt(user_input, history)
    
    async def approve_sentence(self, sentence):
        approval = input(f"Approve sentence: {sentence} (enter/n)")
        
    def query_gpt(self, user_input, history=[]):
        request = {
            'user_input': user_input,
            'max_new_tokens': 250,
            'auto_max_new_tokens': False,
            'max_tokens_second': 0,
            'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
            'character': 'Gamemaster',  # Will get autodetected if unset
            'your_name': 'You',
            # 'name1': 'name of user', # Optional
            # 'name2': 'name of character', # Optional
            # 'context': 'character context', # Optional
            # 'greeting': 'greeting', # Optional
            # 'name1_instruct': 'You', # Optional
            # 'name2_instruct': 'Assistant', # Optional
            # 'context_instruct': 'context_instruct', # Optional
            # 'turn_template': 'turn_template', # Optional
            'regenerate': False,
            '_continue': False,
            'chat_instruct_command': 'Continue the chat dialogue below. Write a single reply for the character "<|character|>".\n\n<|prompt|>',

            # Generation params. If 'preset' is set to different than 'None', the values
            # in presets/preset-name.yaml are used instead of the individual numbers.
            'preset': 'None',
            'do_sample': True,
            'temperature': 0.7,
            'top_p': 0.1,
            'typical_p': 1,
            'epsilon_cutoff': 0,  # In units of 1e-4
            'eta_cutoff': 0,  # In units of 1e-4
            'tfs': 1,
            'top_a': 0,
            'repetition_penalty': 1.18,
            'repetition_penalty_range': 0,
            'top_k': 40,
            'min_length': 0,
            'no_repeat_ngram_size': 0,
            'num_beams': 1,
            'penalty_alpha': 0,
            'length_penalty': 1,
            'early_stopping': False,
            'mirostat_mode': 0,
            'mirostat_tau': 5,
            'mirostat_eta': 0.1,
            'guidance_scale': 1,
            'negative_prompt': '',

            'seed': -1,
            'add_bos_token': True,
            'truncation_length': 2048,
            'ban_eos_token': False,
            'custom_token_bans': '',
            'skip_special_tokens': True,
            'stopping_strings': []
        }

        response = requests.post(URI, json=request)

        if response.status_code == 200:
            print(response.json())
            result = response.json()['results'][0]['history']
            print(json.dumps(result, indent=4))
            print()
            print(html.unescape(result['visible'][-1][1]))
        
if __name__ == "__main__":
    action = Template()
    asyncio.run(action.run())

