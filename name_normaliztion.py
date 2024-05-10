import pymatgen.core as pg


def rounding_fractions(comp_string: str) -> list[str]:
    elements = [f for i, f in enumerate(comp_string.split('$')) if i%2==0]
    fractions = [str(round(float(f.replace("_{", "").replace("}", "")), 3)) for i, f in enumerate(comp_string.split('$')) if
                 i % 2 != 0]
    final_results = [f"{i}{j}" for i, j in zip(elements, fractions)]
    return final_results


def normalize_comp_name(compName: str) -> str:
    comp = pg.Composition(compName)
    comp = pg.Composition(comp.alphabetical_formula)
    fractional_comp = comp.fractional_composition
    fract_comp_ustring = fractional_comp.to_unicode_string()
    # fractions = [round(float(f.replace("_{", "").replace("}", "")), 3) for i, f in
    #              enumerate(fract_comp_ustring.split('$')) if i % 2 != 0]
    # print(fractions)
    normalized_frac_comp = rounding_fractions(fract_comp_ustring)
    normalized_comp_name = ''.join(f for f in normalized_frac_comp)

    return normalized_comp_name


if __name__ == '__main__':
    norm_n1 = normalize_comp_name('Cr0.167Mo0.167Nb0.167Ta0.167V0.167W0.167')
    print(norm_n1)
    # norm_n2 = normalize_comp_name('NbMoTaWVCr')
