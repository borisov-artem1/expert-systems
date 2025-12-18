import copy
from graphviz import Digraph
import uuid


class Rule:
    def __init__(self, input_atoms, output_vertex):
        self.input_atoms = input_atoms
        self.output_vertex = output_vertex
        self.id = str(uuid.uuid4())[:8]

    def __str__(self):
        inputs_str = " & ".join(str(atom) for atom in self.input_atoms)
        output_str = str(self.output_vertex)
        return f"{inputs_str} -> {output_str}"

    def __repr__(self):
        return self.__str__()


class Atom:
    def __init__(self, name, terminals):
        self.name = name
        self.terminals = terminals
        self.id = str(uuid.uuid4())[:8]
        self.proven = False

    def __str__(self):
        strterms = ""
        for term in self.terminals:
            strterms += str(term) + ", "
        return self.name + '(' + strterms.strip(", ") + ')'

    def __repr__(self):
        return self.__str__()

    def copy_with_substitutions(self, table):
        """Создает копию атома с примененными подстановками"""
        new_terminals = []
        for term in self.terminals:
            if isinstance(term, Variable) and term.name in table.variables:
                value = table.variables[term.name]
                if isinstance(value, str):
                    if value in table.variables:
                        val2 = table.variables[value]
                        if isinstance(val2, str):
                            new_terminals.append(Variable(value))
                        else:
                            new_terminals.append(val2)
                    else:
                        new_terminals.append(Variable(value))
                else:
                    new_terminals.append(value)
            else:
                new_terminals.append(term)
        return Atom(self.name, new_terminals)


class Constant:
    def __init__(self, value):
        self.value = value
        self.variable = False

    def __str__(self):
        return f"{self.value}:const"

    def __repr__(self):
        return self.__str__()


class Variable:
    def __init__(self, name):
        self.name = name
        self.variable = True

    def __str__(self):
        return f"{self.name}:var"

    def __repr__(self):
        return self.__str__()


class Table:
    def __init__(self):
        self.variables = dict()
        self.links = dict()

    def reset(self, other):
        self.variables = other.variables.copy()
        self.links = other.links.copy()

    def __str__(self):
        res = ""
        for var, val in self.variables.items():
            res += f"{var} = {val}\n"
        return res


def unification(table, p1, p2):
    if p1.name != p2.name:
        return False

    if len(p1.terminals) != len(p2.terminals):
        return False

    original = copy.deepcopy(table)

    for t1, t2 in zip(p1.terminals, p2.terminals):
        if t1.variable:
            if t2.variable:
                if t1.name not in table.variables and t2.name not in table.variables:
                    table.variables[t1.name] = t2.name
                    table.variables[t2.name] = t1.name
                elif t1.name not in table.variables:
                    table.variables[t1.name] = table.variables[t2.name]
                elif t2.name not in table.variables:
                    table.variables[t1.name] = table.variables[t2.name]
                elif table.variables[t1.name] != table.variables[t2.name]:
                    table.reset(original)
                    return False
            else:
                if t1.name in table.variables and type(table.variables[t1.name]) is not str:
                    if table.variables[t1.name].value != t2.value:
                        table.reset(original)
                        return False

                if t1.name not in table.variables:
                    table.variables[t1.name] = t2

                if type(table.variables[t1.name]) is str:
                    k = table.variables[t1.name]
                    table.variables[t1.name] = t2
                    table.variables[k] = t2
        else:
            if t2.variable:
                if t2.name in table.variables and type(table.variables[t2.name]) is not str:
                    if table.variables[t2.name].value != t1.value:
                        table.reset(original)
                        return False

                if t2.name not in table.variables:
                    table.variables[t2.name] = t1

                if type(table.variables[t2.name]) is str:
                    k = table.variables[t2.name]
                    table.variables[t2.name] = t1
                    table.variables[k] = t1
            else:
                if t1.value != t2.value:
                    table.reset(original)
                    return False
    return True


