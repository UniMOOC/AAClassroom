# encoding=utf-8
"""
Generador de contenido para exámenes con feedback

El formato de los ficheros debe ser el siguiente. Cada pregunta del examen
(en el siguiente orden, separado por saltos de linea):
    + Titulo del examen (no se usa)
    + Numero del examen (será el nombre del fichero)
    + Numero de la pregunta (no se usa)
    + La pregunta
    - La opcion a mostrar
    - Si es correcta o no (Si / No, solo usa la primera letra en minuscula)

Los campos con + solo aparecen en la linea con la pregunta, es decir, solo
una vez por pregunta.

Un ejemplo de fichero con dos examenes de una pregunta cada uno:
=============
Nombre    1   1   Clics, leads y ventas son KPIs típicos de las campañas a respuesta directa: Verdadero.  Si
                Falso.  No

    1   2   La plataforma de entrega y optimización de campañas de publicidad online se llama:  Admaker.    No
                Adserver.   Si
                Adtemper.   No
    1   3   El tag publicitario es: Un código que desde una página web hace una llamada al Adserver.    Si
                Un código que desde una página sirve una creatividad publicitaria.  No
                Un chiste publicitario. No
=============
"""


import json
import codecs
import argparse
from utf8 import UnicodeReader


def main():
    parser = argparse.ArgumentParser(
        description='Create one or more assessments'
    )
    parser.add_argument('assessments_file')
    # parser.add_argument('-f', help='Adds feedback', action='store_true')
    args = parser.parse_args()

    if args.assessments_file:
        asm_file = open(args.assessments_file, 'r')
        asm_reader = UnicodeReader(asm_file, delimiter='\t')

        make_assmessment(asm_reader, {})


def make_assmessment(asm_reader, options):
    questions = []
    assessment_number = None
    current_question = None
    for row in asm_reader:
        row = [i for i in row if i]

        if not row:
            continue

        if len(row) == 5:
            row.insert(0, '')

        if len(row) == 6 and current_question:
            questions.append(current_question)
            current_question = None
            if row[1] != assessment_number:
                write_assessment(questions, assessment_number)
                questions = []
                assessment_number = row[1]

        if not current_question:
            if not assessment_number:
                assessment_number = row[1]
            question, option, correct = split_question_row(row)
            current_question = {
                'key': len(questions) + 1,
                'question': question,
                'correct': 0 if correct else None,
                'options': [option]
            }
        else:
            option, correct = split_option_row(row)
            current_question['options'].append(option)
            if correct:
                current_question['correct'] = len(current_question['options']) - 1

    if current_question:
        questions.append(current_question)

    write_assessment(questions, assessment_number)


def split_option_row(row):
    option = row[0]
    correct = row[1][:1].lower() == 's' if len(row) > 1 else False

    return option, correct


def split_question_row(row):
    question = row[3]
    option = row[4]
    correct = row[5][:1].lower() == 's'

    return question, option, correct


def write_assessment(questions, name):
    asm_fout = codecs.open(
        u'{}.json'.format(name),
        'w',
        encoding='utf-8'
    )
    asm_fout.write(json.dumps(
        questions, sort_keys=True,
        indent=4, separators=(',', ': '),
        ensure_ascii=False)
    )
    asm_fout.close()

if __name__ == '__main__':
    main()
