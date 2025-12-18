from items import Atom, Conjunct, Implication, Knowleadge
from unification import unificate_atoms, apply_substitution, add_substitutions


class BackwardDeduction():
    def __init__(self, knowleadge: Knowleadge) -> None:
        self.knowleadge = knowleadge.copy()
        self.step_counter = 0

    def knowleadge_prove(self, goal: Atom) -> bool:
        facts = self.knowleadge.data
        open_rules = self.knowleadge.open_rules
        close_rules = self.knowleadge.close_rules

        print(f"\n{'=' * 64}")
        print("НАЧАЛО ОБРАТНОЙ ДЕДУКЦИИ")
        print(f"{'=' * 64}")
        print(f"Цель: {goal}")

        self.step_counter = 0

        if self.__is_proved(facts.args, goal):
            print("✓ Цель уже содержится в фактах!")
            return True

        global_subs = {}

        print(f"\n{'=' * 64}")
        print("ШАГ 1: Пытаемся правило для цели C(W)")
        print(f"{'=' * 64}")

        for rule in open_rules:
            self.step_counter += 1
            print(f"\nТекущее правило (шаг {self.step_counter}):")
            print(f"  {rule}")
            print(f"\nТекущее состояние базы знаний:")
            print(self.knowleadge)

            result = self.__try_to_prove(
                facts=facts,
                rule=rule,
                goal=goal,
                global_substitutions=global_subs,
            )

            if result is not None:
                print(f"\n{'=' * 64}")
                print("✓ ЦЕЛЬ УСПЕШНО ДОКАЗАНА!")
                print(f"Финальные подстановки: {global_subs}")
                print(f"{'=' * 64}")
                return True
            else:
                print(f"\n✗ Правило не привело к доказательству цели")
                print(f"{'-' * 64}")

        print(f"\n{'=' * 64}")
        print("✗ НЕ УДАЛОСЬ ДОКАЗАТЬ ЦЕЛЬ")
        print(f"Все правила проверены, цель не доказана")
        print(f"{'=' * 64}")
        return False

    def __try_to_prove(
            self,
            facts: Conjunct,
            rule: Implication,
            goal: Atom,
            global_substitutions: dict
    ) -> Conjunct | None:

        print(f"\n  Пытаемся применить правило:")
        print(f"    Правило: {rule}")
        print(f"    Цель: {goal}")

        rule_result = rule.right.copy()
        rule_input_atoms = rule.left.copy()

        # унифицируем правую часть правила с целью
        print(f"  Унифицируем вывод правила с целью...")
        for right_atom in rule_result.args:
            subs = unificate_atoms(right_atom, goal)

            if subs is None:
                print(f"  ✗ Вывод правила {right_atom} НЕ унифицируется с целью {goal}")
                print(f"  Правило не подходит")
                return None

            print(f"  ✓ Вывод правила {right_atom} унифицируется с целью {goal}")
            print(f"    Подстановки: {subs}")

            add_substitutions(global_substitutions, subs)
            apply_substitution(rule_result.args + rule_input_atoms.args, subs)

            print(f"  После подстановок:")
            print(f"    Вывод правила: {rule_result}")
            print(f"    Условия правила: {rule_input_atoms}")

        print(f"\n  Переходим к доказательству условий правила...")
        print(f"  Условия для доказательства: {rule_input_atoms}")

        success = self.dfs(
            left=rule_input_atoms,
            facts=facts,
            global_substitutions=global_substitutions
        )

        if not success:
            print(f"  ✗ Не удалось доказать все условия правила")
            return None

        print(f"\n  ✓ ВСЕ условия правила доказаны!")
        print(f"    Итоговый вывод: {rule_result}")
        print(f"    Итоговые подстановки: {global_substitutions}")

        # Добавляем доказанный факт в базу знаний
        for atom in rule_result.args:
            if not any(self.__atoms_equal(atom, existing) for existing in facts.args):
                facts.args.append(atom)
                print(f"    Добавлен новый факт: {atom}")

        # Переносим правило в доказанные (с подстановками)
        proved_rule = rule.copy()
        apply_substitution(proved_rule.left.args + proved_rule.right.args, global_substitutions)
        self.knowleadge.close_rules.append(proved_rule)
        self.knowleadge.open_rules.remove(rule)

        print(f"    Правило добавлено в доказанные: {proved_rule}")

        return rule_result

    def dfs(
            self,
            left: Conjunct,
            facts: Conjunct,
            global_substitutions: dict
    ) -> bool:

        print(f"    Начинаем DFS для условий: {left.args}")

        # стек состояний: (оставшиеся подцели, подстановки)
        stack = [
            (left.args.copy(), global_substitutions.copy())
        ]

        depth = 0

        while stack:
            subgoals, subs = stack.pop()
            depth += 1

            print(f"\n    Глубина {depth}:")
            print(f"      Оставшиеся подцели: {subgoals}")
            print(f"      Текущие подстановки: {subs}")

            # если подцелей не осталось — успех
            if not subgoals:
                print(f"      ✓ Все подцели доказаны!")
                global_substitutions.update(subs)
                return True

            # берём одну подцель
            current = subgoals.pop(0)
            print(f"      Проверяем подцель: {current}")

            # 1. Пытаемся доказать фактом
            proved = False
            print(f"      Ищем среди фактов...")
            for fact in facts.args:
                s = unificate_atoms(current, fact)
                if s is not None:
                    print(f"      ✓ Найден факт: {fact}")
                    print(f"        Подстановки: {s}")

                    new_subs = subs.copy()
                    add_substitutions(new_subs, s)

                    new_subgoals = subgoals.copy()
                    apply_substitution(new_subgoals, s)

                    stack.append((new_subgoals, new_subs))
                    proved = True
                    break

            if proved:
                continue

            # 2. Пытаемся доказать правилом
            print(f"      Не найдено среди фактов, ищем подходящее правило...")
            for rule in self.knowleadge.open_rules:
                rule_copy = rule.copy()
                rule_right = rule_copy.right.args

                for r in rule_right:
                    s = unificate_atoms(r, current)
                    if s is None:
                        continue

                    print(f"      ✓ Найдено правило: {rule}")
                    print(f"        Вывод правила {r} унифицируется с подцелью {current}")
                    print(f"        Подстановки: {s}")

                    new_subs = subs.copy()
                    add_substitutions(new_subs, s)

                    left_atoms = rule_copy.left.args.copy()
                    apply_substitution(left_atoms + subgoals, s)

                    new_subgoals = left_atoms + subgoals.copy()
                    stack.append((new_subgoals, new_subs))
                    proved = True
                    break

                if proved:
                    break

            if not proved:
                print(f"      ✗ Подцель {current} не доказана")

        print(f"    ✗ DFS завершился неудачей")
        return False

    def __is_proved(self, atoms: list[Atom], goal: Atom) -> bool:
        for atom in atoms:
            if (
                    atom.isPositive != goal.isPositive or \
                    atom.name != goal.name or \
                    not self.__equal_types(atom, goal)
            ):
                continue

            if unificate_atoms(atom, goal) != None:
                return True

        return False

    def __atoms_equal(self, a1: Atom, a2: Atom) -> bool:
        """Сравнивает два атома"""
        if a1.isPositive != a2.isPositive or a1.name != a2.name:
            return False
        if len(a1.args) != len(a2.args):
            return False
        for t1, t2 in zip(a1.args, a2.args):
            if t1.type != t2.type or t1.name != t2.name:
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