class HyperGraphSearcher:
    def __init__(self, rules):
        self.rules = rules
        self.table = Table()
        self.proven_atoms = list()
        self.proven_rules = list()
        self.opened_atoms = list()
        self.used_atoms = list()
        self.found = False

        self.search_tree = []
        self.current_step = 0
        self.proof_tree = []

    def add_to_proof_tree(self, node_type, content, parent_id=None, substitutions=None):
        """Добавляет узел в дерево доказательства"""
        node_id = f"node_{len(self.proof_tree)}"
        node = {
            'id': node_id,
            'type': node_type,
            'content': content,
            'parent': parent_id,
            'substitutions': substitutions.copy() if substitutions else {},
            'children': [],
            'proven': node_type == 'fact' or node_type == 'new_fact'
        }

        if parent_id:
            for n in self.proof_tree:
                if n['id'] == parent_id:
                    n['children'].append(node_id)
                    break

        self.proof_tree.append(node)
        return node_id

    def visualize_search_tree(self, filename="proof_tree"):
        """Создает сбалансированную древовидную визуализацию доказательства"""
        dot = Digraph(comment='Дерево доказательства')

        dot.attr(rankdir='LR', size='24,16', dpi='300',
                 nodesep='0.8', ranksep='1.5',
                 compound='true')

        levels = {}
        for node in self.proof_tree:
            level = 0
            current = node
            while current.get('parent'):
                level += 1
                parent_id = current['parent']
                current = next(n for n in self.proof_tree if n['id'] == parent_id)
            levels.setdefault(level, []).append(node)

        for level, nodes in sorted(levels.items()):
            with dot.subgraph(name=f'cluster_{level}') as cluster:
                cluster.attr(label=f'Уровень {level}', style='rounded', color='lightgrey',
                             fontsize='10', rank='same')
                for node in nodes:
                    node_id = node['id']
                    label = self._format_node_label(node)
                    cluster.node(node_id, label, **self._get_node_style(node['type']))

        for node in self.proof_tree:
            if node['parent']:
                parent_type = next(n['type'] for n in self.proof_tree if n['id'] == node['parent'])
                edge_attrs = self._get_edge_attrs(node['type'], parent_type)
                dot.edge(node['parent'], node['id'], **edge_attrs)

        dot.render(filename, view=True, cleanup=True)
        return dot

    def _format_node_label(self, node):
        """Форматирует label для узла"""
        if node['type'] == 'goal':
            return f" {node['content']}"
        elif node['type'] == 'rule':
            rule_num, rule_str = node['content']
            label = f" Правило {rule_num}"
            if node['substitutions']:
                subs = " ".join([f"{k}={v}" for k, v in node['substitutions'].items()])
                label += f"\n {subs}"
            return label
        elif node['type'] == 'subgoal':
            return f" {node['content']}"
        elif node['type'] == 'fact':
            return f" {node['content']}"
        elif node['type'] == 'new_fact':
            return f" NEW: {node['content']}"
        return node['content']

    def _get_node_style(self, node_type):
        """Возвращает стиль для узла"""
        styles = {
            'goal': {'shape': 'box', 'style': 'filled', 'fillcolor': 'lightblue'},
            'rule': {'shape': 'parallelogram', 'style': 'filled', 'fillcolor': 'lightyellow'},
            'subgoal': {'shape': 'ellipse', 'style': 'filled', 'fillcolor': 'wheat'},
            'fact': {'shape': 'ellipse', 'style': 'filled', 'fillcolor': 'lightgreen'},
            'new_fact': {'shape': 'ellipse', 'style': 'filled', 'fillcolor': 'palegreen'},
        }
        return styles.get(node_type, {})

    def _get_edge_attrs(self, node_type, parent_type):
        """Возвращает атрибуты для связи"""
        attrs = {}
        if node_type == 'rule' and parent_type == 'goal':
            attrs = {'label': ' ← ', 'fontsize': '10'}
        elif node_type == 'fact' and parent_type == 'subgoal':
            attrs = {'label': ' ✓ ', 'fontsize': '10', 'style': 'dashed'}
        elif node_type == 'new_fact' and parent_type == 'rule':
            attrs = {'label': ' → ', 'fontsize': '10', 'style': 'bold'}
        return attrs

    def search_from_target(self, input_atoms, target_atom):
        self.table = Table()
        self.opened_atoms = [target_atom]
        self.proven_atoms = list(input_atoms)
        self.used_atoms = []

        goal_id = self.add_to_proof_tree('goal', str(target_atom))

        current = self.opened_atoms[0]
        current_node_id = goal_id

        print(f"\nНачинаем поиск доказательства для {target_atom}")

        while not self.found and len(self.opened_atoms) != 0:
            print(f"\nТекущая подцель: {current}")

            current_with_subs = current.copy_with_substitutions(self.table)
            for proven in self.proven_atoms:
                temp_check = copy.deepcopy(self.table)
                if unification(temp_check, current_with_subs, proven):
                    print(f"Подцель {current} уже доказана как {proven}")
                    self.table = temp_check

                    if current in self.opened_atoms:
                        self.opened_atoms.remove(current)

                    if self.opened_atoms:
                        current = self.opened_atoms[0]
                        for node in self.proof_tree:
                            if (node['type'] == 'subgoal' and
                                    str(node['content']) == str(current)):
                                current_node_id = node['id']
                                break
                    continue

            rule_applied = False
            for num, rule in self.rules.items():
                temp_table = copy.deepcopy(self.table)

                if unification(temp_table, rule.output_vertex, current):
                    print(f"Нашли правило {num}: {rule}")
                    rule_applied = True

                    self.table = temp_table

                    current = current.copy_with_substitutions(self.table)
                    print(f"После подстановок: {current}")

                    rule_id = self.add_to_proof_tree('rule',
                                                     (num, str(rule)),
                                                     current_node_id,
                                                     self.table.variables)

                    all_proven = True
                    for i, node in enumerate(rule.input_atoms):
                        node_with_subs = node.copy_with_substitutions(self.table)
                        print(f"Проверяем атом {i + 1} (после подстановок): {node_with_subs}")

                        subgoal_id = self.add_to_proof_tree('subgoal', str(node_with_subs), rule_id)

                        atom_proven = False

                        for proven in self.proven_atoms:
                            temp_table2 = copy.deepcopy(self.table)
                            if unification(temp_table2, node_with_subs, proven):
                                print(f"Нашли факт: {proven}")

                                self.table = temp_table2

                                node_with_subs = node_with_subs.copy_with_substitutions(self.table)

                                self.add_to_proof_tree('fact', str(proven), subgoal_id)

                                atom_proven = True
                                break

                        if not atom_proven:
                            node_original = rule.input_atoms[i]
                            if node_original in self.used_atoms:
                                print(f"Атом {node_original} уже был использован, пропускаем")
                                continue

                            self.used_atoms.append(node_original)

                            print(f"Атом {node_with_subs} не найден в фактах, добавляем как подцель")
                            all_proven = False

                            if node_with_subs not in self.opened_atoms:
                                self.opened_atoms.insert(0, node_with_subs)

                            current = self.opened_atoms[0]
                            current_node_id = subgoal_id
                            break

                    if all_proven:
                        print(f"Все атомы правила {num} доказаны!")

                        proven_atom = current.copy_with_substitutions(self.table)
                        proven_atom.proven = True

                        print(f"Выводим новый факт: {proven_atom}")

                        self.add_to_proof_tree('new_fact', str(proven_atom), rule_id)

                        if not any(str(proven_atom) == str(p) for p in self.proven_atoms):
                            self.proven_atoms.append(proven_atom)
                            self.proven_rules.append(num)

                        if current in self.opened_atoms:
                            self.opened_atoms.remove(current)

                        for proven in self.proven_atoms:
                            temp_check = copy.deepcopy(self.table)
                            if unification(temp_check, target_atom, proven):
                                print(f"ЦЕЛЬ {target_atom} ДОСТИГНУТА!")
                                self.found = True
                                break

                        if self.opened_atoms and not self.found:
                            current = self.opened_atoms[0]
                            for node in self.proof_tree:
                                if (node['type'] == 'subgoal' and
                                        str(node['content']) == str(current) and
                                        not node.get('processed', False)):
                                    current_node_id = node['id']
                                    node['processed'] = True
                                    break
                        break

                    break

            if not rule_applied:
                print(f"Не найдено подходящих правил для {current}")
                if current not in self.used_atoms:
                    self.used_atoms.append(current)

                if self.opened_atoms:
                    removed = self.opened_atoms.pop(0)
                    if self.opened_atoms:
                        current = self.opened_atoms[0]
                        for node in self.proof_tree:
                            if (node['type'] == 'subgoal' and
                                    str(node['content']) == str(current)):
                                current_node_id = node['id']
                                break

        self.visualize_search_tree()

        if self.found:
            new_proven_atoms = []
            for atom in self.proven_atoms:
                if atom not in input_atoms and not any(str(atom) == str(fact) for fact in input_atoms):
                    new_proven_atoms.append(atom)

            return self.found, new_proven_atoms, self.proven_rules
        else:
            return self.found


