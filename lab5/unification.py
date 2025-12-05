from items import Term, Atom


def apply_substitution_to_term(term: Term, substitution: dict[str, Term]) -> Term:
    """Применяет подстановку к одному терму."""
    if term.type == "var" and term.name in substitution:
        return substitution[term.name].copy()
    return term.copy()


def compose_substitutions(
        s1: dict[str, Term],
        s2: dict[str, Term]
) -> dict[str, Term]:
    """Композиция двух подстановок s1 и s2, s2 применяется после s1."""

    result = {k: apply_substitution_to_term(v, s2) for k, v in s1.items()}

    for k, v in s2.items():
        if k not in s1:
            result[k] = v.copy()

    return result


def unificate_atoms(left: Atom, right: Atom) -> dict[str, Term] | None:
    if left.name != right.name or len(left.args) != len(right.args) or left.isPositive != right.isPositive:
        return None

    substitions = {}

    for i in range(len(left.args)):
        left_term = left.args[i]
        right_term = right.args[i]

        def unify_term(var_term: Term, other_term: Term):
            if var_term.name in substitions:
                sub_term = substitions[var_term.name]
                if sub_term.type == "var":
                    if sub_term.name == other_term.name:
                        return True


                    for k, v in substitions.items():
                        if v.type == "var" and v.name == var_term.name:
                            substitions[k] = other_term.copy()

                    substitions[var_term.name] = other_term.copy()

                elif sub_term.type == "const":
                    if other_term.type == "const" and sub_term.value == other_term.value:
                        return True
                    elif other_term.type == "var":
                        if other_term.name in substitions and substitions[other_term.name].type == "const" and \
                                substitions[other_term.name].value != sub_term.value:
                            return False

                        substitions[other_term.name] = sub_term.copy()

                    return sub_term.value == other_term.value if other_term.type == "const" else False

                else:
                    return False

            else:
                if other_term.type == "var" and var_term.name == other_term.name:
                    return True

                substitions[var_term.name] = other_term.copy()
                return True


        if left_term.type == "const" and right_term.type == "const":
            if left_term.value != right_term.value:
                return None

        elif left_term.type == "var" and right_term.type == "const":
            if not unify_term(left_term, right_term): return None

        elif left_term.type == "const" and right_term.type == "var":
            if not unify_term(right_term, left_term): return None

        elif left_term.type == "var" and right_term.type == "var":
            if left_term.name != right_term.name:
                if not unify_term(left_term, right_term): return None

    return substitions


def apply_substitution(
        atoms_list: list[Atom],
        substitutions: dict[str, Term],
) -> None:
    for atom in atoms_list:
        for term in atom.args:
            if term.type == "var" and term.name in substitutions:
                substitution_term = substitutions[term.name]

                term.name = substitution_term.name
                term.type = substitution_term.type
                term.value = substitution_term.value if substitution_term.type == "const" else None