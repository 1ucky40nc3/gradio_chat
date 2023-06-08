from typing import Tuple

import time
import random
import logging
import argparse

import gradio as gr

from frontend.models import ChatHistory, Update
from frontend.utils import (
    load_frontend_from_cache,
    load_chats_from_cache,
    load_settings,
    pprint_dcls,
    pprint_dict,
    list_chat_ids,
    find_chat_by_id,
    set_chat_by_id,
    update_chat_by_id,
    del_chat_by_id,
    empty_chat,
    list_setting_ids,
    find_setting_by_id
)


logger = logging.getLogger(__name__)


# We work with global variables here.
# TODO: Use states instead of global variables
chats = None
settings = None


def message_fn(
    message: str, 
    chat_history: ChatHistory, 
    setting_id: str
) -> Tuple[str, ChatHistory]:
    setting = find_setting_by_id(setting_id, settings)
    
    bot_message = random.choice(["How are you?", "I love you", "I'm very hungry"])
    chat_history.append((message, bot_message))
    time.sleep(2)
    return "", chat_history


def select_chat_event(choice: str, chat_id: str, chat_history: ChatHistory) -> Tuple[str, Update, Update]:
    set_chat_by_id(chat_id, chat_history, chats)
    chat = find_chat_by_id(choice, chats)
    return chat.id, gr.update(value=chat.history), gr.update(value=chat.id)


def add_chat_event(chat_id: str, chat_history: ChatHistory) -> Tuple[str, ChatHistory, Update]:
    set_chat_by_id(chat_id, chat_history, chats)
    chat = empty_chat()
    chats.append(chat)
    choices = list_chat_ids(chats)
    return chat.id, chat.history, gr.update(choices=choices, value=chat.id)


def delete_chat_event(chat_id: str) -> Tuple[str, ChatHistory, Update]:
    del_chat_by_id(chat_id, chats)
    if len(chats) == 0:
        logger.info("Creating empty chat because we deleted all chats")
        chat = empty_chat()
        chats.append(chat)
    chat = chats[0]
    choices = list_chat_ids(chats)
    return chat.id, chat.history, gr.update(choices=choices, value=chat.id)


def clear_chat_event() -> None:
    return None


def select_setting_event(choice: str) -> str:
    print(f"Selected setting: {choice}")
    return choice


def rename_chat_event(new_id: str, chat_id: str) -> Tuple[str, Update]:
    chat = find_chat_by_id(chat_id, chats)
    chat.id = new_id
    update_chat_by_id(chat_id, chat, chats)
    choices = list_chat_ids(chats)
    return chat.id, gr.update(choices=choices, value=chat.id)


def argument_parser() -> argparse.ArgumentParser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--frontend",
        default="src/frontend/configs/frontend/default.json",
        type=str,
        help="The path to a frontend config file."
    )
    parser.add_argument(
        "--settings",
        default="src/frontend/configs/settings",
        type=str,
        help="The path to a directory with settings files."
    )
    parser.add_argument(
        "--cache",
        default=".cache",
        type=str,
        help="The path to the cache directory."
    )
    parser.add_argument(
        "--share",
        action="store_true",
        default=False,
        help="State if you want to share the gradio app."
    )
    parser.add_argument(
        "--server_name",
        default="127.0.0.1",
        type=str,
        help="The IP address of the local gradio server."
    )
    parser.add_argument(
        "--server_port",
        default=7860,
        type=int,
        help="The port of our local gradio server."
    )

    return parser


def app(args: argparse.Namespace) -> None:
    global chats
    global settings

    frontend = load_frontend_from_cache(args.frontend, args.cache)
    logger.info(f"Loaded frontend config:\n{pprint_dcls(frontend)}")
    settings = load_settings(args.settings)
    logger.info(f"Loaded a total of {len(settings)} settings")
    chats = load_chats_from_cache(args.cache)
    logger.info(f"Loaded a total of {len(chats)} chats")

    if len(chats) == 0:
        chat = empty_chat("Start")
        chats.append(chat)

    chat_id = frontend.chat_id
    if chat_id is None:
        chat_id = chats[0].id
    setting_id = frontend.setting_id
    print(f"{chat_id=}")

    with gr.Blocks() as demo:
        # Set the states
        chat_id_state = gr.State(chat_id)
        setting_id_state = gr.State(setting_id)

        # Init the layout
        with gr.Row():
            select_chat_radio = gr.Radio(
                choices=list_chat_ids(chats),
                value=chat_id,
                label="Select chat", 
                interactive=True
            )
            with gr.Row():
                add_chat_button = gr.Button(value="New chat")
                delete_chat_button = gr.Button(value="Delete chat")
        
        with gr.Column():
            chat = find_chat_by_id(chat_id, chats)
            chatbot = gr.Chatbot(
                value=chat.history, 
                interactive=True, 
                label="Chat history"
            )
            message_text_box = gr.Textbox(label="Submit a message")
            clear_chat_button = gr.Button(value="Clear chat")

            with gr.Accordion("Settings"):
                select_setting_radio = gr.Radio(
                    choices=list_setting_ids(settings),
                    value=setting_id,
                    label="Select a LLM setting", 
                    interactive=True
                )
                rename_text_box = gr.Textbox(
                    value=chat_id,
                    label="Rename the chat",
                    interactive=True
                )

        # Set the events
        add_chat_button.click(
            add_chat_event, 
            inputs=[
                chat_id_state,
                chatbot,
            ],
            outputs=[
                chat_id_state,
                chatbot,
                select_chat_radio
            ]
        )
        delete_chat_button.click(
            delete_chat_event, 
            inputs=[
                chat_id_state,
            ],
            outputs=[
                chat_id_state, 
                chatbot,
                select_chat_radio
            ]
        )
        clear_chat_button.click(
            clear_chat_event, 
            inputs=None, 
            outputs=chatbot, 
            queue=False
        )
        select_chat_radio.change(
            select_chat_event, 
            inputs=[
                select_chat_radio, 
                chat_id_state, 
                chatbot
            ], 
            outputs=[
                chat_id_state, 
                chatbot,
                rename_text_box
            ]
        )
        message_text_box.submit(
            message_fn, 
            inputs=[
                message_text_box, 
                chatbot,
                setting_id_state
            ], 
            outputs=[
                message_text_box, 
                chatbot
            ]
        )
        select_setting_radio.change(
            select_setting_event,
            inputs=setting_id_state,
            outputs=setting_id_state
        )
        rename_text_box.submit(
            rename_chat_event, 
            inputs=[
                rename_text_box, 
                chat_id_state
            ], 
            outputs=[
                chat_id_state, 
                select_chat_radio
            ]
        )

    demo.launch(
        share=args.share, 
        server_name=args.server_name,
        server_port=args.server_port
    )


def main() -> None:
    parser = argument_parser()
    args = parser.parse_args()
    logger.info(f"Starting frontend with args:\n{pprint_dict(vars(args))}")

    app(args)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    main()