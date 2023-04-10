#  Copyright Notice for GuteFrageBot Copyright (c) at Carina Sophie Schoppe, Tim Fischer 2023 File created on 4/10/23, 9:39 PM by Carin The Latest changes made by Carin on 4/10/23, 9:38 PM All contents of "main.py" are protected by copyright. The copyright law, unless expressly indicated otherwise, is at Carina Sophie Schoppe, Tim Fischer. All rights reserved Any type of duplication, distribution, rental, sale, award, Public accessibility or other use requires the express written consent of Carina Sophie Schoppe, Tim Fischer.

import datetime
import time
from typing import Any

import gutefrage as gf
import openai

gutefrage_username = ""
gutefrage_password = ""
openai.api_key = ""
gutefrage_client = gf.gutefrage(gutefrage_username, gutefrage_password)
original = 130396164
base_id = original
log = True
debug = True
delay = 1
skip = 150
fails = 0
odd = False


def generate_open_ai_answer(title, question: str) -> str:
    if debug:
        print("start generating answer")
    message = f"Antworte wie ein nutzer bzw. Experte auf der Plattform gutefrage.net auf die Frage: {question} mit dem Fragetitel: {title}\n\n Am ende darf keine Grußformel stehen!"
    completion = openai.ChatCompletion.create(
        model="gpt-4-0314",  # gpt-3.5-turbo-0301 oder gpt-4-0314 oder gpt-4
        messages=[{"role": "user", "content": message}]
    )

    result = completion.choices[0]["message"]["content"]

    return result


def post_answer(question_id: int, answer: str) -> None:
    question = gutefrage_client.question(question_id)
    question.reply(answer + "\n Ich hoffe ich konnte dir mit meiner Antwort weiterhelfen.\n Liebe Grüße, Carina Sophie Schoppe :) ")
    if debug:
        print(f"Answered question {question.info()['title']} with answer {answer}")


# create a comment

def get_question_and_title(question_id: int) -> tuple[Any, Any] | tuple[None, None]:
    question = gutefrage_client.question(question_id)
    info = question.info()
    if "error" not in info:
        body = question.info()["body"]
        title = question.info()["title"]
        # remove <p> tags in body
        body = body.replace("<p>", "").replace("</p>", "")
        return title, body
    else:
        if debug:
            print("Error: ", info["error"])
        return None, None


def question_analyser(question_id: int) -> bool:
    question = gutefrage_client.question(question_id)
    info = question.info()
    if info["is_poll"] is not None:
        print("is poll therefore not answering")
        return False
    if info["image_ids"] is not None:
        print("has image therefore not answering")
        return False
    return True


def main():
    global base_id
    while True:
        try:
            if odd and base_id % 2 == 0:
                base_id += 1
                continue
            title, body = get_question_and_title(base_id)
            if title is not None:
                analyse_result = question_analyser(base_id)

                if debug:
                    print(f"Question: {title} {body}")
                if analyse_result is False:
                    base_id += 1
                    continue
                answer = generate_open_ai_answer(title, body)
                post_answer(base_id, answer)
                if log:
                    with open("log.txt", "a", encoding="utf-8") as file:
                        file.write(f"******************************************************************************\n[{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] {base_id} {title} {body} {answer}\n")
                        if debug:
                            print(f"[{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] Written to Log: {base_id} {title} {body} \n{answer}")
                base_id += 1

                time.sleep(delay)
            else:
                if base_id > original + skip:
                    base_id = original
                else:
                    base_id += 1
        except Exception as exe:
            global fails
            if debug:
                print(exe)
                print("Error while answering question")
            fails += 1
            if fails >= 10:
                fails = 0
                base_id += 100


if __name__ == "__main__":
    main()