def main():
    c_N = Constant('N')
    c_M1 = Constant('M1')
    c_W = Constant('W')
    c_A1 = Constant('A1')

    v_x = Variable("x")
    v_y = Variable("y")
    v_z = Variable("z")
    v_x1 = Variable("x1")
    v_x2 = Variable("x2")
    v_x3 = Variable("x3")

    node1 = Atom("A", [v_x])
    node2 = Atom("W", [v_y])
    node3 = Atom("S", [v_x, v_y, v_z])
    node4 = Atom("H", [v_z])
    node5 = Atom("C", [v_x])

    node6 = Atom("M", [v_x1])
    node7 = Atom("O", [c_N, v_x1])
    node8 = Atom("S", [c_W, v_x1, c_N])

    node9 = Atom("M", [v_x2])
    node10 = Atom("W", [v_x2])

    node11 = Atom("E", [v_x3, c_A1])
    node12 = Atom("H", [v_x3])

    rules = dict()
    rules[1] = Rule([node1, node2, node3, node4], node5)
    rules[2] = Rule([node6, node7], node8)
    rules[3] = Rule([node9], node10)
    rules[4] = Rule([node11], node12)

    print("=== БАЗА ПРАВИЛ ===")
    for num, rule in rules.items():
        print(f"Правило {num}: {rule}")

    graph = HyperGraphSearcher(rules)

    target = Atom("C", [c_W])
    given = [
        Atom("O", [c_N, c_M1]),
        Atom("M", [c_M1]),
        Atom("A", [c_W]),
        Atom("E", [c_N, c_A1]),
    ]

    print("\n ЦЕЛЬ ДОКАЗАТЕЛЬСТВА:")
    print(f"   {target}")
    print("\n ИСХОДНЫЕ ФАКТЫ:")
    for i, atom in enumerate(given, 1):
        print(f"   {i}. {atom}")

    print("\n" + "=" * 60)

    res = graph.search_from_target(given, target)

    if isinstance(res, tuple):
        found, nodes, rules = res
        if found:
            print("\n" + "=" * 60)
            print(" РЕШЕНИЕ НАЙДЕНО!")
            print("\n Доказанные атомы:")
            for i, atom in enumerate(nodes, 1):
                print(f"   {i}. {atom}")
            print(f"\n Доказанные правила: {rules}")
    else:
        if res:
            print("\n РЕШЕНИЕ НАЙДЕНО!")
        else:
            print("\n РЕШЕНИЕ НЕ НАЙДЕНО!")

    print("\n Таблица подстановок:")
    print(graph.table)


if __name__ == "__main__":
    main()