import json
import sys

def parse_garak_attempts(file_path):
    """
    Парсит JSONL файл с логами garak и возвращает список словарей
    с полями: uuid, input, output
    """
    results = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Ошибка JSON в строке {line_num}: {e}", file=sys.stderr)
                continue

            if record.get('entry_type') != 'attempt':
                continue

            # Извлечение входного промпта
            prompt = record.get('prompt', {})
            turns = prompt.get('turns', [])
            if turns and isinstance(turns, list):
                user_turn = turns[0]  # обычно первый turn - пользователь
                content = user_turn.get('content', {})
                input_text = content.get('text', '')
            else:
                input_text = ''

            # Извлечение ответа модели
            outputs = record.get('outputs', [])
            if outputs and isinstance(outputs, list):
                output_text = outputs[0].get('text', '')
            else:
                output_text = ''

            results.append({
                'uuid': record.get('uuid'),
                'input': input_text,
                'output': output_text
            })
    return results

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Использование: python parser.py <файл.jsonl>")
        sys.exit(1)

    data = parse_garak_attempts(sys.argv[1])
    print(f"Найдено записей: {len(data)}\n")

    for idx, item in enumerate(data, 1):
        print(f"--- Attempt #{idx} (uuid: {item['uuid']}) ---")
        print(f"INPUT:\n{item['input']}\n")
        print(f"OUTPUT:\n{item['output']}\n")
        print("-" * 80)