# def knowleadge_prove(self, goal: Atom) -> bool:
    #     facts = self.knowleadge.data
    #     open_rules = self.knowleadge.open_rules
    #     close_rules = self.knowleadge.close_rules
    #     global_subs = {}
    #
    #     solution_flag = False
    #     no_solution_flag = False
    #
    #     if self.__is_proved(facts.args, goal):
    #         return True
    #
    #     while not solution_flag and not no_solution_flag:
    #         close_rules_count = 0
    #
    #         i = 0
    #         while i < len(open_rules):
    #             print(f"\nТекущее правило:\n  {open_rules[i]}")
    #
    #             new_fact = self.__try_to_prove(
    #                 facts=facts,
    #                 rule=open_rules[i],
    #             )
    #
    #             if new_fact:
    #                 facts.args += new_fact.args
    #                 close_rules.append(open_rules.pop(i))
    #                 close_rules_count += 1
    #
    #                 if self.__is_proved(new_fact.args, goal):
    #                     solution_flag = True
    #                     break
    #             else:
    #                 i += 1
    #
    #         if close_rules_count == 0:
    #             no_solution_flag = True
    #
    #     return solution_flag



# def __try_to_prove(
    #         self,
    #         facts: Conjunct,
    #         rule: Implication,
    #         goal: Atom,
    #         global_substitutions: dict[str]
    # ) -> dict[str] | None:
    #     rule_result = rule.right.copy()
    #     rule_input_atoms = rule.left.copy()
    #
    #     for right_atom in rule_result.args:
    #
    #         subs = unificate_atoms(right_atom, goal)
    #         if subs is None:
    #             return
    #
    #         add_substitutions(
    #             dest_substitions=global_substitutions,
    #             sourse_substitions=subs,
    #         )
    #
    #         apply_substitution(
    #             atoms_list=rule_result.args + rule_input_atoms.args,
    #             substitutions=subs,
    #         )
    #
    #     return self.dfs(rule_input_atoms, rule_result, goal, facts)





    # def __try_to_prove_rule(
    #         self,
    #         facts: Conjunct,
    #         rule: Implication,
    # ) -> Conjunct | None:
    #     rule_result = rule.right.copy()
    #     rule_input_atoms = rule.left.copy()
    #     global_substitutions = {}
    #
    #     while True:
    #         unificate_count = 0
    #
    #         for rule_input_atom in rule_input_atoms.args:
    #             for fact_atom in facts.args:
    #                 if rule_input_atom.isPositive != fact_atom.isPositive:
    #                     continue
    #
    #                 substitutions = unificate_atoms(
    #                     left=rule_input_atom,
    #                     right=fact_atom,
    #                 )
    #                 if substitutions is None:
    #                     continue
    #
    #                 rule_input_atoms.args.remove(rule_input_atom)
    #
    #                 add_substitutions(
    #                     dest_substitions=global_substitutions,
    #                     sourse_substitions=substitutions,
    #                 )
    #                 apply_substitution(
    #                     atoms_list=rule_result.args + rule_input_atoms.args,
    #                     substitutions=substitutions,
    #                 )
    #                 unificate_count += 1
    #                 break
    #
    #         if unificate_count == 0:
    #             break
    #
    #     if len(rule_input_atoms.args):
    #         print(
    #             f"\n{self.knowleadge}\n" f"\n=> ❌\n" f"\n{'-' * 64}"
    #         )
    #         return None
    #
    #     print(
    #         f"\n{self.knowleadge}\n" \
    #         f"\n=> {rule_result} с подстановкой {global_substitutions}\n" \
    #         f"\n{'-' * 64}"
    #     )
    #     return rule_result
