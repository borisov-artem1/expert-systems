from items import Atom, Conjunct, Implication, Knowleadge, Term
from unification import unificate_atoms, apply_substitution, compose_substitutions
import copy
import graphviz


class BackwardDeduction():
    def __init__(self, knowleadge: Knowleadge) -> None:
        self.knowleadge = knowleadge.copy()
        self._uid = 0
        self.proof_graph = graphviz.Digraph(comment='Proof Tree',
                                            graph_attr={'rankdir': 'TB', 'bgcolor': 'white'})
        self.node_counter = 0

    def _get_unique_node_id(self, label: str) -> str:
        """Создает уникальный ID узла для Graphviz."""
        self.node_counter += 1
        return f"N{self.node_counter}_{label[:5].replace('(', '').replace(')', '').replace(':', '_')}"

    def knowleadge_prove(self, goal: Atom, max_depth: int = 1000) -> bool:
        """
        Попытка доказать goal методом обратной дедукции (DFS).
        Возвращает True если доказано, иначе False.
        """
        facts = self.knowleadge.data

        root_id = self._get_unique_node_id(str(goal))
        self.proof_graph.node(root_id, label=str(goal), style='filled', fillcolor='#D0E0FF')

        print(f"\nНачинаем доказательство цели: {goal}\n")
        final_subs = self._dfs(goal.copy(), facts, self.knowleadge.open_rules, self.knowleadge.close_rules, depth=0,
                               max_depth=max_depth, parent_node_id=root_id)

        proved = final_subs is not None
        if proved:
            print("\nЦель успешно доказана ✅\n")
            self._save_proof_graph(f"proof_C_{goal.args[0].name}.gv")
        else:
            print("\nНе удалось доказать цель ❌\n")
        return proved

    def _dfs(self, goal: Atom, facts: Conjunct, open_rules: list[Implication], close_rules: list[Implication],
             depth: int, max_depth: int, parent_node_id: str) -> dict[str, Term] | None:
        if depth > max_depth:
            return None

        print(f"{'  ' * depth}Доказываем: {goal}")

        for fact in facts.args:
            if fact.isPositive != goal.isPositive or fact.name != goal.name:
                continue
            subs = unificate_atoms(goal, fact)
            if subs is not None:
                print(f"{'  ' * depth}✔ Совпало с фактом: {fact} с подстановкой {subs}")

                fact_id = self._get_unique_node_id(str(fact))
                self.proof_graph.node(fact_id, label=f"FACT: {fact}", style='filled', fillcolor='#A8FFB0')
                self.proof_graph.edge(parent_node_id, fact_id, label=f"Matches {subs}", style='bold', color='#006400')

                return subs

        for rule_idx, rule in enumerate(list(open_rules)):
            std_rule = rule.copy()
            self._standardize_apart(std_rule)

            rule_initial_subs = None
            right_atom_to_unify = None

            for right_atom in std_rule.right.args:
                if right_atom.isPositive != goal.isPositive or right_atom.name != goal.name:
                    continue

                rule_initial_subs = unificate_atoms(right_atom, goal)
                if rule_initial_subs is not None:
                    right_atom_to_unify = right_atom
                    break

            if rule_initial_subs is None:
                continue

            left_subgoals = [a.copy() for a in std_rule.left.args]
            right_after = [a.copy() for a in std_rule.right.args]

            apply_substitution(left_subgoals + right_after, rule_initial_subs)

            print(f"{'  ' * depth}Применяем правило: {rule} (стандартизировано: {std_rule})")
            print(f"{'  ' * depth}Унификация {right_atom_to_unify} с {goal} дала подстановку {rule_initial_subs}")
            print(f"{'  ' * depth}Новые подцели: {', '.join(map(str, left_subgoals)) if left_subgoals else 'Пусто'}")

            rule_label = f"RULE: {rule}\nSub: {rule_initial_subs}"
            rule_node_id = self._get_unique_node_id(str(rule))
            self.proof_graph.node(rule_node_id, label=rule_label, shape='box', style='filled', fillcolor='#FFE0A0')
            self.proof_graph.edge(parent_node_id, rule_node_id, label="Implied by", style='dashed')

            current_total_subs = rule_initial_subs.copy()

            all_proved = True
            subgoal_ids = []

            for sg_idx, sg in enumerate(left_subgoals):
                subgoal_id = self._get_unique_node_id(str(sg))
                self.proof_graph.node(subgoal_id, label=str(sg), style='filled', fillcolor='#D0E0FF')
                self.proof_graph.edge(rule_node_id, subgoal_id, label=f"Subgoal {sg_idx + 1}")
                subgoal_ids.append(subgoal_id)

                proved_sg_subs = self._dfs(sg, facts, open_rules, close_rules, depth + 1, max_depth, subgoal_id)

                if proved_sg_subs is None:
                    all_proved = False
                    self.proof_graph.node(subgoal_id, style='filled', fillcolor='#FFD0D0')
                    print(f"{'  ' * depth}Подцель {sg} не доказана, откатываемся.")
                    break

                self.proof_graph.node(subgoal_id, style='filled', fillcolor='#D0FFD0')

                current_total_subs = compose_substitutions(current_total_subs, proved_sg_subs)
                apply_substitution(left_subgoals[sg_idx + 1:] + right_after, proved_sg_subs)

            if all_proved:
                for r in right_after:
                    apply_substitution([r], current_total_subs)

                    if not any(t.type == 'var' for t in r.args):
                        if not any(self._atoms_equal(r, existing) for existing in facts.args):
                            facts.args.append(r)
                            fact_id = self._get_unique_node_id(str(r))
                            self.proof_graph.node(fact_id, label=f"NEW FACT: {r}", style='filled, rounded',
                                                  fillcolor='#C0A0FF', shape='box')
                            self.proof_graph.edge(rule_node_id, fact_id, label="Conclusion", style='bold',
                                                  color='#800080')
                            print(f"{'  ' * depth}Добавляем факт: {r}")

                close_rules.append(std_rule)
                print(f"{'  ' * depth}Правило доказано и перемещено в закрытые: {std_rule}")

                return current_total_subs

        print(f"{'  ' * depth}Не найдено доказательство для: {goal}")
        return None

    def _save_proof_graph(self, filename="proof_tree.gv") -> None:
        """Сохраняет код графа в файл .gv."""
        try:
            self.proof_graph.render(filename, view=False, format='png')
            print(f"\nГраф вывода сохранен в {filename} (Graphviz source) и сгенерирован в {filename}.png")
        except Exception as e:
            self.proof_graph.save(filename)
            print(f"\nГраф вывода сохранен в {filename}. Для генерации .png установите Graphviz: {e}")


    def _standardize_apart(self, rule: Implication) -> None:
        """
        Переименовать все переменные в правиле, добавив уникальный суффикс,
        чтобы при рекурсивных вызовах переменные разных правил не пересекались.
        """
        self._uid += 1
        uid = self._uid

        def rename_term(term):
            if term.type == "var":
                term.name = f"{term.name}__{uid}"

        for atom in rule.left.args + rule.right.args:
            for t in atom.args:
                rename_term(t)

    def _atoms_equal(self, a1: Atom, a2: Atom) -> bool:
        if a1.isPositive != a2.isPositive or a1.name != a2.name:
            return False
        if len(a1.args) != len(a2.args):
            return False
        for t1, t2 in zip(a1.args, a2.args):
            if t1.type != t2.type:
                return False
            if t1.name != t2.name:
                return False
            if t1.type == "const" and t1.value != t2.value:
                return False
        return True

    def __equal_types(self, left: Atom, right: Atom) -> bool:
        if len(left.args) != len(right.args):
            return False
        for i in range(len(left.args)):
            if left.args[i].type != right.args[i].type:
                return False
        return True

