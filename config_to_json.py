import argparse
import json
import re
import math
import sys
# Exception for syntax errors
class SyntaxError(Exception):
    pass

# Parser class
class ConfigParser:
    def __init__(self):
        self.constants = {}

    def parse(self, text):
        # Remove comments
        text = self._remove_comments(text)
        # Parse constants
        text = self._parse_constants(text)
        # Parse main content
        return self._parse_structure(text.strip())

    def _remove_comments(self, text):
        text = re.sub(r";.*", "", text) 
        text = re.sub(r"\{#.*?#\}", "", text, flags=re.DOTALL) 
        return text

    def _parse_constants(self, text):
        set_pattern = re.compile(r"set ([a-zA-Z_]+) = (.+)")

        for match in set_pattern.finditer(text):
            name, value = match.groups()
            self.constants[name] = self._evaluate(value.strip())
        text = set_pattern.sub("", text)

        return text

    def _evaluate(self, expression):
        # Проверяем строковые литералы
        if expression.startswith('"') and expression.endswith('"'):
            return expression[1:-1]  # Убираем кавычки и возвращаем строку
        # Числа
        if re.match(r"^-?\d+(\.\d+)?$", expression):
            return float(expression) if '.' in expression else int(expression)
        # Константы
        if expression in self.constants:
            return self.constants[expression]
        # Выражения
        if expression.startswith("@{") and expression.endswith("}"):
            content = expression[2:-1].strip()
            return self._evaluate_expression(content)
        raise SyntaxError(f"Invalid constant expression: {expression}")


    def _evaluate_expression(self, expression):
        parts = expression.split()
        if len(parts) < 2:
            raise SyntaxError(f"Invalid expression: {expression}")
        op, *args = parts
        args = [self._evaluate(arg) for arg in args]

        if op == "+":
            return sum(args)
        elif op == "sqrt":
            if len(args) != 1:
                raise SyntaxError(f"sqrt expects one argument, got {len(args)}")
            return math.sqrt(args[0])
        elif op == "abs":
            if len(args) != 1:
                raise SyntaxError(f"abs expects one argument, got {len(args)}")
            return abs(args[0])
        else:
            raise SyntaxError(f"Unknown operation: {op}")

    def _parse_value(self, text):
        text = text.strip()
        if text.startswith("[") and text.endswith("]"):
            return self._parse_array(text)
        if text.startswith("table(") and text.endswith(")"):
            return self._parse_table(text)
        return self._evaluate(text)



    def _parse_array(self, text):
        content = text[1:-1].strip()
        if not content:
            return []
        items = []
        balance = 0
        current_item = []

        for char in content:
            if char == ',' and balance == 0:
                items.append(''.join(current_item).strip())
                current_item = []
            else:
                current_item.append(char)
                if char == '[' or char == '(':
                    balance += 1
                if char == ']' or char == ')':
                    balance -= 1

        if current_item:
            items.append(''.join(current_item).strip())

        return [self._parse_value(item) for item in items]

    def _parse_table(self, text):
        content = text[6:-1].strip()  # Убираем "table(" и ")"
        if not content:
            return {}
        result = {}
        items = []
        balance = 0
        current_item = []
    
        # Разбиваем текст на элементы верхнего уровня
        for char in content:
            if char == ',' and balance == 0:
                items.append(''.join(current_item).strip())
                current_item = []
            else:
                current_item.append(char)
                if char in "([{":
                    balance += 1
                elif char in ")]}":
                    balance -= 1
    
        if current_item:
            items.append(''.join(current_item).strip())
    
        # Парсим каждый элемент как ключ-значение
        for item in items:
            if "=>" in item:
                key, value = item.split("=>", 1)
                key = key.strip()
                value = value.strip()
                result[key] = self._parse_value(value)
            else:
                raise SyntaxError(f"Invalid table entry: {item}")
    
        return result
    




    def _parse_structure(self, text):
        
        result = {}
        items = []
        current_item = []
        balance = 0

        # Парсим строку на элементы верхнего уровня
        for char in text:
            if char == ',' and balance == 0:  # Разделяем только на верхнем уровне
                if current_item:
                    items.append(''.join(current_item).strip())
                    current_item = []
            else:
                current_item.append(char)
                if char in "([{":
                    balance += 1
                elif char in ")]}":
                    balance -= 1

        if current_item:
            items.append(''.join(current_item).strip())

        for item in items:
            if "=>" in item:  # Это ключ-значение
                key, value = item.split("=>", 1)
                result[key.strip()] = self._parse_value(value.strip())
            elif item.startswith("table(") and item.endswith(")"):  # Обработка вложенных таблиц
                result.update(self._parse_table(item))
            else:
                raise SyntaxError(f"Invalid structure: {item}")
        return result


# Main function
def main():
    parser = argparse.ArgumentParser(description="Convert config to JSON.")
    parser.add_argument("input_file", help="Path to the input config file.")
    args = parser.parse_args()

    with open(args.input_file, "r", encoding="utf-8") as f:
        text = f.read()

    try:
        config_parser = ConfigParser()
        result = config_parser.parse(text)
        print(json.dumps(result, indent=4))
    except SyntaxError as e:
        print(f"Syntax error: {e}", file=sys.stderr)
        exit(1)

if __name__ == "__main__":
    main()
